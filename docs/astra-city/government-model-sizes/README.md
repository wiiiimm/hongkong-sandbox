# Government model size inventory — 11 September 2026

Executor: Codex root. Policy: `government-size-v1`. All 216,976 indexed government
building **model parts** in frozen native run
`e98f84fdaeb489b229af3910d80d765bb87dbbdc565ec1794836b04909f370ec` are covered.
This population includes unmatched source parts; it differs from the 212,669
current viewer-matched government forms and 346,108 total mapped forms.

| Group | Triangle range | Models |
| --- | ---: | ---: |
| XS | 0–99 | 97,946 |
| Small | 100–499 | 92,361 |
| Medium | 500–1,999 | 20,552 |
| Large | 2,000–9,999 | 5,567 |
| XL | 10,000–49,999 | 521 |
| XXL | 50,000+ | 22 |
| Unmeasured | Unknown | 7 |
| **Total** | | **216,976** |

The seven Unmeasured sources are the previously confirmed corrupt government
files; their failed source states/errors remain explicit. No missing measurement
is silently treated as a small model.

Neon tables: `astra_modelling.native_model_sizes` (indexed individual measurements)
and `astra_modelling.native_model_size_runs` (verified run summary). Raw download
bytes, GLB bytes, decoded geometry bytes, source/indexed vertices and native XYZ
bounding dimensions remain independently queryable. Triangle grouping is a mesh
cost category; it does not score appearance, importance, FPS or installation ease.

Validation uses the entire immutable source projection, not a sample: all stored
fields match original Neon metadata; thirteen exact boundary cases exercise the
actual generated column. The migration was first run in a rollback transaction.
`summary.json` contains committed-run readback and representative index-plan checks;
`dry-run.json` retains the pre-commit migration check. `idempotency.json` verifies
216,976 reused rows and zero inserts on an unchanged rerun.
`lookup-verification.json` verifies ordinary reads and unchanged prior batch reviews.
Lookup timing excludes
network/connection/cold-start overhead.

No source downloads, per-model AI calls, geometry changes, queue creation, source
reservations or review/publication/progress changes. The original 200-form batch
remains 11 installed and 189 held; earlier evidence and reasons remain in Neon.

[Commands, SQL and resumption details](../../../source-scripts/city/government-import/size-groups/README.md).
Future work can select any bracket or sort by raw cost. Queue construction is
explicitly deferred at the user’s request.
