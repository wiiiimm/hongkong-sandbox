# HKS-193 — Central and the Wan Chai–Sheung Wan corridor

Astra/Kant prepared the source inventory, compact model loader and browser checks; root integrated the live catalogues and terrain. **37 exact government models now load progressively** across Central, the waterfront, Sheung Wan and Wan Chai. This includes the initial 16, the independently matched West Wing podium and 20 corridor models. Original IDs, measured heights, indexed source geometry and retained podium forms are preserved. Full source arrays remain offline.

The model runtime passes actual desktop and 390/320 px browser acceptance, including night shaders, original-source picking, collision, memory budgets and failed-download Retry. See [runtime details](RUNTIME-MODELS.md), [browser evidence](browser/README.md) and [corridor inventory](CORRIDOR-MODELS.md).

**HKS-193 remains in progress.** Live terrain intersects some low source geometry, particularly The Center and Blue House; source elevations were not moved to hide that disagreement. Full source-supported walking routes, stairs and bridge approaches remain unapproved. The [route-contact follow-up](contacts-README.md) records useful alternatives and remaining access gaps. Model availability alone does not complete sections 01.1–01.4 or 02.1–02.2.

## Retained initial source audit

The initial review-window baseline contained 3,265 building forms: 3,232 government components and 33 retained OSM forms, with no detailed Central models. The 20 m buffered source selection contains 3,327 government components. `baseline.json` and the immutable `baseline-buildings.json.gz` preserve the initial source IDs, geometry hashes and recorded heights.

The existing range downloader and model importer have processed 16 original Lands Department sheets. They produced 2,977 exact single-component model matches, with no ambiguous UID groups or duplicate matched groups. The offline expanded model collection is 892 MB; it must stay outside ordinary runtime city tiles. All original glTF/bin entries and per-entry hashes are retained separately.

[Compact model hand-off](COMPACT-MODELS.md) documents 16 individually loadable models, including 12 landmarks and four route-adjacent source matches. They total 304,336 source triangles, 7.67 MB compressed transfer and 33.69 MB decoded geometry. The packed-only catalogue is small; the complete 2,977-entry inventory is separate. All 16 assets passed the app's real vendored GLTFLoader, original expanded float-byte, source ID/height, material and coordinate checks. This was the initial CPU-only packing pass; subsequent runtime and browser evidence is linked above.

The now-published Central 5 m terrain uses the existing archival DTM/source-TIN mosaic and outer transition. All 2,436 perimeter probes agree with the existing rendered ground within 0.000001 m. Its larger source-sheet crop is documented in `terrain-crop.json`; the geographic review scope is unchanged. The published sampler uses this patch. Source placement and public-access disagreements remain explicit in the browser evidence; a successful terrain seam check does not resolve those local differences.

## Continuous route candidates and remaining checks

The official 3D pedestrian snapshot contains 13,026 native XYZ segments, all requested source IDs accounted for. The original dictionary v2.2 (December 2025), section 1.3, confirms HK1980/HKPD. Section 1.4 gives horizontal accuracy of ±1 m and vertical accuracy of ±2 m. This is not a surveyed bridge-floor specification. The snapshot, query provenance, dictionary, 109 linked access-time records and 125 detailed opening-time records are retained under `source-scripts/city/central-completion/`.

Candidates use source-enabled, certain outdoor bidirectional paths. They exclude service lanes, lifts, moving escalators and restricted or unresolved schedules. Explicit full-day source schedules are retained; a null schedule is not described as a guarantee of uninterrupted access. Exact native segment vertices and persistent PedestrianRouteIDs remain available alongside the city-coordinate route. No fabricated straight connectors are inserted between disconnected paths.

| Candidate | Source length | Source segments | Remaining review |
| --- | ---: | ---: | --- |
| Central core | 1,694.303 m | 155 | Harcourt Road Footbridge, 12 stair segments and three building contacts |
| Waterfront/IFC/piers/Tamar | 1,935.041 m | 110 | Four stair segments and three building contacts |
| SoHo/LKF | 1,234.842 m | 161 | 17 stair segments and one building contact |

The core bridge candidates are persistent source routes `250016975` and `250017331`, on Harcourt Road Footbridge. Actual source infrastructure deck triangles must be identified and validated. A line's height alone is not a walking-surface approval.

The preflight samples every source edge at intervals no longer than 1 m using the actual terrain sampler and current BuildingIndex. Median absolute ground-to-network height differences improve from 1.81 m to 0.37 m in the core, 0.51 m to 0.26 m on the waterfront, and 1.38 m to 0.26 m in SoHo. These comparisons retain the network's stated source accuracy. No sampled candidate centreline is wet in either terrain version. They are diagnostic point samples, **not** a continuous navigation or shoreline-clearance pass.

Remaining contact IDs are recorded precisely in `route-preflight.json`:

- Core: `landsd/98394:0` (Bank of China Building), `landsd/26576:0` (unnamed form), `landsd/3088:0` (City Hall High Block).
- Waterfront: `landsd/98226:0`, `landsd/70842:0`, `landsd/26195:0` (West Wing). These three lacked accepted exact detailed-model matches in the initial staging pass. The separate contact follow-up now matches the podium; the two canopy models remain unavailable.
- SoHo: `landsd/75683:0` (Hollywood House).

The first four matched contact models are included in the compact batch for geometric inspection. Buildings, original route vertices and collision rules have not been moved or suppressed to make these diagnostics pass. Resolve source clearance and stairs, then replay actual `Navigation.update` forward and reverse with the normal actor radius. Only then publish a `walkCentreline` and approve the route. The candidate JSON deliberately has no such field.

## Reproduction

Run from the Astra worktree. Downloads are cached; the scripts reuse shared importers rather than replacing them.

```sh
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/central-completion/fetch.py
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/central-completion/run.py select
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/central-completion/run.py build
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/central-completion/run.py terrain
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/central-completion/pedestrian_fetch.py
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/central-completion/pedestrian_access.py
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/central-completion/route_candidates.py
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/central-completion/route-candidates-test.py
node source-scripts/city/central-completion/route-preflight.mjs
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/central-completion/pack_models.py
node source-scripts/city/central-completion/compact-test.mjs
```

Three source-route tests and all 16 actual-loader asset checks passed. The preflight reports remaining contacts explicitly. These initial source checks are retained separately from the later live model/browser acceptance. Full-section and continuous-route completion have not been claimed.

Primary references: [Lands Department 3D mapping](https://www.landsd.gov.hk/en/survey-mapping/mapping/3d-mapping.html), [official 3D pedestrian metadata](https://portal.csdi.gov.hk/csdi-webpage/metadata/landsd_rcd_1637222018065_52265/html), [Transport Department escalator operation](https://www.td.gov.hk/en/transport_in_hong_kong/pedestrians/hillside_escalator/index.html). Detailed source URLs, revisions and hashes are retained in the adjacent manifests and request records.
