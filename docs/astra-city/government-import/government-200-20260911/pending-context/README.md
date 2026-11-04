# Pending government-model context — 11 September 2026

Executor: Codex root. User authorised local checks, with zero per-model AI calls.
This is a diagnostic follow-up, not architectural modelling or publication.

## The complete 200-form funnel

| Stage | Count |
| --- | ---: |
| Exact cached government source forms loaded | 200 |
| Initial checks: advanced / held | 61 / 139 |
| Stricter acceptance of those 61: installed / held | 2 / 59 |
| Current total: installed / pending | **2 / 198** |

The 61 were an intermediate subset. All 200 were processed. The two installed
models remain landsd/81808:0 and landsd/204515:0; no extra model passed the current
direct-import contract during this follow-up. Neither pending nor processed means
installed. Counts refer to source forms, not necessarily whole physical buildings.

## Scripted follow-up of all 198 pending forms

All 198 decoded through the actual City loader with exact cached asset hashes and
unchanged current source records. All-vertex, triangle-centre and <=1 m low-rim edge
checks were repeated against drawn terrain. No geometry errors or missing drawn
terrain samples occurred. Overlapping current reasons: 166 terrain intersections,
38 ground-contact failures, 112 strict footprint/centroid fits and one sampler /
renderer disagreement. These counts overlap and must not be added.

Original TIN geometry was recovered for all 70 source sheets using the cached ZIP
central directory, pinned ETag, member CRC and SHA verification. Transfers total
271,709,541 bytes; derived compact original ZIPs total 271,196,447 bytes and remain
in the ignored local pass cache. These are data transfers, not AI calls. Source
photographs were omitted; original terrain/model geometry was not edited.

All decoded model vertices were compared with barycentric heights of original
terrain triangles. Each pending form receives one primary investigation route:

| Primary route | Forms |
| --- | ---: |
| Current vertex burial absent against original terrain | 122 |
| Some vertices also below original terrain; substructure/context unresolved | 37 |
| Original sheet terrain does not cover every model vertex | 13 |
| Native contact/elevated-support investigation | 17 |
| Strict identity fit, after the preceding terrain routes | 7 |
| Remaining current ground-contact problems | 2 |
| **Total pending** | **198** |

The 122 identify a viewer-terrain discrepancy at sampled source vertices, not 122
approved terrain patches or imports. Sixty-six also fail the strict identity gate.
The 13 partial-coverage cases are not missing government building meshes: their
building geometry loaded, but the selected sheet's TIN did not cover every vertex.
Neighbouring footprint intersections are recorded as support hints only. No actual
companion-support triangle acceptance or assembly membership is inferred. A source
vertex below native ground may be a legitimate foundation; this pass does not
judge architecture. The two remaining current-contact cases have acceptable native
vertex contact but still fail the drawn-terrain contact contract.

No acceptance threshold was relaxed. No model, terrain, manifest, review snapshot
or public progress count was changed. Public enhanced count remains 283 overall;
276 / 212,669 government-source forms completed (0.13%). Further work requires
bounded source-backed terrain corrections, adjacent TIN coverage, support geometry
and identity evidence, followed by the existing publication/runtime guards.

## Evidence and verification

- `selection.json.gz`: fresh 198-form snapshot, original batch linkage, exact source
  records, frozen native result hashes and current manifest hash; excludes the two
  installed models. Native hashes were rechecked read-only in Neon before claiming.
- `metrics.json`: actual drawn-terrain samples, asset/current-data/code hashes.
- `results.json.gz`: complete per-form routes, source-TIN metrics, neighbour hints,
  source member/checksum provenance and input hashes.
- `neon-sync.json`: full result readback exactly matched all 198 rows; writes were
  fenced by both the job token and live source ownership. No review/progress writes.
- Twelve policy/selection/context tests pass, including four analytic native-TIN
  cases: false viewer burial, burial in both sources, incomplete coverage and slope
  interpolation. JavaScript syntax and Git whitespace checks pass.

The processing pass took 101.902 seconds after preparation. No new browser test is
claimed because nothing was published or changed in the runtime. CPU diagnostics
are not browser acceptance, architectural acceptance or a performance benchmark.
Source reservations were released by the supervisor after verified Neon sync.

Shared stage: `government-pending-context-v1`.
Job: `037fef779d7f6c875e84a1129feef4bda641a141bac072bf2c224d3fc902d532`.

## Reproduction and limits

The bounded runner is `source-scripts/city/government-import/pending-context.py`.
It uses the existing pinned Neon connection and ignored exact-source cache from the
original batch. It refuses to overwrite an existing selection on a fresh start.
The `--execute` continuation requires a currently owned reservation and is intended
for a failed/incomplete run, not repeating a successful shared job. Do not rerun a
completed pass over its archived evidence; use a new version/folder for new inputs.
The 70 original source caches are local, not claimed as a new R2 backup.

The metrics entry point now also accepts an explicit `--selection`, `--out` and
optional `--geometry-out`. Its default still measures the historical 61; always use
separate output paths for new evidence. Native context is vertex-only and must not
be substituted for the more conservative full direct-import acceptance metrics.
No AI modelling, architectural scoring, simplification or reconstruction occurred.
