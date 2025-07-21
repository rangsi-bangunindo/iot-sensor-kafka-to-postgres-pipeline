import json
import logging
import psycopg2
from kafka import KafkaConsumer, KafkaProducer
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Logging config
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")
KAFKA_DEAD_LETTER_TOPIC = os.getenv("KAFKA_DEAD_LETTER_TOPIC")

# PostgreSQL configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Table names
METADATA_TABLE = os.getenv("METADATA_TABLE")
TARGET_TABLE = os.getenv("TARGET_TABLE")

# Connect to PostgreSQL
def get_pg_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

# Fetch metadata and cache in memory (assumes small table)
def load_device_metadata(conn):
    with conn.cursor() as cur:
        cur.execute(f"SELECT device_id, device_name, location, manufacturer FROM {METADATA_TABLE}")
        metadata = {
            row[0]: {
                "device_name": row[1],
                "location": row[2],
                "manufacturer": row[3]
            }
            for row in cur.fetchall()
        }
    return metadata

# Enrich sensor data using device metadata
def enrich_sensor_data(sensor_data, metadata_dict):
    device_id = sensor_data.get("device_id")
    enrichment = metadata_dict.get(device_id)

    if enrichment is None:
        enrichment = {
            "device_name": "Perangkat Tidak Dikenal",
            "location": "Lokasi Tidak Diketahui",
            "manufacturer": "Tidak Diketahui"
        }

    enriched_data = {
        **sensor_data,
        **enrichment
    }
    return enriched_data

# Save enriched sensor data
def insert_sensor_data(conn, record):
    with conn.cursor() as cur:
        cur.execute(
            f"""
            INSERT INTO {TARGET_TABLE} (
                device_id, device_name, temperature, humidity,
                timestamp, location, manufacturer
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                record["device_id"],
                record["device_name"],
                record["temperature"],
                record["humidity"],
                record["timestamp"],
                record["location"],
                record["manufacturer"]
            )
        )
    conn.commit()

def consume_and_process():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_CONSUMER_GROUP,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset='earliest',
        enable_auto_commit=False
    )

    dead_letter_producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda m: json.dumps(m).encode("utf-8")
    )

    MAX_RETRIES = 3

    try:
        pg_conn = get_pg_connection()
        device_metadata = load_device_metadata(pg_conn)
        logging.info("Loaded device metadata.")

        for message in consumer:
            data = message.value
            logging.info(f"Consumed: {data}")

            success = False
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    data = enrich_sensor_data(data, device_metadata)

                    insert_sensor_data(pg_conn, data)
                    consumer.commit()
                    logging.info(f"Inserted and committed for device {data['device_id']}")
                    success = True
                    break

                except Exception as e:
                    logging.warning(f"Attempt {attempt} failed: {e}")
                    if attempt < MAX_RETRIES:
                        continue
                    else:
                        logging.error("Max retries exceeded. Sending to dead-letter topic.")
                        try:
                            if KAFKA_DEAD_LETTER_TOPIC:
                                dead_letter_producer.send(KAFKA_DEAD_LETTER_TOPIC, value=data)
                                dead_letter_producer.flush()
                                logging.info("Sent to dead-letter topic.")
                            else:
                                logging.critical("Dead-letter topic not set. Message dropped.")
                        except Exception as dlq_error:
                            logging.critical(f"Failed to send to dead-letter topic: {dlq_error}")

            if not success:
                logging.error(f"Data permanently failed: {data}")

    except Exception as e:
        logging.error(f"Fatal error in consumer: {e}")
    finally:
        consumer.close()
        dead_letter_producer.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    logging.info("Starting Kafka consumer...")
    consume_and_process()
