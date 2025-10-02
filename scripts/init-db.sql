-- Database initialization script for A11yomatic

-- Create database if not exists (handled by Docker environment variables)

-- Create extension for UUID support
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE a11yomatic TO a11yomatic;

-- Tables will be created by SQLAlchemy's create_all()
-- This script ensures the database and extensions are ready
