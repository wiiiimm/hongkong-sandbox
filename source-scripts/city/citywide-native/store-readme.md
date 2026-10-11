# Shared native preparation store — HKS-222

`store.py` shares per-sheet mechanical preparation across processes and devices using the existing pinned Neon connection and fenced jobs. It does not write viewer assets, architectural approvals or `model_reviews`.

Call `migrate()` once, then `register(label, items)`. Each item contains `sheet`, `stage` (initially `prepare`), SHA-256 fields `sourceSha256`, `pipelineSha256`, `footprintSha256`, optional `terrainSha256`, and `inputs` containing frozen source ETag/directory checksums, parameters and references. Every field affects the cache key. Run labels and ordering do not: identical sheets are reused across different runs.

```python
run = store.register(label, items)
jobs = store.claim_many(run['runId'], owner, limit=8, lease_seconds=300)
# Each row includes the frozen item, owner, UUID token and server-clock lease.
store.heartbeat_many(jobs, lease_seconds=300)
# Prepare each sheet, upload immutable artefacts and independently read them back.
store.finish_group([{'job': job, 'result': result} for job, result in completed])
```

Claim only work that can start promptly. `claim_many` uses one transaction and connection, skips locked jobs and returns at most 8 rows; `claim` wraps a single claim. Empty claims can mean another worker owns pending work; consult `report(run_id)` before declaring completion. Keep heartbeats running during downloads, conversion and R2 verification. Heartbeats and completion reject expired or replaced tokens. A failed member rolls back the whole completion group, including copied results; successful rows remain immutable.

Results require `status` (`prepared`, `exceptions` or `source-empty`), non-negative integer `counts`, `artifacts` and the exact `store.QUALIFICATION`. Artefacts contain an `astra-modelling/` object `key`, `sha256`, `bytes` and `kind`; prepared results require at least one. Optional `models` retain compact per-model identity/state/check metadata in queryable JSONB. The caller must verify actual remote content before completion: the store checks binding syntax and ownership, not R2 itself.

Use `fail(job, 'network-timeout', retry=True)` for transient download/conversion-infrastructure/upload errors. Do not permanently cache those as deterministic `exceptions`. Existing bounded retry rules apply. Deterministic matching or source-format exceptions can be cached with explicit checks. Changing a relevant source, pipeline, footprint or terrain dependency produces a new immutable key. Do not include unrelated terrain patches or batch labels.

`report(run_id)` returns cached/pending counts and job/outcome summaries. `cached_results(run_id)` returns hash-verified result records, including `cacheKey`, `sheet`, `stage`, `resultSha256` and `result`.

Test without network: `python -m unittest discover -s source-scripts/city/citywide-native -p test_store.py -v`. Run isolated live fixtures with the same command prefixed by `MODELLING_INTEGRATION_TEST=1` using the configured modelling Python environment. Fixtures exercise overlapping runs, concurrent claims, changed-input invalidation, post-COPY expiry rollback and retry fencing. They do not acquire source models or publish anything.
