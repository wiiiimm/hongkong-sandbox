# Local building inventory — HKS-199 / HKS-200

Run from the Astra worktree root (Python standard library only):

```sh
python3 source-scripts/city/building-batch/inventory.py
python3 -m unittest discover -s source-scripts/city/building-batch -p 'test_*.py' -v
```

The first command writes `source-scripts/city/building-batch/local/buildings.sqlite`, which is ignored by Git and not deployed. Use `--db` for another location and `--viewer` for another input snapshot. Do not run concurrently with a publisher changing the viewer assets; the inventory has a single SQLite writer transaction. Reading/hashing local inputs is deliberate even on repeated runs so changed bytes cannot silently look complete.

Inputs are the existing city manifest, 452 tile files, official-model catalogues/assets and 132 review-section definitions. There are no network or AI dependencies. SHA-256 fingerprints skip unchanged tile decoding/import. Models retain native asset paths and metadata; embedded geometry remains in its original tile with a content fingerprint. Source manifest/version metadata, footprints, source IDs, recorded/estimated heights, placement notes and local coordinates are retained. Coordinates are Astra local metres, x=E-834500, z=816500-N; heights are HKPD. Section definitions are retained, but geographic section/building membership is HKS-201 work.

Refreshes upsert changed records, retain removed buildings as inactive history, and preserve separate selections/reviews. Use `WHERE active=1` for current coverage. A failed or interrupted import rolls back to the previous committed inventory; restart the command to retry. This is transaction-based inventory recovery, not the future leased multi-worker processing system. Invalid/duplicate identities, missing files, model hashes and count mismatches fail closed. Existing model presence is not a new quality approval. This script does not re-run model conversion, modify the live map or declare any region complete.

Tables: `buildings`, `models`, `inputs`, `settings`, `sections`, `selections`, `reviews`. Source geometry/text stay separate from review state. The later job ledger and stage adapters belong to HKS-202; no placeholder job is marked successful here.

## Verified 7 September 2026

Initial local run: 346,115 forms, 342,223 distinct government IDs, 1,859 embedded and 1,020 progressive model references, 132 sections. 14.56 s, 482,910,208-byte SQLite database. Repeat: 1.17 s, all 452 tiles skipped, zero building updates. All 1,020 external model assets verified against catalogue SHA-256/size. Six tests exercise repeat/preserved selection, change/removal, duplicate rollback, interruption/resume, missing input, and model identity/checksum failures. Evidence JSON is in `docs/astra-city/building-batch/`.

## Execution issues

All belong to the Astra Living Hong Kong milestone; parent HKS-199.

- HKS-200: inventory (implemented; review pending), 4 points.
- HKS-201: tourist landmark and surrounding-area selection, 4 points.
- HKS-202: resumable local processing adapters and worker ledger, 8 points.
- HKS-203: validation, compact exception reports and guarded publication, 8 points.
- HKS-204: measured Central/Mui Wo/Tai O/Ngong Ping trial, 4 points.
- HKS-205: trial-gated rollout across 132 sections, 4 points.

Existing regional issues remain the quality owners. HKS-198 optional government photo imagery is separate. No trial selection or new model-processing batch has run yet.
