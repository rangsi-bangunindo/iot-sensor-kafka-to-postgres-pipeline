import json
import time
import random
import logging
from kafka import KafkaProducer
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")
PRODUCE_INTERVAL = int(os.getenv("PRODUCE_INTERVAL_SECONDS", 1))

# Initialize Kafka producer
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    logging.info(f"Connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
except Exception as e:
    logging.error(f"Failed to connect to Kafka: {e}")
    exit(1)

# Simulate IoT sensor data
DEVICE_IDS = [f"device_{i}" for i in range(1, 6)]

def generate_sensor_data():
    return {
        "device_id": random.choice(DEVICE_IDS),
        "temperature": round(random.uniform(20.0, 35.0), 2),
        "humidity": round(random.uniform(30.0, 70.0), 2),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

def produce_data():
    while True:
        data = generate_sensor_data()
        try:
            producer.send(KAFKA_TOPIC, value=data)
            logging.info(f"Produced: {data}")
        except Exception as e:
            logging.error(f"Failed to produce message: {e}")
        time.sleep(PRODUCE_INTERVAL)

if __name__ == "__main__":
    logging.info("Starting IoT sensor data producer...")
    produce_data()
