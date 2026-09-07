# HKS-210 · Triangle mesh inspection

Implemented by the Codex implementation subagent on 7 September 2026 in the existing Astra City worktree. No reference images were used or modified. Inspection uses the loaded Lands Department terrain, existing source building geometry and bridge layers. Source coordinates and HKPD elevations remain unchanged at 1× scale.

## Controls and coverage

Places → Inspect the mesh offers Solid (default/off), Overlay and Wireframe, with independent Terrain and Structures targets. Overlay skin opacity ranges from 0–100%; other modes disable the slider. Settings are session-only and reload defaults to Solid. Existing layer visibility remains authoritative.

Inspection focuses on a circle around the view centre. The control reports its actual radius and triangle count, and explains that outside the circle stays solid. Desktop starts with a 700 m maximum radius and an 18,000-triangle budget; mobile uses 350 m and 7,000 triangles. Dense geometry automatically shrinks the circle. Every actual triangle intersecting the resulting circle is retained; no arbitrary faces are dropped inside it. Move the view centre to inspect elsewhere. This bound is required because unrestricted wire rendering measured about 6 fps in the existing Central overview.

Terrain covers the coarse mesh, recursive detailed patches and terrain hydro cut/bank/bed meshes. Structures covers base extrusions, asynchronously attached government models, bridge model/proxy decks and canopies, instanced rails and illustrative cables. Wires include coplanar triangle diagonals. Water, streets, trees, local-detail surfaces, vehicles and labels remain in their normal styles and are explicitly excluded in the UI. No geometry is lifted, exploded, rescaled or displaced.

## Rendering and lifecycle

`city/mesh-inspection.js` receives explicit registrations on terrain creation, building tile/replacement attachment, government-model attachment, bridge tile build and cable attachment. Root removal unregisters synchronously; bridge/cable disposal unregisters before source resources are freed. Solid performs no triangle selection and creates no derived inspection resources.

`city/inspection-region.js` conservatively selects source triangles by their transformed XZ bounds. It considers only source roots whose spatial bounds intersect the maximum circle, ranks candidate bounds by distance, and shrinks the radius before constructing geometry. The wire fragment shader clips the conservative subset at the exact circle boundary. It does not simplify, invent edges or construct a whole-territory barycentric mesh.

Only selected positions and source triangle indices are copied into a bounded indexed wire buffer; material groups and native local transforms remain intact. Source vertex and face-offset mappings are retained for verification. Instanced rails borrow their original box geometry and copy only selected instance matrices. Overlay objects cannot intercept picking or cast duplicate shadows. Skin/wire materials are shared per source material and target, reference-counted and released with derived geometry/instance buffers on Solid, region replacement or eviction. Source buffers and textures remain owned by their existing layers.

Skin shaders fade only within the same circle, so distant portions of a merged building tile remain solid. Hidden faces stay depth-occluded. Zero-opacity fragments write logarithmic depth before returning without facade shading; other fragments retain the original facade and texture shader. Source shader callbacks and live clock uniforms remain attached. Wires render after their skins in the matching opaque/transparent queue. Source shadow silhouettes, picking faces, visibility, LOD, walking/collision data and all transforms remain unchanged. Wire colours switch to a lighter palette only at the clock’s day/night threshold.

Planning runs on the existing 600 ms cadence, using the explicit registry rather than whole-scene traversal. Triangle subsets rebuild only after meaningful focus movement, changed targets, arrivals/removals or visibility changes. Opacity and palette changes reuse existing subsets. This can incur a short CPU planning cost when moving through dense geometry; it does not scan triangle geometry every frame.

## Verification

Command: `node --test 3d-viewer/city/tests/*.test.js`, Node 24.17.0. Result: 244 tests passed, 0 failures (229 existing + 15 inspection tests).

Focused tests verify exact source positions, triangle topology and material-group mapping; adaptive hard budgets; source/instance transforms; depth and render queue ordering; logarithmic depth before zero-opacity return; far-source appearance; original shader/texture retention; live night uniforms; original material restoration; picking face stability; late arrivals; government replacement/fallback bakes; bridge LOD; and derived-resource eviction.

Implementation-agent smoke benchmark in actual headless Chrome at Central (50 frames, first 11 omitted, DPR 1):

| Viewport | Solid median | Overlay median | Wireframe median | Selected triangles | Radius |
|---|---:|---:|---:|---:|---:|
| 1440 × 1000 | 16.7 ms | 33.3 ms | 33.3 ms | 17,998 | 198 m |
| 390 × 844 | 16.7 ms | 16.7 ms | 16.7 ms | 6,998 | 125 m |

No application or shader errors occurred. Solid returned to its original draw count (desktop 227; mobile 156) and zero derived material pairs. Full independent browser acceptance, including detailed models/bridges/night, is recorded separately by the parent agent. Mobile results emulate a phone viewport in desktop Chrome; physical-phone performance is not measured.

Debug state: `window.__city.state.inspection` exposes mode, opacity, targets, mesh/overlay/material counts and `scope` with radius, triangles, budget, maximum radius and focus. Controls: `#mesh-inspection`, `input[name="mesh-mode"]`, `#mesh-terrain`, `#mesh-structures`, `#mesh-opacity`, `#mesh-status` and `#mesh-scope-status`.

## Independent acceptance

Root actual-browser run passed all 15 recorded views: Central Solid/Overlay/Wireframe and per-layer targets; detailed Court of Final Appeal source picking/collision, day/night and restoration; live travel to Mui Wo; eight repeated release cycles; bridge loading; and 390 px controls with keyboard opacity adjustment and no horizontal overflow. Every sampled subset vertex and triangle maps exactly to its source, every selected instance preserves its matrix, and every budget is respected. Solid restores original material references and zero inspection overlays/material pairs. No application or shader errors.

| View | Median frame time | p95 |
|---|---:|---:|
| central-solid | 33.3 ms | 33.4 ms |
| central-overlay | 33.3 ms | 33.4 ms |
| central-wireframe | 33.3 ms | 33.4 ms |
| central-structures | 33.3 ms | 33.4 ms |
| central-terrain | 33.3 ms | 33.4 ms |
| detailed-court-wireframe | 16.7 ms | 33.4 ms |
| detailed-court-night-wireframe | 16.7 ms | 49.9 ms |
| detailed-court-night-restored | 16.7 ms | 16.8 ms |
| muiwo-streamed-wireframe | 16.7 ms | 33.4 ms |
| muiwo-restored | 16.7 ms | 16.7 ms |
| bridge-wireframe | 16.7 ms | 16.7 ms |
| bridge-restored | 16.7 ms | 16.7 ms |
| mobile-wireframe | 16.7 ms | 16.8 ms |
| mobile-restored | 16.7 ms | 16.7 ms |

Evidence: `browser.json`, corresponding PNGs and reproducible `3d-viewer/city/tests/wireframe-browser.mjs`. The earlier failed performance design is retained in `full-scope-browser.json`; it is not the shipped implementation. Early Central measurements overlapped a CPU test run (Solid also measured33.3ms); later scenes were measured after it exited. Frame rates depend on device and scene; this is desktop Chrome, not physical mobile hardware. Direct collision/picking and unchanged source data were checked; this focused run does not claim full gameplay, physical-phone or whole-city regional acceptance.
