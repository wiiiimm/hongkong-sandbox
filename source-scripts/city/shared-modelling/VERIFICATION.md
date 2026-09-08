# HKS-217 verification — 8 September 2026

Target: `soft-snow-34493321` / `br-icy-firefly-b3zn5ogh` (`astra-modelling`), PostgreSQL 18.6. All schema, snapshot and queue writes in this pass use that isolated endpoint and `astra_modelling` schema. Parent production remains the project's default branch.

- Verified authenticated connection using full TLS verification and certifi CA roots. Initial system-root attempts failed; no insecure TLS workaround was used.
- Live queue suite: 6 tests passed in 122.307 seconds (four database integration cases and two original routing cases). Sixteen concurrent claims across eight threads returned sixteen distinct jobs, repeat planning retained IDs, completion could not be overwritten, same-owner expiry/reclaim used new tokens, expired heartbeat/finish were refused, capability/batch isolation and terminal retry expiry passed.
- Additional local suite: 14 tests passed, five opt-in live cases skipped. Includes libpq environment override rejection, inventory lookup contract, adapter reuse, and failing-adapter non-success. The live cases were run separately; a skipped offline invocation is not their evidence.
- Independent review found three issues: libpq environment routing overrides; decoded source-record contract; failed worker returning success. All fixed with regression coverage.
- Live inventory fixture and full migration evidence are separately recorded in `inventory-verification.json` by the migration executor. Do not infer whole-inventory remote verification from the six-row fixture alone.

Snapshot import preserves historical jobs without scheduling them. New shared jobs are explicit batches. The shared worker supports the pure metadata audit and the explicitly gated source-preserving cached-model adapter. Other terrain/download/browser/publication scripts retain their local execution contracts and require per-job wrappers before simultaneous devices can safely run them. No new model is accepted or published by this infrastructure pass.

R2 remote access and actual cloud round-trip remain a separate gate under HKS-216. The verified local cache clone does not prove a remote backup exists.

## Independent-process real-source worker smoke

Two separate worker processes (two threads each), launched outside the checkout, audited eight real imported building records directly from Neon with no SQLite/cache arguments. All eight completed exactly once; repeated planning retained completion. Elapsed 53.288 seconds including planning and repeat verification. Evidence: `worker-verification.json`. Two additional private-environment setup tests pass (branch pinning, restrictive file permissions, no overwrite, missing-credential refusal).

## Independent-process model preparation

Two processes reused the existing cached-model processor for two explicitly selected current-set jobs from Neon. Both completed once, with verified immutable local-test objects (7,692 and 63,414 bytes), no SQLite/catalogue/viewer writes, and placement review still required. Elapsed 16.611 seconds. This uses LocalStore and does not establish R2 availability. Evidence: `model-worker-verification.json`; five adapter tests and the combined 21-test offline suite pass (five live-only cases skipped in that invocation). Independent review found no new adapter/registration defects.
