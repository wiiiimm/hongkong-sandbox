# Tai O detailed models · HKS-170

Astra added **532 verified government building models** to the central Tai O waterfront, using the existing Mui Wo downloader, glTF converter, source matching, terrain resampler, tile publisher and city renderer. This is a bounded two-sheet implementation; complete stilt-village channels, decks and walking routes remain separate work.

| Official sheet | HK1980 extent, metres | Revision, Hong Kong date | Building models | Verified replacements |
|---|---|---|---:|---:|
| 9-SW-23A | E803000–803750, N812600–813200 | 11 May 2026 | 100 | 100 |
| 9-SW-23B | E803750–804500, N812600–813200 | 11 May 2026 | 435 | 432 |
| **Total** | **1,500 × 600 m source coverage** | | **535** | **532** |

The import keeps whole source footprints selected within a 35 m margin around those sheets. All **1,030 selected existing forms** remain; **498 retain outline-based fallback geometry**. The matched source models contribute **51,207 triangles / 153,621 vertices**. Three models fail the conservative matching screen; no duplicate or ambiguous source model groups were accepted. Five non-building infrastructure models are recorded but excluded from this building/terrain slice. [Full model accounting](build.json).

Across Hong Kong, the city retains **346,115 forms**, exactly **342,223 official source IDs / 342,225 official components**, and all **1,327 previous Mui Wo detailed models**. The new total is **1,859 detailed models**. Root independently compared every form against `9538e03`: every immutable footprint, source identity, recorded elevation and height classification is preserved; every existing `modelGeometry` object and every one of the 345,085 out-of-selection forms is unchanged. There are no duplicate extrusions. [Independent preservation evidence](independent-preservation.json).

Within the selection, 346 bases with **both original source elevations absent** were re-estimated from the finer terrain and remain labelled `terrain-estimated`. No recorded BaseHeight or TopHeight was raised or replaced. Existing foundation fields were preserved; this pass does not invent stilt supports or waterfront decks.

## Sources and exact placement

Source product: [Lands Department 3D Visualisation Map](https://www.landsd.gov.hk/en/survey-mapping/mapping/3d-mapping.html), [CSDI metadata](https://portal.csdi.gov.hk/csdi-webpage/metadata/landsd_rcd_1742809441342_98380/html) and [official sheet index](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0). The index response/request, original model entry hashes, revisions and download records are retained under `source-scripts/city/tai-o-models/`. Government data retain [CSDI terms](https://portal.csdi.gov.hk/csdi-webpage/doc/TNC); supplementary OSM paths retain OpenStreetMap/ODbL attribution. No archival Lantau reference image was used or altered.

Model node matrices produce `[E, HKPD height, -N]`. The sole city transformation is translation `[-834500, 0, 816500]`, with no extra rotation, scale or height offset. Matching reuses the exact GeoRefNo plus ≥50% overlap of the smaller projected footprint and ≤10 m centroid separation, followed by an unambiguous BuildingCSUID/component match. The matching subset comes from the retained official `Building_Outline_Public_v20260819` territory GeoJSON, projected from CRS84 to EPSG:2326; it is explicitly a derived matching input, not a newly surveyed native-coordinate snapshot. Live footprint vertices remain unchanged.

All 532 baked models pass comparison with original glTF transform bounds and triangle counts. Positions and normals are finite; no zero-normal vertices occur in this slice. Original material facts and source colours remain in the payload. The city palette, window layout and lighting schedules are illustrative. Model roof maximum and outline TopHeight differ by more than 2 m for **137** matches: both values remain intact, and the source card explicitly labels its number **OUTLINE HEIGHT**.

Only original glTF/bin entries were transferred using the government's normal HTTP 206 byte-range support. The two downloads transferred **4,036,048 bytes**, including archive directories, versus **75,207,259 bytes** for the two complete source ZIPs. Entry CRC/SHA-256, URL, ETag, Last-Modified and byte ranges are retained in `sources/*/download.json`. Compact derived ZIP hashes are distinguished from unavailable complete archive hashes, which are null. Raw caches and extracted geometry are ignored; no photographs are extracted or requested at runtime. The baked payload is **1,027,342 bytes gzip**, SHA-256 `208b32d4c3209f6ae864e89cbaa124054fb933459c7272369ccb4d24bf50e603`.

Unmatched source models are `B037601293201063C0`, `B037681292101063C0` and `B040251306201063C0`, all on 23B. None receives an automatic replacement or fabricated footprint. Their bounds and failure reasons are in [build.json](build.json).

## Terrain, seams and remaining conflicts

The existing archival Lands Department 5 m DTM is reused for a **393 × 197** patch, bounded by E802762.5–804722.5 / N812407.5–813387.5. The two actual source TINs contribute 36,000 sampled grid positions. **6,696 existing nonpositive DTM water nodes are excluded from land-detail blending**; the 29,304 remaining nodes form one union, blending only its exterior/holes over 15 m. The visualisation TIN contains water surfaces and cannot independently establish a shoreline. Original sampled source grids are retained, and source water is not turned into invented land. [Mosaic evidence](terrain-mosaic.json).

At 120 paired source-sheet edge samples, the maximum same-location TIN difference is **0.0878 m**, median **0.000057 m**, with none over 1 m. The source triangle probe permits only the existing 1 cm boundary tolerance. Of 532 model bounding-box centres, **531 intersect their own sheet TIN**, and none has its roof maximum below that TIN. `landsd/62330:0` / `B038481320201063C0` has centre `[-30652.53125,3299.71875]`, approximately **0.281 m north of its sheet edge**; the own-sheet check correctly returns no height rather than extrapolating. [Source audit](source-audit.json).

The outer patch initially revealed the existing water-clamp mismatch between coarse and subdivided terrain: raw heights agreed, but 67 boundary probes differed in displayed height, by up to 2.576 m. An optional `renderedElev` field now joins those actual rendered triangles within the outer 70 m transition only. Raw elevation values, vegetation and water classification are unchanged; source TINs and building elevations are unshifted. The same small helper supplies both terrain meshes and walking samples, including chunk boundaries. Patches without the optional field, including Mui Wo, retain their existing behaviour. Final patch SHA-256: `e19dfb6b9d2d90c5ab305a697827148da596b6ed1a444cb5cc8c3cb9ee95a166`.

The same rendered-triangle diagnostic compares the highest displayed roof against terrain extrema across each whole source footprint, with 0.1 m tolerance:

| Diagnostic, 1,030 selected forms | Before `9538e03` | After |
|---|---:|---:|
| Roof maximum below all footprint terrain | 96 | 1 |
| Roof maximum below some footprint terrain | 170 | 13 |
| Newly wholly buried forms | — | 0 |

The one wholly-below case is fallback `landsd/14899:0`: source roof 15.7 m HKPD versus terrain minimum 16.0 m. The 13 partial cases comprise two recorded-outline/terrain mismatches and 11 estimated-height fallbacks. **None of the 532 detailed model roof maxima falls below its footprint terrain extrema.** These are conservative source-conflict diagnostics, not per-roof-face visibility proof; they do not identify which source revision is correct. [Comparison](terrain-comparison.json), [final integration rows](integration.json). The final integration report records an idempotent second publication (`changedForms: 0`); the independent baseline comparison records the 1,030 changed forms.

Screenshots still show incomplete channels and coarse shoreline/land-cover shapes. Nearby visual path/plaza surfaces and vegetation are not a surveyed village reconstruction. This pass does not complete architectural QA, continuous accessible routes, stilt-deck structure or HKS-170's wider channel acceptance.

## Arrival and visual evidence

The more detailed collision volume invalidated only `taiopromenade`. It moved **14.318 m**, from `[-30796.6,3830.3]` to `[-30787.2,3819.5]`, along retained public [OSM way 1187601801](https://www.openstreetmap.org/way/1187601801), in `source-scripts/city/snapshots/outlying-west.json.gz`. The replacement passes dry-triangle, 1.2 m building-clearance and sampled 2 m path checks. The shared repairer now updates both regional package JSON and the generated destination module, then re-imports the published modules in a fresh process. **All 190 walking arrivals pass; six aerial destinations remain unchanged.** Main `taio` is unchanged. [Repair record](arrival-repairs/repairs.json), [idempotent verification](arrival-repairs/verification.json).

The actual city browser loads all 532 models through the normal tile stream. Real roof picking and source-card/collision checks pass for both sheets (`landsd/64563:0`, `landsd/240302:0`). Main Tai O walking entry moves 2.015 m without collision. Day/night and mobile runs produce no page or tile errors. Saved screenshots were visually inspected: sourced stepped roofs and terraces are visible, the night window layer works on those forms, mobile controls remain legible, and the channel limitations above remain apparent.

| Fixed 1440×1000 view | Before median / p95 | Final median / p95 | Before → final draw calls |
|---|---|---|---|
| Overview 15:00 | 16.6 / 16.9 ms | 16.7 / 17.5 ms | 78 → 80 |
| Overview 22:00 | 16.7 / 17.3 ms | 16.7 / 17.4 ms | 79 → 81 |
| Village 15:00 | 16.7 / 17.4 ms | 16.7 / 17.5 ms | 46 → 48 |
| Village 22:00 | 16.7 / 17.5 ms | 16.7 / 17.4 ms | 47 → 49 |

At **390×844**, a final daytime view measured median **16.7 ms**, p95 **17.6 ms**, 65 draw calls and 820,794 rendered triangles. Each measurement uses 120 animation frames after 20 warm-up frames. These are local desktop Chrome measurements, including a mobile-sized viewport; they do not claim physical-phone or production-network performance. [Before browser report](browser/before-verification.json), [final report](browser/after-verification.json).

- Overview: [before day](browser/before-overview-1500-1440x1000.png) · [after day](browser/after-overview-1500-1440x1000.png) · [before night](browser/before-overview-2200-1440x1000.png) · [after night](browser/after-overview-2200-1440x1000.png)
- Village: [before day](browser/before-village-1500-1440x1000.png) · [after day](browser/after-village-1500-1440x1000.png) · [before night](browser/before-village-2200-1440x1000.png) · [after night](browser/after-village-2200-1440x1000.png)
- [23A source card](browser/after-9-SW-23A-source-card-1440x1000.png) · [23B source card](browser/after-9-SW-23B-source-card-1440x1000.png) · [mobile](browser/after-mobile-1500-390x844.png)

## Reproduce and validate

Run from the authorised Astra worktree. Retained source selections are the reproducible inputs; `run.py select` can refresh the matching subset from current live forms and the retained territory source, if intentionally needed. Ordinary rebuilds reuse those selections and local geometry caches first. Never run the obsolete Mui Wo-only merge after territory publication.

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/tai-o-models/run.py fetch
/tmp/astra-city-venv/bin/python source-scripts/city/tai-o-models/run.py build
/tmp/astra-city-venv/bin/python source-scripts/city/tai-o-models/run.py terrain
/tmp/astra-city-venv/bin/python source-scripts/city/tai-o-models/run.py publish
CITY_NODE=/Users/williamli/.nvm/versions/node/v24.17.0/bin/node /tmp/astra-city-venv/bin/python source-scripts/city/tai-o-models/audit.py
/tmp/astra-city-venv/bin/python source-scripts/city/tai-o-models/test_models.py
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-models/test_models.py
/Users/williamli/.nvm/versions/node/v24.17.0/bin/node --test 3d-viewer/city/tests/tai-o-models.test.js
/Users/williamli/.nvm/versions/node/v24.17.0/bin/node 3d-viewer/city/tests/tai-o-models-browser.mjs after
```

[Validation accounting](validation.json) records the unchanged raw arrays and all 346 estimated-only base changes. Focused Python checks pass **5 Tai O + 3 existing Mui Wo tests**, including exact source transforms, cache provenance, mosaic/water behaviour and numeric-zero render overrides. The three focused Node tests exercise all 532 models, actual perimeter mesh vertices, raw-height continuity, the walking sampler and terrain chunk boundaries. Root's final full city suite passes **137/137**. Independent source/pipeline review checked preservation of Mui Wo defaults and identified no remaining blocker, including the generated-arrival repair and rendered transition. [Root’s final independent review](independent-review.json) records the full-suite and visual checks.

[Primary-agent test and visual review](independent-review.json).
