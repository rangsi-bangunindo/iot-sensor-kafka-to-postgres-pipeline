import logging
from kafka_client.consumer import consume_and_process
from config.config import get_config

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')
    logging.info("Starting Kafka consumer...")

    config = get_config()
    consume_and_process(config)
