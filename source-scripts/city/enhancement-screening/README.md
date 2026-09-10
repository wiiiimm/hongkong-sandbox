# Acceptance reuse and import routing — HKS-220 / HKS-203 / HKS-199

Full skip-screening was removed from the active pipeline on 11 September 2026.
The retained planner performs existing acceptance and input-hash checks; it does
not run metadata/shape comparisons or require a new good-enough assessment before
source preparation. `screen.py` exposes only `migrate`, `export`, `plan`, `record`.

Normal route: skip unchanged verified forms; otherwise reuse cached original
government geometry, validate identity/components, placement/support and runtime
limits, then use the existing acceptance and guarded publication flow. Keep the
current fallback and queue scripted investigation when a source/check is unresolved.
An `enhancement-required` event is not a prerequisite for mechanical preparation.

Government-model handling uses local scripts with **zero per-model AI calls**.
Downloads and Neon/R2 syncing remain ordinary data transfers. Do not add an AI
fallback, generation, simplification or architectural-review loop. Cases requiring
AI judgement remain pending and must be reported before that work begins.

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
`assess.json.gz`, and `summary.json`. `assess` means no current acceptance: these
forms can proceed to local source lookup and import validation without full
comparison screening. Do not feed this partition into an AI modelling queue.
The planner does not alter historical jobs or enqueue new jobs. Use its partition
before creating a bounded enhancement batch, then recheck after reserving the
selected source keys. Keep required podium/support components even when their own
optional enhancement is skipped. The plan is a snapshot, not a queue lock.

`plan --offline` previews committed proof without credentials. Its outputs are
explicitly non-authoritative; do not schedule work from them.

## Existing acceptance and future decisions

The active workflow reuses current verified decisions. New source-backed import
acceptance still needs evidence and the existing ownership/publication checks;
neither a successful download nor a clean diagnostic alone grants approval.
There is no automatic new good-to-go rule in the pipeline. Historical comparison
candidates remain unaccepted. The ledger can still record separately justified
acceptance/rework decisions; per-building AI adequacy review is outside the current
user-authorised scope.

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

## Retained optional diagnostics

The full metadata and shape pilots are historical experiments. Their scripts,
frozen reports and all Neon diagnostic records remain available for targeted
debugging or regression replay, outside the active import pipeline. They never
grant acceptance or schedule work. See [DIAGNOSTICS.md](DIAGNOSTICS.md) only when
that diagnostic work is specifically needed; do not run another broad sample as
an enhancement prerequisite.
