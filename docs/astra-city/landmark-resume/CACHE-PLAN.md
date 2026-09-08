# HKS-215 · Portable landmark working state

The practical unit is a **versioned working snapshot alongside a matching Git checkout**, with a local SQLite copy on each device. A remote database is unnecessary for this serial hand-off workflow. R2 could hold the immutable snapshot; it must not be used as a live SQLite filesystem or as a way for two devices to edit the same database. **This task created an inventory only: no backup, upload, download, database mutation or source/geometry change.** Upload remains a separate authorisation.

The measured closure covers preflight snapshot `3887f2f23fbad306`: **273 candidate models**, **245 terrain-flagged parts with native inputs**, and zero missing inventoried paths. [cache-inventory.json](cache-inventory.json) contains each path, existence, bytes, categories, rebuildability, restore profiles, Git tracking, link targets and existing provenance hashes. It deliberately omits credentials, HTTP URLs and file contents. [collect_inventory.py](collect_inventory.py) reads the existing database and prepared caches and **writes `cache-inventory.json` in this documentation folder**. It is an inventory producer for the populated source device, not a cold-device doctor or an integrity verifier. It requires the old database, prepared catalogue, acquisition caches and preflight/terrain reports to exist; it refuses an active SQLite WAL rather than inspecting an incoherent database. Recorded existing hashes have not been revalidated by this collector and are not a verified backup or snapshot.

## What to retain

| Working state | Current size | Treatment |
|---|---:|---|
| SQLite ledger | 640.10 MB | Retain a consistent backup: 346,115 buildings, 2,663 input records, selections and 29,760 historical job rows. Rebuilding the inventory does not restore job history or decisions. |
| Current prepared candidates | 28.49 MB | Retain all 273 compressed assets plus catalogues, proofs, selection, plan and validation. |
| Pinned preflight snapshot | 33.89 MB | Retain the full ignored snapshot directory, including its asset copies and `pin.json`; preserve the snapshot ID and hashes. |
| Selected native model files | 149.14 MB ignored | Retain source manifests/glTF/bin for current candidate jobs, or hydrate byte-identically from compact native ZIPs before running the CLI. |
| Native terrain files | 666.98 MB ignored | Retain native binaries, derived geometry glTF and terrain manifests. Original glTF hashes belong to native cache members; derived glTF has a separate hash. |
| Acquisition source caches | 260.73 MB ignored | Preserve compact ZIPs, complete directories, source revision/ETag metadata and per-sheet state. These prove checked absence and allow offline extraction. |
| Exact footprint selections | 0.36 MB ignored | Preserve every required `official-selection.json.gz`, including empty terrain selections. |
| Identity reference evidence | 10.14 MB ignored | Preserve cited cached material; upstream pages can change. |
| Official footprint source and archival 5 m DTM | 64.04 MB + 28.71 MB | Already tracked here, without Git LFS filters; retain through the matching checkout. Do not download replacements merely to resume. |

Rows overlap; their sizes are not additive. The machine inventory's deduplicated **path** totals are:

- **Portable working closure:** 1.793 GB outside Git, plus 0.871 GB of inventoried files already tracked. Some duplicate extraction/staging must be hydrated offline before all existing acquisition commands work. This is a conservative working closure, not a claim of optimal compressed size.
- **Restore for unmodified CLIs:** 2.607 GB outside Git, plus the same tracked files. This adds the required extracted-member and staging caches. It is the simplest first cross-device checkpoint.
- Content-addressed storage could reduce duplicate assets across prepared/preflight/source caches. No compression or content-dedup savings have been assumed or measured.

Current historical jobs include 5,404 pending rows from old batches. Preserve their batch memberships; they do not mean 5,404 outstanding landmark downloads.

## Snapshot and restore contract

When a backup is authorised, pause local job writers and use SQLite's online backup API (or `.backup`) to a new staging destination. Do not copy an open database file while ignoring a WAL. Run `PRAGMA quick_check` against the resulting backup, hash it, then package it with a manifest containing repository commit, preflight ID, relative paths, byte counts and SHA-256 values. Existing `expectedSHA256` values in this inventory are evidence references; **the future package must hash every actual packaged file**. No backup was created during this audit.

Use immutable snapshot identifiers and object hashes. Keep a small current-checkpoint pointer separate from immutable objects. Restore to a new local checkout and database path, verify all bytes before replacing any existing working state, then choose one device as the writer. Job leases from a previous machine are a recovery concern, not permission to merge divergent SQLite files. Preserve coordinate/reference facts and all identity/placement holds.

Recreate relative `landmark-identity/staged/` adapter symlinks after restoring their targets. The current inventory records 87 adapter/administrative links; do not copy the worktree's `.git` pointer, which belongs to the original checkout. No source-data references outside this checkout were found in the inspected closure. Python, Node and Chrome are external device dependencies, not source evidence: install suitable local runtimes instead of copying `/private/tmp/astra-city-venv`, `node_modules` or host binaries.

## Cold-clone pitfalls in the current commands

1. **Acquisition plans are tracked; their footprint selections are ignored.** `acquire.py` loads an existing plan without rebuilding `official-selection.json.gz`. A new or repaired sheet then fails in the decoder. Restore that exact selection, or add explicit offline hydration; blindly rerunning the command is insufficient.
2. **Completed state is not a payload restore mechanism.** `acquire.py` skips completed sheets; reports read staged manifests and `verify.py` requires retained members/ZIPs. Restore/hydrate all referenced files before trusting completion. Missing sheets now fail verification, and partially covered targets remain deferred.
3. **The cache scanner does not directly discover nested acquisition batches.** `cached_models.py` scans one-level `*/staged/*/manifest.json`; `stage_proposals.py` creates adapter symlinks for nested batches. Rebuild those links first. Its `run` command also writes selections/jobs, so it is not a read-only integrity check.
4. **The database alone is insufficient.** Completed candidate jobs still check native source hashes. Missing prepared outputs can be repacked by `run_stage`, but only with complete source dependencies. Its fingerprints include tool and runtime-input hashes; changing the checkout can legitimately invalidate a plan.
5. **Preflight snapshot contents are ignored.** A tracked `snapshot.json` pointer without `snapshots/<id>/assets/` cannot rerun the gallery. Recreating a fresh capture can change the identity. Restore the pinned directory instead, and keep candidate/validation/runtime hashes together.
6. **Legacy comparison evidence is a dependency.** `stage_proposals.summaries()` reads ignored `landmark-bulk/compact/catalogue.json`. The inventory includes it even though it is not the current output.
7. **Device paths are hard-coded.** The stage adapter defaults to one user's Node executable (overridable with `--node`). Gallery code currently hard-codes macOS Chrome and `127.0.0.1:4176`; changing device/OS requires configuring those paths and starting the matching preview. Python needs the existing geometry dependencies, including NumPy, Shapely and pyproj.
8. **Source revisions can change between checkpoints.** `15-NW-3B` already needed a separate repacked-archive snapshot. Preserve both the old hold and the resolving `terrain-source-refresh` evidence; do not overwrite ledgers or re-download broad source tiles on a cold clone.

Current gallery output is still being produced and is intentionally excluded from this stable working closure. Add its completed evidence files as a later optional review-evidence snapshot. This plan does not authorise modelling, geometry changes, terrain application or publication.
