# Original government import contract v1 — HKS-203

An unchanged original government mesh can be accepted as a verified source port
using scripts. No AI architectural review or reconstruction is required. This is
specific to exact source parts, not inferred whole buildings or complete landmarks.
The user delegated import routing and requires zero per-model AI work.

Required gates:

- Previous native decoder, source picking/collision and terrain checks passed.
- Exact current UID, CSUID, object ID and recorded source heights; one frozen native
  result, identical asset bytes/SHA and original 1× HKPD transforms. Current source
  and terrain input hashes still match immediately before publication.
- Cached source footprint overlap >=0.98 and centroid separation <=1 m. Registry
  landmark parts and existing held/unavailable/identity-unresolved reviews remain
  outside this narrow automatic path. Already installed parts are not repeated.
- Check **all source vertices and triangle centres**, plus lower-rim edges at <=1 m
  spacing against actual drawn terrain triangles. Require complete ground coverage;
  no inspected surface more than 0.5 m below terrain; at least one lower-rim contact
  within 0.1 m above ground; no lower-rim gap over 1 m. Sampler and drawn terrain must
  agree within 0.004 m. Source geometry and surveyed elevations are never moved.
- Fit the existing mobile per-model geometry/resident/triangle budget. Preserve
  normal visibility/distance streaming and fallback; no new quality/LOD promise.
- Every selected import passes the actual City desktop/mobile day/night checks:
  active UID, in-frustum object, source picking/collision, valid draw output, no
  shader/page errors, and failed-download fallback plus retry. Retain rendered
  evidence and verify the exported files. This is runtime verification; no AI
  judges architectural appearance or modelling quality.
- Hold live source reservations. Seed a new review snapshot that inherits prior
  identical source decisions, then use fenced approvals and the existing guarded
  publisher. Mark installed-verified only after installed browser checks pass.
  Refresh the review proof and progress statistics; verify Neon readback.

The 0.5 m burial allowance permits minor base/terrain mismatch; it does not certify
survey-level foundations. A failed contact test may be a valid supported or belowgrade
component, so it stays pending for additional scripted context checks. Mesh sampling
beyond vertices/centres/rim is not exhaustive triangle intersection certification.
No claim is made about complete architecture, materials, routes, dense-scene FPS,
physical-phone performance or regional completion.

`acceptance-policy.py` contains the numerical contract and failure reasons.
`acceptance-metrics.mjs` queries actual geometry, `stage-acceptance.py` checks source
proof/holds and stages the subset, and `integrate.py` verifies fresh evidence,
publishes under ownership and records installed results. Current tools are explicitly
bound to the first 200-form batch. Do not retarget them by editing IDs without a new
frozen batch/evidence set. Broad skip-screening remains retired.

## Supported original pairs — bounded Saxon second pass

The `original-government-supported-pair-v1` path keeps every direct-import gate
for the original podium, including source identity, current terrain, mobile budget
and prior holds. The original tower keeps the same source, identity, budget and
all-surface terrain gates. Its terrain-only lower-rim gap is resolved only when
**every** sampled lower-rim point is covered by the exact original podium triangles,
with a minimum gap between -0.1 and +0.1 m and a maximum gap <=1 m. Both current
source hashes are checked. No building is shifted or reconstructed. Install both
parts atomically, record the support dependency and verify both in staged/installed
browser scenes, including asset-failure fallback/retry.

A source-backed terrain patch may restrict native detail to the source bounds,
with a 10 m transition on parent triangle boundaries and unchanged parent heights
outside that band. It still must pass exact coverage, overlap, seam, water-mask,
source contact and neighbour checks. The default native-terrain builder is unchanged.

`unchanged_support.py` can explain a **ground-gap-only** warning for an elevated,
unchanged form using one unchanged solid fallback podium: top/base gap <=0.1 m,
footprint coverage >=99.99%, containment within 0.002 m, no native/changed/open-sided
support, and no terrain-regression warning on that support. Ambiguous or incomplete
matches stay blocked. This proves unchanged source-form support; it does not grant
whole-building architecture or structural-engineering certification. The ordinary
neighbour report is retained, with a separate hashed support proof.
