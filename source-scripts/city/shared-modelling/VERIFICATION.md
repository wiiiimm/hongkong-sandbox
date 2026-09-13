# HKS-217 verification — 8 September 2026

Target: `soft-snow-34493321` / `br-icy-firefly-b3zn5ogh` (`astra-modelling`), PostgreSQL 18.6. All schema, snapshot and queue writes in this pass use that isolated endpoint and `astra_modelling` schema. Parent production remains the project's default branch.

- Verified authenticated connection using full TLS verification and certifi CA roots. Initial system-root attempts failed; no insecure TLS workaround was used.
- Live queue suite: 6 tests passed in 122.307 seconds (four database integration cases and two original routing cases). Sixteen concurrent claims across eight threads returned sixteen distinct jobs, repeat planning retained IDs, completion could not be overwritten, same-owner expiry/reclaim used new tokens, expired heartbeat/finish were refused, capability/batch isolation and terminal retry expiry passed.
- Additional local suite: 14 tests passed, five opt-in live cases skipped. Includes libpq environment override rejection, inventory lookup contract, adapter reuse, and failing-adapter non-success. The live cases were run separately; a skipped offline invocation is not their evidence.
- Independent review found three issues: libpq environment routing overrides; decoded source-record contract; failed worker returning success. All fixed with regression coverage.
- Live inventory fixture and full migration evidence are separately recorded in `inventory-verification.json` by the migration executor. Do not infer whole-inventory remote verification from the six-row fixture alone.

Snapshot import preserves historical jobs without scheduling them. New shared jobs are explicit batches. The shared worker supports the pure metadata audit and the explicitly gated source-preserving cached-model adapter. Other terrain/download/browser/publication scripts retain their local execution contracts and require per-job wrappers before simultaneous devices can safely run them. No new model is accepted or published by this infrastructure pass.

The model worker cloud round-trip was subsequently verified below under HKS-216. Full working-snapshot upload and clean restoration are separately evidenced by the snapshot workflow; neither the local clone nor two model objects proves a complete remote backup.

## Independent-process real-source worker smoke

Two separate worker processes (two threads each), launched outside the checkout, audited eight real imported building records directly from Neon with no SQLite/cache arguments. All eight completed exactly once; repeated planning retained completion. Elapsed 53.288 seconds including planning and repeat verification. Evidence: `worker-verification.json`. Two additional private-environment setup tests pass (branch pinning, restrictive file permissions, no overwrite, missing-credential refusal).

## Independent-process model preparation

Two processes reused the existing cached-model processor for two explicitly selected current-set jobs from Neon. Both completed once, with verified immutable local-test objects (7,692 and 63,414 bytes), no SQLite/catalogue/viewer writes, and placement review still required. Elapsed 16.611 seconds. This uses LocalStore and does not establish R2 availability. Evidence: `model-worker-verification.json`; five adapter tests and the combined 21-test offline suite pass (five live-only cases skipped in that invocation). Independent review found no new adapter/registration defects.

## Real R2 model preparation — HKS-216 / HKS-217

At 09:12 UTC on 8 September 2026, two concurrent worker threads processed two explicit current-set model jobs from immutable Neon snapshot `f26ca1cad7e19b984c78d12877a8b35cca7af8f434ab1c7ec8756983ccdc0008`. Both completed in one attempt, with no worker errors, in **14.873 seconds** including planning and independent object readback. This uses the actual Cloudflare R2 S3 API and existing `R2Store`, not LocalStore. Credentials were loaded from ignored environment configuration without printing or recording their values.

Batch: `verification-real-r2-model-76a05d8210914b289dd95a6c448f8318`. Target remains the pinned `astra-modelling` branch and schema. The existing cached-model converter reused retained source material; no bulk queue, SQLite, catalogue or viewer mutation occurred. Both results retain `staged-needs-placement-review`, `liveReplacement: false` and `publicationApproved: false`.

Bucket `hk-sandbox-assets` contains these immutable objects. After the worker's own verified write/readback, a separate download checked both complete bytes and SHA-256:

| Object key | Bytes | Verification |
| --- | ---: | --- |
| `astra-modelling/objects/sha256/c1/c1f45b68b350964035597487cf6398c8926b46da985c1e83aee8dd61edcc0eaa` | 7,692 | SHA-256 matches object basename |
| `astra-modelling/objects/sha256/f2/f27037644d72f619aa52736d65bdb57d7d3cfd98aaa8d5d7ea60743353ee7f88` | 63,414 | SHA-256 matches object basename |

Machine-readable evidence: [cloud-model-worker-verification.json](cloud-model-worker-verification.json). This validates real shared candidate processing and cloud transport, not new architectural refinement, multi-device cache availability, placement acceptance or publication.
