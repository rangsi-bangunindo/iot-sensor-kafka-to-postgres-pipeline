Project Structure

```text
iot-sensor-kafka-to-postgres-pipeline/
├── kafka_client/
│   └── __init__.py              # Retry-wrapped KafkaConsumer instantiation
├── scripts/
│   ├── producer.py              # Kafka Producer: sends IoT sensor data
│   └── consumer.py              # Kafka Consumer: enriches and writes to PostgreSQL
├── db/
│   └── schema.sql               # Contains CREATE TABLE + INSERTs for device_metadata
├── .env                         # (gitignored) Actual credentials and connection configs
├── .env.example                 # Template for required environment variables
├── requirements.txt             # Dependencies (kafka-python, psycopg2, etc.)
├── docker-compose.yml           # Optional local Kafka/Postgres setup
├── .gitignore                   # Ignore .env and Python cache/files
└── README.md                    # Setup and run instructions
```
