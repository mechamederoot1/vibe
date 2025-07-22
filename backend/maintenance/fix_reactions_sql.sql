-- Fix reactions table - Add missing updated_at column
-- Run this SQL directly in your database

-- Check if column exists first
SHOW COLUMNS FROM reactions LIKE 'updated_at';

-- Add the missing column if it doesn't exist
ALTER TABLE reactions 
ADD COLUMN IF NOT EXISTS updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Verify the fix
DESCRIBE reactions;

-- Show all columns to confirm
SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'reactions' 
AND TABLE_SCHEMA = DATABASE();
