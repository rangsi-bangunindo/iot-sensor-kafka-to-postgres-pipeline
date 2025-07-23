# IoT Sensor: Kafka to PostgreSQL Pipeline

A Python-based data pipeline that simulates IoT sensor data, streams it through Apache Kafka, and stores enriched readings in a PostgreSQL database. Designed for local development and modular integration.

---

## Features

- Simulates IoT temperature and humidity readings
- Streams data to Kafka topic
- Enriches data with device metadata
- Stores results in PostgreSQL
- Supports Kafka consumer retry with exponential backoff
- Uses `.env` for configuration
- Compatible with Windows Command Prompt (also works on Unix with adjusted paths)

---

## Project Structure

```text
iot-sensor-kafka-to-postgres-pipeline/
├── kafka_client/               # Kafka-specific logic & handlers
│   ├── __init__.py
│   ├── connection.py
│   └── consumer.py             # Core consumer logic (used by entry point)
├── postgres_client/            # All DB-related logic
│   ├── __init__.py
│   ├── connection.py           # Database connection logic
│   └── io.py                   # Read/write functions (load metadata, insert records)
├── scripts/                    # Entry points (CLI / main execution)
│   ├── __init__.py
│   ├── consumer.py             # Runs Kafka consumer using kafka_client.processor
│   └── producer.py             # Optional: sends simulated sensor data
├── utils/                      # Shared helper modules
│   ├── __init__.py
│   └── enrichment.py           # Sensor enrichment logic
├── config/                     # Configuration handling
│   └── config.py               # Loads env vars from .env
├── db/                         # SQL schemas or migration scripts
│   └── schema.sql
├── docker-compose.yml          # Placeholder for future use
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md
```

---

## Environment Configuration

Create a `.env` file based on the following structure:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=<your_database_name>
POSTGRES_USER=<your_username>
POSTGRES_PASSWORD=<your_password>

KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=iot_sensor_data
KAFKA_CONSUMER_GROUP=iot_consumer_group
KAFKA_DEAD_LETTER_TOPIC=iot_dead_letter

METADATA_TABLE=device_metadata
TARGET_TABLE=iot_sensor_readings

PRODUCE_INTERVAL_SECONDS=1
```

> **Note**: These values are intended for local testing. Update them if connecting to services via Docker Compose, remote hosts, or cloud platforms.

---

## Database Schema

Defined in `db/schema.sql`:

```sql
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

---

## Setup Instructions

### 1. Create and Activate Virtual Environment

```powershell
python -m venv .venv
.venv\Scripts\activate   # On macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL

Ensure PostgreSQL is running and accessible with credentials from `.env`. Run the schema:

```pgsql
psql -h localhost -U <your_username> -d <your_database_name> -f db/schema.sql
```

### 3. Start Kafka

Make sure Kafka is up and topics `iot_sensor_data` and `iot_dead_letter` are created.

### 4. Run the Producer

Simulates and sends data:

```powershell
python scripts/producer.py
```

### 5. Run the Consumer

Consumes, enriches, and writes to DB:

```powershell
python -m scripts.consumer
```

Avoid using `python scripts/consumer.py` directly to ensure module imports work correctly.

---

## Example Data Flow

This section illustrates how raw sensor data flows through the pipeline, from ingestion in Kafka to enrichment and storage in PostgreSQL.

### 1. Kafka Input (`iot_sensor_data`)

Sample messages sent by the Kafka producer:

```json
{"device_id": "device_3", "temperature": 21.24, "humidity": 39.27, "timestamp": "2025-07-21 18:22:50"}
{"device_id": "device_5", "temperature": 25.61, "humidity": 33.3,  "timestamp": "2025-07-21 18:22:53"}
```

### 2. Metadata Table (`device_metadata`)

Reference data stored in PostgreSQL to enrich incoming sensor data:

| device_id | device_name    | location | manufacturer           |
| --------- | -------------- | -------- | ---------------------- |
| device_3  | Sensor Gamma   | Surabaya | PT Teknologi Nusantara |
| device_5  | Sensor Epsilon | Medan    | PT Cerdas Sensorik     |

### 3. Enriched Output (`iot_sensor_readings`)

Final enriched records stored in PostgreSQL after processing:

| id  | device_id | device_name    | temperature | humidity | timestamp           | location | manufacturer           | ingestion_time          |
| --- | --------- | -------------- | ----------- | -------- | ------------------- | -------- | ---------------------- | ----------------------- |
| 1   | device_3  | Sensor Gamma   | 21.24       | 39.27    | 2025-07-21 18:22:50 | Surabaya | PT Teknologi Nusantara | 2025-07-21 20:44:13.601 |
| 2   | device_5  | Sensor Epsilon | 25.61       | 33.30    | 2025-07-21 18:22:53 | Medan    | PT Cerdas Sensorik     | 2025-07-21 20:44:21.106 |

---

## Testing and Verification

- Keep producer and consumer running in separate terminals
- Check latest inserted data:

```sql
SELECT * FROM iot_sensor_readings ORDER BY ingestion_time DESC LIMIT 5;
```

- Simulate Kafka disconnection to test retry logic

---

## Logging

Logging is implemented using the `logging` module. Consumer logs retry attempts and failures at `INFO` or `WARNING` level. Adjust the logging level in `scripts/consumer.py` for debugging or production.

---

## Sample Logs

The following examples illustrate runtime outputs from the producer and consumer. These logs help verify successful connections, message flow, and metadata enrichment.

### Producer Output

```powershell
[2025-07-22 09:06:25,997] INFO - Connected to Kafka at ***.***.***.***:9092
[2025-07-22 09:06:25,997] INFO - Starting IoT sensor data producer...
[2025-07-22 09:06:26,728] INFO - Produced: {'device_id': 'device_3', 'temperature': 27.69, 'humidity': 64.9, 'timestamp': '2025-07-22 09:06:25'}
```

### Consumer Output

```powershell
[2025-07-22 09:06:26,733] INFO - Starting Kafka consumer...
[2025-07-22 09:06:27,528] INFO - KafkaConsumer connected successfully on attempt 1.
[2025-07-22 09:06:35,148] INFO - Consumed: {'device_id': 'device_3', 'temperature': 27.69, 'humidity': 64.9, 'timestamp': '2025-07-22 09:06:25'}
[2025-07-22 09:06:35,746] INFO - Inserted and committed for device device_3
```

### Kafka Group Join (During Rebalance)

```powershell
[2025-07-22 09:06:30,822] INFO - Failed to join group iot_consumer_group: NodeNotReadyError: coordinator-0
[2025-07-22 09:06:31,313] INFO - Failed to join group iot_consumer_group: [Error 79] MemberIdRequiredError
[2025-07-22 09:06:34,503] INFO - Successfully joined group iot_consumer_group
```

These samples are illustrative. Actual log contents may vary based on configuration, environment, or runtime conditions.
