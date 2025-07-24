import json
import time
import random
import logging
from kafka import KafkaProducer

DEVICE_IDS = [f"device_{i}" for i in range(1, 6)]

def generate_sensor_data():
    return {
        "device_id": random.choice(DEVICE_IDS),
        "temperature": round(random.uniform(20.0, 35.0), 2),
        "humidity": round(random.uniform(30.0, 70.0), 2),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

def produce_sensor_data(config):
    try:
        producer = KafkaProducer(
            bootstrap_servers=config["KAFKA_BOOTSTRAP_SERVERS"],
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        logging.info(f"Connected to Kafka at {config['KAFKA_BOOTSTRAP_SERVERS']}")
    except Exception as e:
        logging.error(f"Failed to connect to Kafka: {e}")
        exit(1)

    interval = config["PRODUCE_INTERVAL_SECONDS"]

    while True:
        data = generate_sensor_data()
        try:
            producer.send(config["KAFKA_TOPIC"], value=data)
            logging.info(f"Produced: {data}")
        except Exception as e:
            logging.error(f"Failed to produce message: {e}")
        time.sleep(interval)
