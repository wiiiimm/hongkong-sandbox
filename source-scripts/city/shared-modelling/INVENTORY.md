# Portable source inventory (HKS-217)

`inventory_sync.py` stores immutable, source-accounted SQLite snapshots in the
pinned Neon modelling branch. It imports every ordinary inventory table,
including selections, reviews, provenance, and historical job payloads. Historical
`pending` jobs **do not become runnable shared jobs**. The shared queue is separate.

The source SQLite connection is read-only and remains in one read transaction
through fingerprinting and upload. The logical SHA-256 identity covers schema SQL,
source rowids, all values, user/application versions, and every table's count and
content hash. Rtree shadow pages are not copied: logical bounds are retained and
SQLite rebuilds the index during restoration. Generated columns recompute from
the original schema; triggers are created after data is restored.

## Commands

Run from the repository root, using the configured modelling Python environment.
The database commands use `db.connect()` and its dedicated-branch guard; they never
fall back to the application's production connection. No connection string is
accepted as a CLI argument or printed.

```sh
python source-scripts/city/shared-modelling/inventory_sync.py inspect \
  --sqlite source-scripts/city/building-batch/local/buildings.sqlite

python source-scripts/city/shared-modelling/inventory_sync.py import \
  --sqlite source-scripts/city/building-batch/local/buildings.sqlite

python source-scripts/city/shared-modelling/inventory_sync.py export \
  --snapshot SNAPSHOT_SHA256 --sqlite /new/workspace/buildings.sqlite

python source-scripts/city/shared-modelling/inventory_sync.py verify \
  --snapshot SNAPSHOT_SHA256 --sqlite /new/workspace/buildings.sqlite
```

`inspect` is offline and makes no database changes. `import` uses bounded-memory
PostgreSQL COPY and commits one immutable snapshot atomically. An identical rerun
verifies stored content and skips replay. A changed source creates another
snapshot; it never overwrites another worker's queue or an older snapshot.
Concurrent importers serialise schema creation briefly and use a per-fingerprint
transaction lock to avoid duplicate uploads.

`export` streams rows using a server cursor into a new adjacent temporary SQLite
file. It verifies every table's count/hash, restores source indexes/views/triggers,
checks SQLite integrity and compares the reconstructed logical fingerprint before
atomically publishing the destination. Existing destination files are refused.
The export is a point-in-time source snapshot, **not a live mirror of shared queue
updates**. Model files and terrain caches must be restored separately from R2.

## Querying source identities

`astra_modelling.inventory_rows` stores table name, source order, canonical source
key, indexed key SHA-256 and JSON-encoded row values. Table metadata describes the
column order and whether the first value is a preserved SQLite rowid. Values keep
SQLite types: blobs use base64 and floats use hexadecimal strings. This avoids
JSON number precision loss. It is an archival/import bridge, not a replacement for
native spatial SQL tables.

Python callers can retrieve a source row without scanning the snapshot:

```python
from inventory_sync import lookup_row
row = lookup_row(connection, snapshot_id, 'buildings',
                 {'primary_key': [['uid', 'landsd:example']]})
```

Composite keys follow the original primary-key column order. Nullable primary
keys fall back to `{'rowid': 17}`; Rtree rows use `{'virtual_id': 17}`. Stored key
hashes and payload content are revalidated during verify, export and import reuse.

## Supported source schema and limits

The current 13 logical inventory tables are supported. Unknown virtual-table
modules are rejected, as are ordinary tables that shadow all three SQLite rowid
aliases. SQLite-specific binary storage layout, WAL files and query-planner
statistics are deliberately not archived; logical data and application schema are.
No snapshot removal or production write operation is provided.

Offline fixture verification:

```sh
python -m unittest discover -s source-scripts/city/shared-modelling \
  -p test_inventory_sync.py -v
```

The fixture includes non-contiguous rowids linked to Rtree bounds, generated
columns, BLOB/text/float fidelity, AUTOINCREMENT history, historical pending jobs,
concurrent WAL writes, corrupt payload rejection and destination protection.
Live Neon import/export evidence must be recorded separately; offline tests do
not establish that remote credentials or permissions work.

To repeat the small remote fixture against the pinned modelling branch, set
`ASTRA_TEST_LIVE_INVENTORY=1` for the same test command. This imports one immutable
six-row fixture snapshot (subsequent runs reuse it), never modifies runnable jobs,
and exercises lookup, export and verification. It is deliberately opt-in.
