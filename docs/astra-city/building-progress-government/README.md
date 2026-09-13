# Government-source model progress — HKS-220 / HKS-199

Implemented by Codex root on 11 September 2026. No map-reference images or model
geometry were produced or changed. Counts use the deployed City forms, existing
verified source reviews and the frozen Lands Department native preparation run.

| Statistic | Forms |
| --- | ---: |
| Models on this map | 346,108 |
| Government source matched | 212,669 |
| Enhanced on this map | 281 |
| Enhanced within government-source group | 274 |
| Government upgrades remaining | 212,395 |
| Other models awaiting sources (excludes completed forms) | 133,432 |

Progress is **274 / 212,669 = 0.1288387%, displayed 0.13%**. Seven verified enhanced
forms are outside the matched source group and still count toward 281. The frozen
proof contains 212,675 UID/CSUID pairs; six leave the denominator when intersected
with current displayed identities and suppression. This is source availability,
not a claim that every import already passes placement/runtime checks or needs
replacement. Existing detail can need verification only. No whole-building
completion is inferred from source-form counts.

The header shows enhanced count and scoped percentage, with compact map/source
totals underneath. Its dialog gives exact counts, the fraction behind the percentage,
and separate bars that partition all map forms without double counting. Existing
good-to-go evidence remains supported; there are currently zero such forms.

Refresh and provenance: [source script notes](../../../source-scripts/city/building-progress/README.md).
The source inventory was read from Neon in a read-only transaction. No acceptance,
model or diagnostic-history writes. Zero per-model AI calls; no modelling work.

## Verification

- Fresh read-only exporter run reproduced all 212,675 committed UID/CSUID pairs.
- `node --test 3d-viewer/city/tests/building-progress.test.js`: 11 tests pass.
- `node 3d-viewer/scripts/build_progress.mjs`: self-contained static build passes.
- With the viewer served on port 4176,
  `node 3d-viewer/city/tests/building-progress-browser.mjs` checks actual dialog
  markup/CSS/module at desktop 1280×900, phone 390×844 and narrow 320×740, followed
  by unmodified City startup. It covers unavailable, stale, empty, mixed,
  invalid-count and missing-source-scope cases, accessible values, exact denominator,
  partition sums, expansion, Escape dismissal and no horizontal overflow.
- `browser.json` records the results. PNGs capture each layout/header and
  `live-dialog.png` the running City. Screenshots are checked for readability and
  layout; software Chrome is not physical-device performance certification.

Full metadata/shape screening is retired from the active pipeline and skill.
Existing acceptance/hash reuse and import safety checks remain; optional diagnostic
scripts/reports and Neon history are preserved. This UI does not trigger screening,
source preparation, imports or AI jobs.
