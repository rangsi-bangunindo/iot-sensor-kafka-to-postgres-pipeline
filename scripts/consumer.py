import json
import logging
import psycopg2
from kafka import KafkaProducer
from dotenv import load_dotenv
from kafka_client import get_kafka_consumer
from postgres_client import get_pg_connection, load_device_metadata, insert_sensor_data
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

def consume_and_process():
    consumer = get_kafka_consumer(
        topic=KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_CONSUMER_GROUP
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
