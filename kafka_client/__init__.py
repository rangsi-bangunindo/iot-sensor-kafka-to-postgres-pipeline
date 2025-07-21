import time
import logging
import json
import random
from kafka import KafkaConsumer
from kafka.errors import KafkaError

def get_kafka_consumer(topic, bootstrap_servers, group_id, max_retries=5, base_delay=1.0):
    """Creates a KafkaConsumer with retries using exponential backoff and jitter."""

    for attempt in range(1, max_retries + 1):
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset='earliest',
                enable_auto_commit=False
            )
            logging.info(f"KafkaConsumer connected successfully on attempt {attempt}.")
            return consumer

        except KafkaError as e:
            delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
            logging.warning(f"KafkaConsumer connection attempt {attempt} failed: {e}")
            if attempt < max_retries:
                logging.info(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                logging.critical("Exceeded maximum retries to create KafkaConsumer.")
                raise
