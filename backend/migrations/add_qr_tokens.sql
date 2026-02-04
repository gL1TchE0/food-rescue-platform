-- Migration: Add QR Verification Tokens to Tasks
-- Description: Adds pickup_token and delivery_token columns to tasks table for QR code verification
-- Date: 2026-02-04

-- Add pickup_token column
ALTER TABLE tasks 
ADD COLUMN pickup_token VARCHAR(10) UNIQUE NOT NULL DEFAULT upper(encode(gen_random_bytes(3), 'hex'));

-- Add delivery_token column
ALTER TABLE tasks 
ADD COLUMN delivery_token VARCHAR(10) UNIQUE NOT NULL DEFAULT upper(encode(gen_random_bytes(3), 'hex'));

-- Create indexes for fast token lookup
CREATE INDEX idx_tasks_pickup_token ON tasks(pickup_token);
CREATE INDEX idx_tasks_delivery_token ON tasks(delivery_token);

-- Update existing tasks with random tokens (if any exist)
UPDATE tasks 
SET 
    pickup_token = upper(encode(gen_random_bytes(3), 'hex')),
    delivery_token = upper(encode(gen_random_bytes(3), 'hex'))
WHERE pickup_token IS NULL OR delivery_token IS NULL;

-- Add comments
COMMENT ON COLUMN tasks.pickup_token IS 'QR token for verifying food pickup from donor';
COMMENT ON COLUMN tasks.delivery_token IS 'QR token for verifying food delivery to NGO';
