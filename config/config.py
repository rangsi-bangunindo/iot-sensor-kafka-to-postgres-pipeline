import os
from dotenv import load_dotenv

load_dotenv()

def get_config():
    return {
        # Kafka settings
        "KAFKA_BOOTSTRAP_SERVERS": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        "KAFKA_CONSUMER_GROUP": os.getenv("KAFKA_CONSUMER_GROUP"),
        "KAFKA_TOPIC": os.getenv("KAFKA_TOPIC"),
        "KAFKA_DEAD_LETTER_TOPIC": os.getenv("KAFKA_DEAD_LETTER_TOPIC"),

        # PostgreSQL settings
        "POSTGRES_HOST": os.getenv("POSTGRES_HOST"),
        "POSTGRES_PORT": os.getenv("POSTGRES_PORT"),
        "POSTGRES_DB": os.getenv("POSTGRES_DB"),
        "POSTGRES_USER": os.getenv("POSTGRES_USER"),
        "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD"),

        # Table names
        "METADATA_TABLE": os.getenv("METADATA_TABLE"),
        "TARGET_TABLE": os.getenv("TARGET_TABLE")
    }
