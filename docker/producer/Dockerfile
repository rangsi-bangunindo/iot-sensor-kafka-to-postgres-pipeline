# Use an official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy only requirement definitions first (optional optimization)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Mount source in dev via volumes: - .:/app
COPY docker/producer/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
