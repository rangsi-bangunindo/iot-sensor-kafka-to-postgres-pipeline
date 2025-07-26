# Use an official Python image as base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Set PYTHONPATH before installing dependencies
ENV PYTHONPATH="/app"

# Copy dependencies definition file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full source code into the image
COPY . .

# Set default command (can be overridden in docker-compose)
CMD ["python", "scripts/producer.py"]
