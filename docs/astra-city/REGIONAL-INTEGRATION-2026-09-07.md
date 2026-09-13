# Astra city integration — 7 September 2026

The isolated `codex/astra-hong-kong-city` preview now combines the original date/location sky, source-based regional terrain and progressively loaded government models. No changes were merged or deployed.

## Completed implementation slices

| Slice | Commit | Evidence |
| --- | --- | --- |
| Original golden-hour palette, sun/moon date/HKT/location alignment and sun-driven shadows without the old low-sun clamp | `367cc1b` · HKS-119 | [Golden sky and shadow checks](golden-hour/README.md) |
| Weather haze/sky-glow control, fresh HKO visibility, separate EPD AQHI and manual override | `8e8a181` · HKS-195 | [Atmosphere](atmosphere/README.md) |
| Mui Wo source terrain, ten infrastructure models, mapped estuary and 4.137 km continuous public route | `9a33045` · HKS-192 | [Mui Wo](mui-wo-completion/README.md) |
| Bounded compact-model loader, exact UID replacement, source collision/picking and shared night lighting | `455761f` · HKS-193 | [Runtime contract](central-completion/RUNTIME-MODELS.md) |
| 17 Central and 20 additional Wan Chai–Sheung Wan models, source terrain and retained original archives | `80c42db` · HKS-193 | [37-model browser acceptance](central-completion/browser/README.md) |
| 681 Pui O models, 5 m terrain and labelled missing-base estimates | `7281071` · HKS-171 | [Pui O](pui-o-completion/README.md) |

The building inventory remains **346,115 forms**, including **342,223 government source IDs**. Existing **1,859 embedded detailed models** remain intact. Four new compact catalogues expose **718 unique additional building UIDs**, containing 534,791 source triangles and 13,117,045 compressed bytes. These are available-model totals, not simultaneous rendering counts or whole-region acceptance. Distance, visibility and separate mobile/desktop budgets govern loading.

## Bridge cluster and shared integration

Tsing Ma and Ting Kau use seven original government components, totalling 54,965 source triangles. Their 10,536 illustrative cable triangles remain separately labelled, with no walking access inferred. Exact source identity drives removal of seven ordinary tower extrusions and 21 fully covered proxies; two Tsing Yi approach tails remain.

The shared 5 m bridge terrain uses thirteen original source sheets. A browser-discovered foundation defect came from an old DTM water mask excluding newer source ground. The correction restores 1,435 scoped grid nodes from the retained TIN grids, preserving source meshes, mapped island shapes and water polygons. Whole-island source/triangle checks and final browser terrain rays passed. The −4 m water bed remains an illustrative rendering surface, not bathymetry. [Bridge evidence](ting-kau/README.md) and [foundation correction](ting-kau/foundations/README.md).

The shared registry preserves every existing terrain patch and compact catalogue. Composite hydro retains Tai O and Mui Wo; the bridge cluster keeps its own nested source-region bounds. The minimap recursively draws those leaf bounds, avoiding invented land between source extents. A regression covers the nested package and original drawing order.

Entering Walk/Fly now protects the requested arrival from orbit-camera streaming replans. Cancellation, another destination or returning to Orbit releases that protection. A selected building card and highlight follow its visible source model when loading finishes or a fallback returns.

## Validation and remaining work

The final city suite passes **226 tests**. The full 37-model corridor review, Pui O source/arrival/walking/flight/night/failure checks and two-bridge before/after review pass in actual Chrome. Narrow 320/390 px contexts exercise the mobile UI and model budgets. Typical measured median/p95 frames were 16.7/16.8 ms; this is desktop Chrome evidence, not physical-phone, sustained thermal or measured-heap certification. Exact per-run numbers and exported images are retained with each area.

HKS-193 remains open for source-ground intersections, entrances, continuous pedestrian routes, stairs and wider corridor detail. HKS-171 remains open for the inherited gridded shoreline, wetlands/channel semantics, inland connections and other south-Lantau villages. The Cheung Sha/Tong Fuk/Shui Hau [availability audit](south-lantau-audit/README.md) identifies 24 unique advertised source sheets without downloading their models again. Mui Wo's thirteen partial terrain conflicts and wider Tai O/private-stilt detail also remain explicit.

The numbered grid records **0 Ready, 0 Close, 12 Under review and 120 Base mapped**. A verified local route or model batch does not satisfy every gate across a whole section. [Current Linear execution tracker](EXECUTION-ISSUES.md).
