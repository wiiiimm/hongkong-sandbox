# HKS-214 — grounded native source-part framing review

Codex Astra (`modelling_reservations` subagent) reviewed all 24 prepared parts. The result is **24 native source parts approved for integration**, totalling 975,981 compressed bytes and 44,968 triangles. This directory is staging evidence, not proof of runtime publication or R2 upload. No whole landmark or region is marked complete.

The corrected pass contains 48 screenshots: one normal scene and one labelled isolated native-model/terrain view per source UID. All 48 contain the complete model bounds, all 24 isolated views pass visibility checks, and 23 normal views pass. Pedder Building remains mostly obstructed by its neighbours in normal context (4 of 21 representative source rays); its isolated native view is clear. All eight contact sheets were inspected. The first attempt exposed clipped tall-building crowns; camera distance was corrected using the actual field of view and bounding radius, then all 24 captures were repeated.

`visual-acceptance.json` records the decision, precise component scope and image hashes for each part. Several names refer to a podium or small ancillary component, including The Centre, Sun Hung Kai Centre, Cadogan, AIA Kowloon Tower, Langham Place Hotel and 39 Conduit Road. Their parent towers or campuses are not approved by this review. Proposed landmark memberships remain proposals. Pedder's source roof reaches 54.080 m HKPD while its footprint's recorded top is 43.8 m; the native bytes remain unchanged and this review does not certify storey counts or surveyed facade accuracy. Procedural window spacing is illustrative.

The normal views use the actual viewer, its native loader and existing terrain. Isolated views hide unrelated building meshes while retaining native source geometry and terrain; other context such as roads and bridges may remain. Camera placement tests occupancy, terrain clearance, 21 actual source-triangle centre rays and all eight projected bounding-box corners, then settles and rechecks before capture. Visibility samples aid review but do not independently prove architectural fidelity.

Existing CPU and browser checks are reused from `grounded-model-review` and `landmark-preflight`: no sampled CPU terrain concerns for these 24 parts, and before/after verification passes with active native models and exact source picking. This pass fills the previously inadequate visual framing evidence. Model coordinates, native geometry and vertical scale remain unchanged at 1×. It introduces no terrain patch, runtime change, database review entry or deployment.

`inputs.json` records the baseline manifest and pre-road `world.js` hash (source commit `08a14ce416ac8dc08c65cd0c6c63aac2888cb5ba`). Cultural catalogue additions and road draping changed concurrently after the capture page loaded. These do not change the reviewed native source bytes; a separate representative check of the final installed manifest and road implementation is still required.

From the Astra worktree, with the documented Python/Node environments and local viewer on port 4176:

```sh
node source-scripts/city/grounded-framing-review/browser.mjs
node source-scripts/city/grounded-framing-review/contact.mjs
python source-scripts/city/grounded-framing-review/verify.py
python source-scripts/city/grounded-framing-review/prepare_publication.py --lease-file /path/to/current-source-reservation.json
```

Capture commands should run through the shared reservation supervisor. Claim all exact `building:landsd/OBJECTID:PART` keys in the selection before work, and release after it. `prepare_publication.py` verifies current ownership, reviewed input/image hashes, CPU/browser evidence, asset checksums and absent installed UIDs before writing only the adjacent `approved/` catalogue/assets, plan and guard. Approval decisions are explicitly authored, not inferred from a passing script. If captures are regenerated, review them again and refresh the decision hashes deliberately.

Validation: `verify.py` passed 24 unique parts and 48 checksum-matched, fully framed captures, with 23 clear normal scenes and 24 clear isolated views. Publication preparation passed with all 24 source assets checksum-matched; there are no held source parts. Root must verify `guard.json`, apply the existing integration publisher, and separately record the installed-state check. Proposed identities, photoreal facades, complete landmarks, R2 publication and regional acceptance remain outside this approval.
