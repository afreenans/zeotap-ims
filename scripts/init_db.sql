-- Initialize database schema

CREATE TABLE IF NOT EXISTS work_items (
    id SERIAL PRIMARY KEY,
    component_id VARCHAR(100) NOT NULL,
    severity VARCHAR(10) NOT NULL,
    state VARCHAR(20) DEFAULT 'OPEN',
    signal_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_work_items_component ON work_items(component_id);
CREATE INDEX idx_work_items_state ON work_items(state);
CREATE INDEX idx_work_items_created ON work_items(created_at DESC);

CREATE TABLE IF NOT EXISTS rca_records (
    id SERIAL PRIMARY KEY,
    work_item_id INTEGER REFERENCES work_items(id) ON DELETE CASCADE,
    root_cause_category VARCHAR(100) NOT NULL,
    fix_applied TEXT NOT NULL,
    prevention_steps TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    mttr_seconds INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rca_work_item ON rca_records(work_item_id);
