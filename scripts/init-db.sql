-- Initialize A11yomatic database

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE a11yomatic TO a11yomatic;

-- Note: Tables will be created automatically by SQLAlchemy
