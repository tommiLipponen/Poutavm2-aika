-- PostgreSQL schema for MQTT chat messages
-- Run this as lempuser to create the mqtt_messages table

-- Drop table if exists (for clean reinstall)
-- DROP TABLE IF EXISTS mqtt_messages;

-- Create mqtt_messages table
CREATE TABLE IF NOT EXISTS mqtt_messages (
    id SERIAL PRIMARY KEY,
    nickname VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    client_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_mqtt_created ON mqtt_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_mqtt_nickname ON mqtt_messages(nickname);

-- Grant permissions (if needed)
-- GRANT ALL PRIVILEGES ON TABLE mqtt_messages TO lempuser;
-- GRANT USAGE, SELECT ON SEQUENCE mqtt_messages_id_seq TO lempuser;

-- Verify table creation
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'mqtt_messages'
ORDER BY ordinal_position;
