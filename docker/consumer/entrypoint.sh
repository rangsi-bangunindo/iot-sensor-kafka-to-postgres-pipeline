#!/bin/sh
set -e

echo "Starting consumer service..."

# Optional: wait for Kafka and Postgres to be available
# Consider using wait-for-it or netcat-based checks if needed

exec python scripts/consumer.py
