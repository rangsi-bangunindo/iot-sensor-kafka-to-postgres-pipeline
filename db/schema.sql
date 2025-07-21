-- This file creates the necessary tables for sensor data ingestion and enrichment
-- Drop tables if they already exist (for development/testing purposes)
DROP TABLE IF EXISTS rangsi_iot_sensor_readings;
DROP TABLE IF EXISTS rangsi_device_metadata;
-- Master metadata table for device information
CREATE TABLE rangsi_device_metadata (
    device_id VARCHAR PRIMARY KEY,
    device_name VARCHAR NOT NULL,
    location VARCHAR NOT NULL,
    manufacturer VARCHAR NOT NULL
);
-- Enriched sensor readings table
CREATE TABLE rangsi_iot_sensor_readings (
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
-- Dummy metadata seed for devices
INSERT INTO rangsi_device_metadata (device_id, device_name, location, manufacturer)
VALUES (
        'device_1',
        'Sensor Alpha',
        'Jakarta',
        'PT Sensorindo'
    ),
    (
        'device_2',
        'Sensor Beta',
        'Bandung',
        'PT Sensorindo'
    ),
    (
        'device_3',
        'Sensor Gamma',
        'Surabaya',
        'PT Teknologi Nusantara'
    ),
    (
        'device_4',
        'Sensor Delta',
        'Yogyakarta',
        'PT Inovasi Digital'
    ),
    (
        'device_5',
        'Sensor Epsilon',
        'Medan',
        'PT Cerdas Sensorik'
    );