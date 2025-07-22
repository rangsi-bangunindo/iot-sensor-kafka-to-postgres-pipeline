import os

# Table names from environment
METADATA_TABLE = os.getenv("METADATA_TABLE")
TARGET_TABLE = os.getenv("TARGET_TABLE")

# Fetch metadata and cache in memory (assumes small table)
def load_device_metadata(conn):
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT device_id, device_name, location, manufacturer
            FROM {METADATA_TABLE}
            """
        )
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
