#!/bin/sh
set -e

echo "Starting producer service..."

exec python scripts/producer.py
