-- Additive screening ledger. Does not mutate model reviews or historical jobs.
CREATE TABLE IF NOT EXISTS astra_modelling.enhancement_screening_events (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 uid text NOT NULL,
 input_hash text NOT NULL CHECK (input_hash ~ '^[a-f0-9]{64}$'),
 policy text NOT NULL,
 decision text NOT NULL CHECK (decision IN ('good-to-go','enhancement-required')),
 reason text NOT NULL CHECK (length(trim(reason)) > 0),
 evidence text NOT NULL,
 evidence_hash text NOT NULL CHECK (evidence_hash ~ '^[a-f0-9]{64}$'),
 owner text NOT NULL,
 token uuid NOT NULL,
 request_id text NOT NULL,
 reviewed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 UNIQUE(request_id, uid)
);
CREATE INDEX IF NOT EXISTS enhancement_screening_lookup
 ON astra_modelling.enhancement_screening_events(uid, input_hash, policy, id DESC);
