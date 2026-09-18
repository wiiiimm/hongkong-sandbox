-- Additive derived metadata only. No review, job, reservation or runtime writes.
CREATE TABLE IF NOT EXISTS astra_modelling.native_model_sizes (
    run_id text NOT NULL,
    cache_key text NOT NULL,
    model_id text NOT NULL,
    policy text NOT NULL CHECK (policy = 'government-size-v1'),
    source_result_sha text NOT NULL,
    sheet text NOT NULL,
    source_entry text NOT NULL,
    source_state text NOT NULL,
    viewer_uid text,
    building_csuid text,
    source_hold_reason text,
    source_error text,
    triangles bigint CHECK (triangles >= 0),
    source_vertices bigint CHECK (source_vertices >= 0),
    indexed_vertices bigint CHECK (indexed_vertices >= 0),
    compressed_bytes bigint CHECK (compressed_bytes >= 0),
    glb_bytes bigint CHECK (glb_bytes >= 0),
    geometry_bytes bigint CHECK (geometry_bytes >= 0),
    width_m double precision CHECK (width_m >= 0),
    height_m double precision CHECK (height_m >= 0),
    depth_m double precision CHECK (depth_m >= 0),
    size_group text GENERATED ALWAYS AS (
        CASE WHEN triangles IS NULL THEN 'unmeasured'
             WHEN triangles < 100 THEN 'xs'
             WHEN triangles < 500 THEN 'small'
             WHEN triangles < 2000 THEN 'medium'
             WHEN triangles < 10000 THEN 'large'
             WHEN triangles < 50000 THEN 'xl'
             ELSE 'xxl' END
    ) STORED,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (run_id, cache_key, model_id),
    FOREIGN KEY (run_id, cache_key)
        REFERENCES astra_modelling.native_stage_members(run_id, cache_key)
);
CREATE INDEX IF NOT EXISTS native_model_sizes_group
    ON astra_modelling.native_model_sizes
    (run_id, size_group, triangles DESC NULLS LAST, cache_key, model_id);
CREATE INDEX IF NOT EXISTS native_model_sizes_complexity
    ON astra_modelling.native_model_sizes
    (run_id, triangles DESC NULLS LAST, cache_key, model_id);
CREATE INDEX IF NOT EXISTS native_model_sizes_download
    ON astra_modelling.native_model_sizes
    (run_id, compressed_bytes DESC NULLS LAST, cache_key, model_id);
CREATE INDEX IF NOT EXISTS native_model_sizes_memory
    ON astra_modelling.native_model_sizes
    (run_id, geometry_bytes DESC NULLS LAST, cache_key, model_id);
CREATE INDEX IF NOT EXISTS native_model_sizes_uid
    ON astra_modelling.native_model_sizes (run_id, viewer_uid)
    WHERE viewer_uid IS NOT NULL;
CREATE TABLE IF NOT EXISTS astra_modelling.native_model_size_runs (
    run_id text PRIMARY KEY REFERENCES astra_modelling.native_stage_runs(run_id),
    policy text NOT NULL CHECK (policy = 'government-size-v1'),
    source_digest text NOT NULL,
    summary jsonb NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
