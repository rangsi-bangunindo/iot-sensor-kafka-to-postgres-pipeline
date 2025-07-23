def load_device_metadata(conn, config):
    table = config["METADATA_TABLE"]
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT device_id, device_name, location, manufacturer
            FROM {table}
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

def insert_sensor_data(conn, record, config):
    table = config["TARGET_TABLE"]
    with conn.cursor() as cur:
        cur.execute(
            f"""
            INSERT INTO {table} (
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
