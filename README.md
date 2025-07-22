# IoT Sensor Kafka to PostgreSQL Pipeline

A Python-based data pipeline that simulates IoT sensor data, streams it through Apache Kafka, and stores enriched readings in a PostgreSQL database. Designed for local development on Windows and supports modular development for future containerization.

## Features

- Simulates IoT temperature and humidity readings
- Streams data to Kafka topic
- Enriches data with device metadata
- Stores results in PostgreSQL
- Supports Kafka consumer retry with exponential backoff
- Uses `.env` for configuration
- Compatible with Windows Command Prompt

## Project Structure

```
iot-sensor-kafka-to-postgres-pipeline/
├── kafka_client/
│   └── __init__.py              # KafkaConsumer with retry logic
├── scripts/
│   ├── __init__.py              # Optional package marker
│   ├── producer.py              # Sends sensor data to Kafka
│   └── consumer.py              # Reads, enriches, inserts to DB
├── db/
│   └── schema.sql               # Table definitions
├── .env                         # Local config (excluded from Git)
├── .env.example                 # Template for environment variables
├── requirements.txt             # Python dependencies
├── docker-compose.yml           # Placeholder for future use
├── .gitignore                   # Ignore rules
└── README.md                    # Project documentation
```

## Environment Configuration

Create a `.env` file based on the following structure:

```
# PostgreSQL Configuration
POSTGRES_HOST=<your_postgres_host_or_container_name>
POSTGRES_PORT=5432
POSTGRES_DB=<your_postgres_db>
POSTGRES_USER=<your_postgres_user>
POSTGRES_PASSWORD=<your_postgres_password>

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=<your_kafka_bootstrap_servers>
KAFKA_TOPIC=<your_iot_sensor_data>
KAFKA_CONSUMER_GROUP=<your_iot_consumer_group>
KAFKA_DEAD_LETTER_TOPIC=<your_iot_dead_letter>

# Other Settings
PRODUCE_INTERVAL_SECONDS=1
```

## Database Schema

Defined in `db/schema.sql`:

```
-- Master metadata table for device information
CREATE TABLE device_metadata (
    device_id VARCHAR PRIMARY KEY,
    device_name VARCHAR NOT NULL,
    location VARCHAR NOT NULL,
    manufacturer VARCHAR NOT NULL
);

-- Enriched sensor readings table
CREATE TABLE iot_sensor_readings (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR NOT NULL,
    device_name VARCHAR NOT NULL,
    temperature FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    location VARCHAR NOT NULL,
    manufacturer VARCHAR NOT NULL,
    ingestion_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Setup Instructions

### 1. Create and Activate Virtual Environment

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL

Ensure PostgreSQL is running and accessible with credentials from `.env`. Run the schema:

```
psql -h <your_postgres_host> -U <your_postgres_user> -d <your_postgres_db> -f db/schema.sql
```

### 3. Start Kafka and Zookeeper

Make sure Kafka is up and topics `sensor_data` and `dead_letter_topic` are created.

### 4. Run the Producer

Simulates and sends data:

```
python scripts\producer.py
```

### 5. Run the Consumer

Consumes, enriches, and writes to DB:

```
python -m scripts.consumer
```

Avoid using `python scripts\consumer.py` directly to ensure module imports work correctly.

## Example Enriched Output

```
{
  "device_id": "device-01",
  "device_name": "Temperature Sensor A",
  "temperature": 26.5,
  "humidity": 63.2,
  "timestamp": "2025-07-20T10:30:45",
  "location": "Warehouse A",
  "manufacturer": "SensorCorp",
  "ingestion_time": "2025-07-20T10:30:47"
}
```

## Testing and Verification

- Keep producer and consumer running in separate terminals
- Check latest inserted data:

```
SELECT * FROM iot_sensor_readings ORDER BY ingestion_time DESC LIMIT 5;
```

- Simulate Kafka disconnection to test retry logic

## Logging

Logging is implemented using the `logging` module. Consumer logs retry attempts and failures at `INFO` or `WARNING` level. Adjust the logging level in `scripts/consumer.py` for debugging or production.

```

Let me know if you want to include things like Kafka topic creation commands, docker-compose instructions later, or auto-ingestion enhancements.
```
