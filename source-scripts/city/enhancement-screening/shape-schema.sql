-- HKS-203: immutable diagnostic run history; separate from acceptance ledgers.
CREATE TABLE IF NOT EXISTS astra_modelling.shape_screening_runs (
    run_id text PRIMARY KEY CHECK (length(run_id) = 64),
    manifest jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (manifest->>'authoritative' = 'false'),
    CHECK (manifest->>'automaticAcceptanceEnabled' = 'false')
);
CREATE TABLE IF NOT EXISTS astra_modelling.shape_screening_outcomes (
    run_id text NOT NULL REFERENCES astra_modelling.shape_screening_runs(run_id),
    uid text NOT NULL,
    role text NOT NULL CHECK (role IN ('sample', 'control')),
    action text NOT NULL CHECK (action IN ('skip', 'keep-current-candidate', 'import-candidate', 'retain-pending')),
    input_hash text NOT NULL,
    result_sha text NOT NULL CHECK (length(result_sha) = 64),
    result jsonb NOT NULL,
    PRIMARY KEY (run_id, uid)
);
CREATE INDEX IF NOT EXISTS shape_screening_outcomes_uid ON astra_modelling.shape_screening_outcomes(uid);
