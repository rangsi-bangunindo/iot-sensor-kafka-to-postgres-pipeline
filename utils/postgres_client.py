import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Table names
METADATA_TABLE = os.getenv("METADATA_TABLE")
TARGET_TABLE = os.getenv("TARGET_TABLE")

# Connect to PostgreSQL
def get_pg_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

# Fetch metadata and cache in memory (assumes small table)
def load_device_metadata(conn):
    with conn.cursor() as cur:
        cur.execute(f"SELECT device_id, device_name, location, manufacturer FROM {METADATA_TABLE}")
        return {
            row[0]: {
                "device_name": row[1],
                "location": row[2],
                "manufacturer": row[3]
            }
            for row in cur.fetchall()
        }

# Save enriched sensor data
def insert_sensor_data(conn, record):
    with conn.cursor() as cur:
        cur.execute(
            f"""
            INSERT INTO {TARGET_TABLE} (
                device_id, device_name, temperature, humidity,
                timestamp, location, manufacturer
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                record["device_id"],
                record["device_name"],
                record["temperature"],
                record["humidity"],
                record["timestamp"],
                record["location"],
                record["manufacturer"]
            )
        )
    conn.commit()
