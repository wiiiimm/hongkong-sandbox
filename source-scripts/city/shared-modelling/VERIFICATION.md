# HKS-217 verification — 8 September 2026

Target: `soft-snow-34493321` / `br-icy-firefly-b3zn5ogh` (`astra-modelling`), PostgreSQL 18.6. All schema, snapshot and queue writes in this pass use that isolated endpoint and `astra_modelling` schema. Parent production remains the project's default branch.

- Verified authenticated connection using full TLS verification and certifi CA roots. Initial system-root attempts failed; no insecure TLS workaround was used.
- Live queue suite: 6 tests passed in 122.307 seconds (four database integration cases and two original routing cases). Sixteen concurrent claims across eight threads returned sixteen distinct jobs, repeat planning retained IDs, completion could not be overwritten, same-owner expiry/reclaim used new tokens, expired heartbeat/finish were refused, capability/batch isolation and terminal retry expiry passed.
- Additional local suite: 14 tests passed, five opt-in live cases skipped. Includes libpq environment override rejection, inventory lookup contract, adapter reuse, and failing-adapter non-success. The live cases were run separately; a skipped offline invocation is not their evidence.
- Independent review found three issues: libpq environment routing overrides; decoded source-record contract; failed worker returning success. All fixed with regression coverage.
- Live inventory fixture and full migration evidence are separately recorded in `inventory-verification.json` by the migration executor. Do not infer whole-inventory remote verification from the six-row fixture alone.

Snapshot import preserves historical jobs without scheduling them. New shared jobs are explicit batches. Current shared worker supports the existing pure metadata-audit adapter; older geometry/download/browser scripts retain their local execution contracts and require per-job wrappers before simultaneous devices can safely run them. No new model is accepted or published by this infrastructure pass.

R2 remote access and actual cloud round-trip remain a separate gate under HKS-216. The verified local cache clone does not prove a remote backup exists.
