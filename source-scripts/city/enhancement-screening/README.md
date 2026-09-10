# Good-enough screening — HKS-220 / HKS-199

The goal is to avoid unnecessary enhancement. A current, evidenced good-to-go
assessment skips modelling without replacing any geometry. This is separate from
native acquisition, source diagnostics and architectural publication approval.

## Four public categories; three work actions

| Category | Meaning | Planner action |
| --- | --- | --- |
| Enhanced | Installed geometry has a matching verified source review, with no current rework decision | skip |
| Good to go | Current city representation was assessed as sufficient | skip |
| Enhancement required | Current assessment names a worthwhile visible improvement | enhance |
| Not screened | No current accepted assessment, including invalidated prior decisions | assess |

These are source forms (tower/podium/wing), not inferred physical buildings. A
current rework decision overrides historical enhanced credit. Enhanced takes
precedence over good to go so a form cannot count twice. Removed bridge proxy
forms are excluded. The old reviewedEnhancedForms field is retained as historical
review coverage; use breakdown/readyForms for the current public categories.

## Script-only planning

No AI calls, source downloads, conversions, new geometry or automatic visual
acceptance occur in this pass. Run from the intended checkout using the existing
shared-modelling Python dependencies and Node:

```sh
python source-scripts/city/enhancement-screening/screen.py migrate
python source-scripts/city/enhancement-screening/screen.py plan
```

Migration is additive on the pinned branch in `shared-modelling/branch.json`.
Existing `.env.modelling` configuration and host/TLS guards apply; never substitute
the application's default database. Plans refresh the latest shared decisions
before reading current committed viewer inputs. A failed refresh aborts.

Outputs under ignored `local/`: `inputs.json.gz`, `skip.json.gz`, `enhance.json.gz`,
`assess.json.gz`, and `summary.json`. Do not feed `assess` into a modelling queue.
The planner does not alter historical jobs or enqueue new jobs. Use its partition
before creating a bounded enhancement batch, then recheck after reserving the
selected source keys. Keep required podium/support components even when their own
optional enhancement is skipped. The plan is a snapshot, not a queue lock.

`plan --offline` previews committed proof without credentials. Its outputs are
explicitly non-authoritative; do not schedule work from them.

## Deciding good enough

Reuse existing audit results from HKS-221 where their keys still match. Look at
current city geometry with its existing styling, not the comparison's plain
baseline. Ask which recognisable feature is missing and whether it matters at
normal viewing distance. Ordinary footprint-based buildings may be good enough;
a museum missing its defining dome may warrant an upgrade. Clean metadata,
triangle counts, lack of source availability and simple building shape alone do
not prove adequacy. Geometry differences can prioritise review, not grant it.

The initial policy intentionally has no heuristic auto-acceptance threshold.
Calibrate such a rule with representative labelled examples before adding it.
Until then, only existing verified enhancements skip automatically; new good-to-go
or rework decisions need evidenced human/agent assessment. This prevents spending
AI tokens on every building while keeping unknown quality honest.

## Recording decisions and skipping repeat work

Reserve all source UIDs with the existing `shared-modelling/RESERVATIONS.md` flow.
Create a JSON array with each `uid`, `inputHash` from the current plan, `decision`
(`good-to-go` or `enhancement-required`), a concrete `reason`, repository-relative
`evidence`, and SHA-256 `evidenceHash`. Evidence should show the current
representation and basis for acceptance or the specific missing feature.

```sh
python source-scripts/city/enhancement-screening/screen.py record \
  --entries path/to/decisions.json --receipt path/to/private-receipt.json \
  --request-id stable-screening-operation-id
```

The command rebuilds current inputs, verifies evidence hashes, checks live source
ownership inside the database transaction, and appends events atomically. Identical
request retries reuse results; different content requires a new request ID.
Previous decisions remain in history. Latest per-UID decisions are exported to
`3d-viewer/scripts/building-progress/screening-proof.json`; commit that proof and
regenerated statistics after review. Static Vercel builds never contact Neon.

A decision is bound to the canonical complete source record, native model
metadata/hash, rendering implementation, terrain/bridge context and policy version.
No clock-based expiry forces repeated review of unchanged buildings. Changed
inputs invalidate acceptance. Terrain invalidation is currently global and
conservative: an unrelated terrain edit can require reassessment. A future revision
can reuse the audit engine's intersecting-patch keys, with an explicit migration.

## Verification

```sh
node --test 3d-viewer/city/tests/building-progress.test.js
python -m unittest discover -s source-scripts/city/enhancement-screening -v
SCREENING_LIVE_TEST=1 python -m unittest discover -s source-scripts/city/enhancement-screening -v
```

The live test uses rollback-only fixture events; it retains no fake acceptance.
The existing browser check is `3d-viewer/city/tests/building-progress-browser.mjs`,
with a static viewer server on port 4176. It tests the actual dialog HTML/CSS/module
without starting the unrelated 3D renderer; full-page smoke evidence is captured
separately. Evidence lives in
`docs/astra-city/enhancement-screening/`.

## 1,000-form pilot and Kai Tak Stadium control

`pilot.py` runs a deterministic, read-only triage experiment. It samples displayed
source forms uniformly using SHA-256 of a fixed seed plus UID, then adds every
exactly named Kai Tak Stadium form as a separate control. Controls do not increase
the random-sample denominator. This samples source forms, including small sheds
and roof structures; it is not weighted by visibility, population or landmark value.

```sh
python source-scripts/city/enhancement-screening/pilot.py --capture
python source-scripts/city/enhancement-screening/pilot.py
python -m unittest discover -s source-scripts/city/enhancement-screening -v
```

Use the shared-modelling Python dependencies and existing pinned `.env.modelling`.
Capture rebuilds current screening and audit fingerprints, checks shared decisions
against the local proof, reuses exact audit-cache hits, and computes only missing
sample audits. Cached native outcomes are read from the explicit completed HKS-222
run. No database writes, model downloads, conversion, AI API calls or new acceptance
occur. The existing statistics generator also rewrites the derived statistics file;
with unchanged inputs its contents remain identical. Without `--capture`, the script
replays committed compressed evidence entirely offline. `--count`, `--seed`,
`--evidence` and `--out` support other explicitly bounded experiments.

The initial **pilot-triage-v1** rule separates:

- **Confirmed skip:** existing current acceptance; explicit rework takes precedence.
- **Likely skip:** unassessed ordinary footprint form, one ring, surveyed height,
  Tower structure, at most 60 m high and 1,500 m², and no source/terrain audit flags.
  Exactly one prepared native match must have the same CSUID and recorded heights,
  cached footprint overlap at least 90%, cached centroid distance at most 2 m,
  current bounding-box edges within 2 m, base/top differences within 1.5 m, and at
  most 64 triangles. All gates must pass. This is a conservative *candidate for
  visual calibration*, not proof that the model looks sufficient.
- **Enhancement candidate:** a registry landmark or distinctive-use form (including
  grandstands/stadiums) rendered only as a footprint, or an existing rework decision.
  This is a review priority, not an automatic modelling job.
- **Review:** all other forms. Missing native coverage, estimated heights and
  terrain flags are unknowns, not evidence that enhancement is required.

The report also shows sensitivity at 128/256 triangles without changing the default
64-triangle rule. These thresholds are exploratory, not validated perceptual
standards. Native hull overlap/centroid metrics belong to the frozen source stage;
current identity, heights and bounds are checked, but polygon equivalence and native
terrain diagnostics are not reaccepted. Mesh complexity, a matched bounding box and
clean metadata cannot establish roof/facade similarity or current real-world fidelity.
Sampled terrain flags can describe legitimate elevated/support components.

Evidence, all 1,000 decisions with reasons, the separate stadium result and measured
times live under `docs/astra-city/enhancement-screening/pilot-1000/`. New public
`good-to-go` decisions still require the normal evidenced, reserved recording flow.

## Shape comparison pilot (HKS-203; current workflow)

Use `screen.py compare` for the new geometry-based diagnostic pass. The earlier
triangle-ceiling pilot remains reproducible historical evidence, not a quality gate.
AI is permitted for code and other non-modelling work only. All routine capture,
recovery, comparison, routing and caching make zero AI calls. A case that would
require AI modelling/architectural judgement stays pending and must be reported to
the user before that work begins; there is no automatic per-building AI fallback.

Install `shape-requirements.txt` into the existing modelling virtual environment.
The complete, bounded workflow is:

```sh
python pilot.py --capture --evidence local/shape-inputs.json.gz --out local/shape-metadata
python shape_prepare.py --allow-source-download --env-file /path/to/private.env
node shape_geometry.mjs local/shapes/geometry-inputs.json local/shapes/geometry
python screen.py compare --shared-cache
python shape_controls.py
python shape_evidence.py
```

Run these commands from this directory, or use their repository-relative paths.
Source recovery first reuses checksum-verified local assets, then exact prepared
R2 bundles when configured. Original government recovery is explicitly opt-in;
it reuses the existing bounded ZIP downloader and packer and must reproduce the
pinned native-stage asset SHA. Changed sources cannot silently substitute new
geometry. No data is published. Up to eight per-sheet processing threads are
supported; they are ordinary CPU/network workers, not AI agents.

The City geometry builder and official model loader export both representations.
Comparisons use one common world frame, 17 orthographic views (including the roof),
and two object screen scales, 96 and 192 pixels. They measure silhouette mismatch,
visible depth changes, roof depth and bounds. Triangle count is only a runtime
budget input, never the quality classifier. A separate rigid-offset diagnostic
identifies equivalent shapes at different positions without moving the sources.
The current City terrain sampler checks every low-rim triangle vertex.

Routes are `skip` (current existing acceptance), `keep-current-candidate`,
`import-candidate`, and `retain-pending`. Candidate routes additionally check
source identity/heights, matching, terrain diagnostics and individual mobile
resource limits. Passing an individual budget is not a dense-scene FPS guarantee.
A support/terrain diagnostic is not a certificate of placement or a reason to
lower surveyed geometry. Known landmarks cannot earn new adequacy credit solely
from negligible geometry differences.

**Automatic acceptance remains disabled.** Fixed-view similarity cannot establish
current real-world accuracy, material/facade quality, assembly completeness or
human-perceived importance. The fixture tests and prior Kai Tak positive control
validate code behaviour; they do not establish a citywide false-skip rate. These
outputs never enqueue modelling, write screening/model-review acceptance or invoke
the publisher. Existing `screen.py record` and the guarded publisher remain the
only acceptance/publication paths, with fresh evidence and source ownership.
No user building-by-building decision is requested by this diagnostic pass.

Metrics reuse the existing immutable Neon `city_audit_cache` under a distinct
`shape-comparison-v1` hash namespace; existing territory audit membership/results
are unchanged. Cache keys include the current source/context input hash, exact
exported geometry hash, comparison policy and engine code. Result hashes detect
corruption; conflicting immutable writes fail. Local-only runs and frozen replay
are explicitly non-authoritative.

`--shared-cache` also saves **every sample and control outcome**, including missing
geometry and other pending cases, into `astra_modelling.shape_screening_runs` and
`shape_screening_outcomes`. The additive `shape-schema.sql` migration is applied
transactionally on the pinned modelling branch. Run fingerprints include inputs,
comparison/routing code, policy, sample/control membership and complete outcome
hashes. Retries are idempotent; a separate post-commit connection verifies every
stored result and membership before `neon-sync.json` reports success. JSONB numeric
normalisation is accounted for in hashes. These tables grant no acceptance credit
and never update the enhancement progress ledger.

For another nonoverlapping sample, use frozen earlier evidence as an exclusion:

```sh
python pilot.py --capture --capture-only --count 5000 \
  --seed hks-screening-shape-5000-v1 \
  --exclude-evidence ../../../docs/astra-city/enhancement-screening/shape-pilot-1000/inputs.json.gz \
  --evidence local/shape-5000/inputs.json.gz --local local/shape-5000/capture
python shape_batch.py --evidence local/shape-5000/inputs.json.gz \
  --out local/shape-5000 --cache local/shapes --allow-source-download --workers 8
python screen.py compare --evidence local/shape-5000/inputs.json.gz \
  --geometry local/shape-5000/geometry \
  --out ../../../docs/astra-city/enhancement-screening/shape-pilot-5000 --shared-cache
```

`--exclude-evidence` can be repeated. Kai Tak is always a separate control, outside
the sample denominator. `shape_batch.py` shares the existing exact-asset cache and
uses sequential source leases of at most 1,000 forms; complete recovery and export
failures are retained in the geometry index. A partial compact ZIP is expanded by
reusing its verified members and downloading only newly requested members.

Historical complete reports can be synced without repeating comparison:
`python shape_store.py --evidence REPORT/inputs.json.gz --report REPORT`.
For a historical summary without `routingSHA256`, pass `--routing-source` pointing
to the exact version of `shape_screen.py` that produced it. Do not substitute a
newer routing implementation. Failure leaves no partial run committed.

Evidence and offline replay instructions:
`docs/astra-city/enhancement-screening/shape-pilot-1000/README.md`.
