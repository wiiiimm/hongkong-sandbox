# Central route-contact follow-up — staged

This bounded HKS-193 follow-up investigates the seven contacts from the initial route preflight. It adds one reviewed exact model match and source-backed route alternatives. All work remains in `central-completion`; shared runtime, live tiles, the original route candidates and the first 16-model compact batch are unchanged. No browser/GPU was used.

## Findings

| Existing building UID | Cause found | Staged response |
| --- | --- | --- |
| `landsd/98394:0` — Bank of China Building | The initial Bank Street contact is inside the outline collision volume but clear of the actual source mesh. The source model has other nearby surfaces that a simple outline-only detour can hit. | Public-source alternative retains both constraints and uses a different Bank Street node, documented in the route comparison. |
| `landsd/26576:0` — unnamed Chater Garden form | The original source triangles also obstruct the sampled actor. | Alternative uses another connected public path. |
| `landsd/3088:0` — City Hall High Block | Actual source geometry obstructs the original frontage path. | Alternative uses another public frontage connection. |
| `landsd/98226:0` — open-sided canopy | The contact is an illustrative post. Both recorded source elevations are null; no exact model is present in the retained sheets. | Public route bypasses the post; no source roof or simulated support is erased. |
| `landsd/70842:0` — open-sided canopy | Same: an illustrative post, not a surveyed column position. | Public route bypasses the post. |
| `landsd/26195:0` — West Wing podium | A curved source model was incorrectly rejected by a convex-hull centroid screen. The initial contact is clear of actual source surfaces, but a later part of the original route intersects the source model. | Reviewed model staged separately. Route stops at the northern public approach; the original Tamar interior arrival remains unresolved. |
| `landsd/75683:0` — Hollywood House | Original mesh surfaces extend beyond the footprint and obstruct both the original path and the first outline-only alternative. | Final source alternative avoids those real surfaces as well. |

These distinctions are recorded in `contact-model-audit.json`, using the app's existing `modelSurfaceCollision` function and original source triangles. A surface-only check does not prove a safe replacement for a building's enclosed interior. No general collision exemption is proposed.

## Reviewed curved-podium match

`landsd/26195:0` / BuildingCSUID `3511615681P20110704` has exactly one source model with the same GeoRefNo: `B351161568102063C1`, sheet `11-SW-9C`.

The old convex-hull centroid differs from the official footprint centroid by **16.77 m**, beyond the importer's 10 m screen. A union of the original triangles' horizontal projections has centroid separation **3.28 m**, **95.64% overlap of the smaller footprint** and **80.32% intersection over union**. It passes the existing spatial thresholds using the actual concave model projection. The union is evidence only; it does not replace the official footprint or any source triangles.

`west-wing-match.json` retains source hashes, original attributes, both screens and the matching rationale. The separate `compact-followup/` catalogue contains one gzip-wrapped GLB: 46,918 original triangles, 1,401,324 compressed bytes, 5,593,944 decoded geometry bytes. The app's actual GLTFLoader reproduced original expanded float bytes, source materials, transforms and bounds. Recorded base/top remain **4.8/16 m HKPD**; the original model top remains **20.939 m HKPD**. Nothing is terrain-draped or height-corrected.

The initial 16-model catalogue and its 2,977-match inventory remain frozen. This is an additional explicitly reviewed match, not a silent change to the shared matching policy.

## Public-source alternatives

The existing route builder now accepts optional obstacle exclusions, leaving its default output unchanged. `contact-edge-audit.mjs` screens original source paths at intervals of at most 0.25 m against the current building volumes and five exact contact models, on both current and staged terrain. Planning uses a 0.58 m radius: the unchanged 0.55 m actor plus 0.03 m margin. It inspected 550,116 sample locations, excluding 1,661 obstructed source segments and 113 whole segments extending outside the review envelope. Source vertices are never clipped or moved.

`route-alternatives.json` preserves every selected original segment and its access attributes, identifies added/removed segments, records source-node changes and hashes the unchanged original routes.

| Alternative | Source length | Scope and limitation |
| --- | ---: | --- |
| Central core | 1,720.819 m | All visitor stops retained; +26.515 m overall. The Bank Street source stop moves about 32 m along the same street. Harcourt Road Footbridge and stairs still require surface validation. |
| Waterfront to Tamar northern approach | 2,011.974 m | City Hall, IFC, pier promenade and harbourfront retained. Ends at source point `[611.8424, 6.316, 539.5712]`; **does not reach the original Tamar Park arrival**. |
| SoHo/LKF | 1,361.700 m | Visitor stops retained; +126.858 m. Avoids Hollywood House's real source overhang. Stair presentation and continuous walking still need checking. |

A second audit uses the normal 0.55 m actor against the alternatives at at most 0.25 m intervals. Across **21,275 samples**, the existing building contact count is zero, and the five contact-model surface hit count is zero. This is a geometric route screen, **not a continuous Navigation.update pass**. Other detailed landmark models, elevated public floors, stairs, full actor/water-edge clearance and forward/reverse runtime walking still need integration checks.

The original Tamar arrival's disconnected source nodes are retained in `failures`, and the northern approach explicitly carries `unresolvedDestination`. The route is not labelled complete by quietly dropping that destination.

## Reproduction and checks

From the Astra worktree, after the initial source/asset staging:

```sh
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/central-completion/west_wing_match.py
node source-scripts/city/central-completion/compact-test.mjs compact-followup
node source-scripts/city/central-completion/contact-edge-audit.mjs
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/central-completion/route_alternatives.py
node source-scripts/city/central-completion/contact-model-audit.mjs
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/central-completion/contact_tests.py
```

Eight focused tests pass: exact source vertices/attributes and public-access constraints, explicit bridge gaps, unchanged original route hashes, excluded obstacle segments, unresolved Tamar access, fresh geometric audit results and retained podium identity/heights. The separate actual-loader check passes for the podium model. Source URLs and hashes are retained in the evidence JSON; no new source geometry was invented.
