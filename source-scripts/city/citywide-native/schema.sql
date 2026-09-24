CREATE TABLE IF NOT EXISTS astra_modelling.native_stage_inputs (
 cache_key text PRIMARY KEY, sheet text NOT NULL, stage text NOT NULL,
 source_sha text NOT NULL, pipeline_sha text NOT NULL, footprint_sha text NOT NULL,
 terrain_sha text, input_json jsonb NOT NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE IF NOT EXISTS astra_modelling.native_stage_results (
 cache_key text PRIMARY KEY REFERENCES astra_modelling.native_stage_inputs(cache_key),
 result_sha text NOT NULL, result jsonb NOT NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE IF NOT EXISTS astra_modelling.native_stage_runs (
 run_id text PRIMARY KEY, expected_count integer NOT NULL, labels text[] NOT NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE IF NOT EXISTS astra_modelling.native_stage_members (
 run_id text NOT NULL REFERENCES astra_modelling.native_stage_runs(run_id),
 cache_key text NOT NULL REFERENCES astra_modelling.native_stage_inputs(cache_key),
 job_id text NOT NULL, PRIMARY KEY(run_id,cache_key)
);
CREATE INDEX IF NOT EXISTS native_stage_members_job ON astra_modelling.native_stage_members(job_id);
CREATE INDEX IF NOT EXISTS native_stage_inputs_sheet ON astra_modelling.native_stage_inputs(sheet,stage);
