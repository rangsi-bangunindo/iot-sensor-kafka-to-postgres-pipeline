# Use an official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy only requirement definitions first (optional optimization)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

ENV PYTHONPATH="/app"

# Default command
CMD ["python", "scripts/consumer.py"]
