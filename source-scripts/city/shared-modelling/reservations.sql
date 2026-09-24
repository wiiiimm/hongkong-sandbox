-- Version 2: cross-batch, agent-session resource reservations. No public schema changes.
CREATE SCHEMA IF NOT EXISTS astra_modelling;
CREATE TABLE IF NOT EXISTS astra_modelling.reservation_schema_versions (
 version integer PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE SEQUENCE IF NOT EXISTS astra_modelling.reservation_generation;
CREATE TABLE IF NOT EXISTS astra_modelling.reservation_groups (
 token uuid PRIMARY KEY,
 owner text NOT NULL,
 batch text,
 resources text[] NOT NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 heartbeat_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 lease_until timestamptz NOT NULL,
 released_at timestamptz
);
CREATE TABLE IF NOT EXISTS astra_modelling.reservations (
 resource text PRIMARY KEY,
 token uuid NOT NULL REFERENCES astra_modelling.reservation_groups(token),
 generation bigint NOT NULL DEFAULT nextval('astra_modelling.reservation_generation')
);
CREATE INDEX IF NOT EXISTS reservations_token ON astra_modelling.reservations(token);
CREATE TABLE IF NOT EXISTS astra_modelling.reservation_events (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 occurred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 action text NOT NULL,
 actor text NOT NULL,
 token uuid NOT NULL,
 resources text[] NOT NULL,
 reason text,
 previous jsonb NOT NULL
);
INSERT INTO astra_modelling.reservation_schema_versions(version) VALUES(2) ON CONFLICT DO NOTHING;
