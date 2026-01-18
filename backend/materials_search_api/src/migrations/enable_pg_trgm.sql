-- Enable pg_trgm extension for fuzzy/typo-tolerant search
-- Run this once on your PostgreSQL database

CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create GIN index on materials.name for fast trigram similarity lookups
CREATE INDEX IF NOT EXISTS ix_materials_name_trgm ON materials USING GIN (name gin_trgm_ops);

-- Create GIN index on materials.description for fuzzy search
CREATE INDEX IF NOT EXISTS ix_materials_description_trgm ON materials USING GIN (description gin_trgm_ops);

-- Verify extension is installed
SELECT * FROM pg_extension WHERE extname = 'pg_trgm';
