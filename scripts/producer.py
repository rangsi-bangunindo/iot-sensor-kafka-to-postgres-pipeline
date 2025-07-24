import logging
from kafka_client.producer import produce_sensor_data
from config.config import get_config

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')
    logging.info("Starting IoT sensor data producer...")

    config = get_config()
    produce_sensor_data(config)
