import json
import logging
from kafka import KafkaProducer
from kafka_client import get_kafka_consumer
from postgres_client.connection import get_pg_connection
from postgres_client.io import load_device_metadata, insert_sensor_data
from utils.enrichment import enrich_sensor_data

def consume_and_process(config):
    consumer = get_kafka_consumer(
        topic=config["KAFKA_TOPIC"],
        bootstrap_servers=config["KAFKA_BOOTSTRAP_SERVERS"],
        group_id=config["KAFKA_CONSUMER_GROUP"]
    )

    dead_letter_producer = KafkaProducer(
        bootstrap_servers=config["KAFKA_BOOTSTRAP_SERVERS"],
        value_serializer=lambda m: json.dumps(m).encode("utf-8")
    )

    MAX_RETRIES = 3

    try:
        pg_conn = get_pg_connection(config)
        device_metadata = load_device_metadata(pg_conn, config)
        logging.info("Loaded device metadata.")

        for message in consumer:
            data = message.value
            logging.info(f"Consumed: {data}")

            success = False
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    data = enrich_sensor_data(data, device_metadata)
                    insert_sensor_data(pg_conn, data, config)
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
                            if config["KAFKA_DEAD_LETTER_TOPIC"]:
                                dead_letter_producer.send(config["KAFKA_DEAD_LETTER_TOPIC"], value=data)
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
