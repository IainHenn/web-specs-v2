CREATE TABLE IF NOT EXISTS metrics (
    id BIGSERIAL PRIMARY KEY,
    agent_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    timestamp BIGINT NOT NULL,
    key TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics (timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_agent_metric ON metrics (agent_id, metric_name);
