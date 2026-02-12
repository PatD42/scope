-- SQL Schema Template (PostgreSQL syntax)
-- Copy relevant sections to schema.sql and migrations/

-- =============================================================================
-- TABLE: {table_name}
-- Epic: SCOPE-XXX
-- Description: {description}
-- =============================================================================

CREATE TABLE IF NOT EXISTS {table_name} (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign keys
    -- related_id UUID NOT NULL REFERENCES related_table(id) ON DELETE CASCADE,

    -- Domain fields
    -- name VARCHAR(255) NOT NULL,
    -- status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'pending')),
    -- data JSONB,

    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_{table_name}_created_at ON {table_name}(created_at);
-- CREATE INDEX IF NOT EXISTS idx_{table_name}_status ON {table_name}(status);
-- CREATE INDEX IF NOT EXISTS idx_{table_name}_related_id ON {table_name}(related_id);

-- For JSONB fields (PostgreSQL)
-- CREATE INDEX IF NOT EXISTS idx_{table_name}_data ON {table_name} USING GIN (data);

-- Unique constraints
-- CREATE UNIQUE INDEX IF NOT EXISTS idx_{table_name}_unique_field ON {table_name}(field);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_{table_name}_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_{table_name}_updated_at
    BEFORE UPDATE ON {table_name}
    FOR EACH ROW
    EXECUTE FUNCTION update_{table_name}_updated_at();

-- =============================================================================
-- CHANGELOG
-- =============================================================================
-- | Epic | Date | Changes |
-- |------|------|---------|
-- | SCOPE-XXX | YYYY-MM-DD | Initial creation |
