-- Immutable source inventory snapshots. Historical jobs are payload, never queue work.
CREATE SCHEMA IF NOT EXISTS astra_modelling;
CREATE TABLE IF NOT EXISTS astra_modelling.inventory_snapshots (
    snapshot_id text PRIMARY KEY,
    format_version integer NOT NULL,
    schema_json text NOT NULL,
    source_label text NOT NULL,
    row_count bigint NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS astra_modelling.inventory_tables (
    snapshot_id text NOT NULL REFERENCES astra_modelling.inventory_snapshots(snapshot_id),
    table_name text NOT NULL,
    metadata_json text NOT NULL,
    content_sha256 text NOT NULL,
    row_count bigint NOT NULL,
    PRIMARY KEY (snapshot_id, table_name)
);
CREATE TABLE IF NOT EXISTS astra_modelling.inventory_rows (
    snapshot_id text NOT NULL,
    table_name text NOT NULL,
    ordinal bigint NOT NULL,
    row_json text NOT NULL,
    source_key_json text NOT NULL,
    source_key_sha256 text NOT NULL,
    PRIMARY KEY (snapshot_id, table_name, ordinal),
    FOREIGN KEY (snapshot_id, table_name)
        REFERENCES astra_modelling.inventory_tables(snapshot_id, table_name)
);

CREATE INDEX IF NOT EXISTS inventory_source_key ON astra_modelling.inventory_rows(snapshot_id, table_name, source_key_sha256);
