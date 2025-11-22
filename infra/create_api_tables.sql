-- Create tables for weather and solar wind data
-- Run as: psql -U lempuser -d lempdb < infra/create_api_tables.sql

-- Weather data from OpenWeatherMap
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    temperature NUMERIC(5,2),  -- Celsius
    humidity NUMERIC(5,2),     -- Percentage
    pressure NUMERIC(7,2),     -- hPa
    wind_speed NUMERIC(5,2),   -- m/s
    description TEXT
);

-- Solar wind data from NOAA
CREATE TABLE IF NOT EXISTS solar_wind_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    speed NUMERIC(7,2),        -- km/s
    density NUMERIC(7,4),      -- particles/cm³
    bt NUMERIC(7,2)            -- Total magnetic field (nT)
);

-- Create indexes for efficient time-based queries
CREATE INDEX IF NOT EXISTS idx_weather_timestamp ON weather_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_solar_timestamp ON solar_wind_data(timestamp DESC);

-- Grant permissions to timeapp user (adjust if different)
GRANT SELECT, INSERT ON weather_data TO timeapp;
GRANT SELECT, INSERT ON solar_wind_data TO timeapp;
GRANT USAGE, SELECT ON SEQUENCE weather_data_id_seq TO timeapp;
GRANT USAGE, SELECT ON SEQUENCE solar_wind_data_id_seq TO timeapp;

-- Display table info
\dt weather_data
\dt solar_wind_data
