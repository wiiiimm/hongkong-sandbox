CREATE SCHEMA IF NOT EXISTS astra_modelling;
CREATE TABLE IF NOT EXISTS astra_modelling.schema_versions (
 version integer PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE IF NOT EXISTS astra_modelling.jobs (
 id text PRIMARY KEY,
 batch text NOT NULL,
 stage text NOT NULL,
 payload jsonb NOT NULL,
 status text NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','running','complete','failed')),
 attempts integer NOT NULL DEFAULT 0,
 max_attempts integer NOT NULL DEFAULT 3 CHECK(max_attempts BETWEEN 1 AND 10),
 owner text,
 token uuid,
 lease_until timestamptz,
 ready_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 result jsonb,
 error text,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE INDEX IF NOT EXISTS shared_jobs_claim ON astra_modelling.jobs(batch,status,ready_at,id);
INSERT INTO astra_modelling.schema_versions(version) VALUES(1) ON CONFLICT DO NOTHING;
