CREATE TABLE IF NOT EXISTS astra_modelling.city_audit_runs (
 run_id text PRIMARY KEY, plan_sha text NOT NULL, pipeline_sha text NOT NULL,
 expected_count integer NOT NULL, tile_count integer NOT NULL,
 labels text[] NOT NULL, created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE IF NOT EXISTS astra_modelling.city_audit_members (
 run_id text NOT NULL REFERENCES astra_modelling.city_audit_runs(run_id),
 uid text NOT NULL, cache_key text NOT NULL, chunk_id integer NOT NULL,
 PRIMARY KEY(run_id,uid)
);
CREATE INDEX IF NOT EXISTS city_audit_members_chunk ON astra_modelling.city_audit_members(run_id,chunk_id);
CREATE TABLE IF NOT EXISTS astra_modelling.city_audit_cache (
 cache_key text PRIMARY KEY, uid text NOT NULL, source_sha text NOT NULL,
 model_sha text NOT NULL, pipeline_sha text NOT NULL, terrain_sha text NOT NULL,
 result jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE INDEX IF NOT EXISTS city_audit_cache_uid ON astra_modelling.city_audit_cache(uid);
