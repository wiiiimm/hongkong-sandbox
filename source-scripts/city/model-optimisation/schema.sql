-- Additive only: no source inventory, modelling jobs or acceptance records are rewritten.
CREATE TABLE IF NOT EXISTS astra_modelling.optimisation_sources (
 revision_id text PRIMARY KEY CHECK(revision_id ~ '^[a-f0-9]{64}$'),
 uid text NOT NULL,
 source_sha256 text NOT NULL CHECK(source_sha256 ~ '^[a-f0-9]{64}$'),
 source_commit text NOT NULL,
 source jsonb NOT NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE INDEX IF NOT EXISTS optimisation_source_uid ON astra_modelling.optimisation_sources(uid);
CREATE TABLE IF NOT EXISTS astra_modelling.optimisation_variants (
 variant_id text PRIMARY KEY CHECK(variant_id ~ '^[a-f0-9]{64}$'),
 revision_id text NOT NULL REFERENCES astra_modelling.optimisation_sources(revision_id),
 recipe_sha256 text NOT NULL CHECK(recipe_sha256 ~ '^[a-f0-9]{64}$'),
 tier text NOT NULL CHECK(tier IN ('original','high','balanced','lightweight')),
 recipe jsonb NOT NULL,
 planned_by text NOT NULL,
 job_id text UNIQUE REFERENCES astra_modelling.jobs(id),
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 UNIQUE(revision_id,recipe_sha256)
);
CREATE TABLE IF NOT EXISTS astra_modelling.optimisation_reviews (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 variant_id text NOT NULL REFERENCES astra_modelling.optimisation_variants(variant_id),
 decision text NOT NULL CHECK(decision IN ('approved','rejected')),
 actor text NOT NULL,
 artifact_sha256 text NOT NULL CHECK(artifact_sha256 ~ '^[a-f0-9]{64}$'),
 evidence jsonb NOT NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE INDEX IF NOT EXISTS optimisation_review_variant ON astra_modelling.optimisation_reviews(variant_id,id DESC);
CREATE OR REPLACE VIEW astra_modelling.optimisation_status AS
 SELECT s.uid,s.source_sha256,v.revision_id,v.variant_id,v.tier,v.recipe_sha256,
        COALESCE(j.status,'planned') AS processing_status,
        COALESCE(r.decision,'unreviewed') AS validation_status,
        v.job_id,j.attempts,j.owner,j.lease_until,j.error,j.result,
        r.id AS review_id,r.artifact_sha256 AS reviewed_artifact_sha256
 FROM astra_modelling.optimisation_variants v
 JOIN astra_modelling.optimisation_sources s USING(revision_id)
 LEFT JOIN astra_modelling.jobs j ON j.id=v.job_id
 LEFT JOIN LATERAL (
   SELECT id,decision,artifact_sha256 FROM astra_modelling.optimisation_reviews
   WHERE variant_id=v.variant_id ORDER BY id DESC LIMIT 1
 ) r ON true;
