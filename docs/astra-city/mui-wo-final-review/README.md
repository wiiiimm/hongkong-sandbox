# Mui Wo final terrain review · HKS-192

This is a **staged source checkpoint**, not a published change or whole-section completion. The exact 13 partial roof/terrain flags from the [integrated Mui Wo pass](../mui-wo-completion/README.md) were checked against original Lands Department TIN triangles. Six are derived terrain artefacts that the staged package resolves. Seven still occur against the source terrain and remain explicit review items. Section **10.6 remains Under review**.

No live terrain, building tile, model, manifest or shared renderer is changed here. The existing 2,408 Mui Wo forms, 1,327 Mui Wo detailed models and territory totals remain untouched. Complete nested rendering and actual browser acceptance are pending.

## Six supported corrections

The staged file contains five disjoint 1 m grids, **17,445 vertices / 211,294 bytes**, nested within the existing Mui Wo 5 m terrain. Four cases are caused by interpolating a coarse grid across locally steep original triangles; two are caused by the old source-union edge blend beside sheet 10-SW-8C. All six highest-roof flags clear with the original building heights held fixed.

| Building UID | Cause | Previous terrain maximum | Staged maximum | Existing highest roof |
| --- | --- | ---: | ---: | ---: |
| landsd/174150:0 · YICK YUEN | 5 m interpolation | 28.387 | 27.688 | 28.219 |
| landsd/195964:0 · HOI SHAN YUEN | 5 m interpolation | 9.967 | 9.755 | 9.700 |
| landsd/206484:0 · detailed model | 5 m interpolation | 68.777 | 68.647 | 68.569 |
| landsd/336510:0 | 5 m interpolation | 19.180 | 18.332 | 18.976 |
| landsd/201705:0 | exterior source blend | 88.966 | 82.330 | 85.400 |
| landsd/206970:0 | exterior source blend | 86.617 | 80.212 | 84.900 |

Elevations are metres HKPD. The existing diagnostic tolerates 0.1 m. These compare the highest roof against terrain over its source outline; they do **not** certify every individual sloping roof face. In particular, detailed model B177191330201063C0 retains its original 68.569 m model top and the separate 78.1 m recorded outline top.

One-metre spacing is a **sampling interval, not surveyed accuracy**. Raw native samples are retained separately. Display grids use their original barycentric TIN values inside the core and an explicit outer transition back to the unchanged parent. Bounds snap to parent 5 m cells. The coastal HOI SHAN YUEN grid is limited to dry ground; no water polygon, submerged bed or original source elevation is changed.

Two neighbouring temporary structures also depend on the old erroneous ground estimate. They have **null official base/top fields, no detailed model, and an existing 3.5 m estimated height**. Applying only the terrain would leave their estimated bases 6.175 m and 4.915 m above the highest ground. The companion [estimate-update payload](../../../source-scripts/city/mui-wo-final-review/building-estimate-updates.json) recomputes their derived bases from the corrected footprint minimum:

| UID | Old estimated base | Staged estimated base | Retained estimated height |
| --- | ---: | ---: | ---: |
| landsd/173217:0 | 83.834 | 76.601 | 3.5 |
| landsd/173237:0 | 81.836 | 74.932 | 3.5 |

These two dependent updates must be applied with the terrain, after checking the original UID, previous base, null source fields and absence of a model. Their original footprints, identifiers, null government values and fallback heights remain intact.

## Seven unresolved source cases

The remaining cases are not fixed by moving a recorded roof or carving ground to fit a building. Five have missing source heights; two retain recorded vertical values. The table reports original TIN height above the existing highest roof, not a claimed construction error.

| UID | Source structure / missing evidence | Maximum excess | Source-ground area above roof + 0.1 m |
| --- | --- | ---: | ---: |
| landsd/108665:0 · YEE YUEN | Temporary; both heights null, 2014 record | 3.652 m | 61.680 m² |
| landsd/163005:0 | Open-sided; both heights null, 2019 record | 0.949 m | 12.981 m² |
| landsd/172595:0 | Temporary; both heights null, 2010 record | 0.321 m | 0.506 m² |
| landsd/226308:0 | Open-sided; both heights null, 2019 record | 1.488 m | 29.316 m² |
| landsd/260075:0 | Open-sided; both heights null, 2019 record | 1.029 m | 7.933 m² |
| landsd/261605:0 | Podium; recorded base 60.3 / top 63.1, 2019 record | 0.296 m | 106.591 m² |
| landsd/296494:0 | Temporary; recorded base 52.0 / top 54.6, April 2026 record | 1.005 m | 9.334 m² |

For the null-height cases, a supported roof-height or source-model reference is needed to replace the current estimate; terrain interpolation is not the cause. For the podium and recorded temporary structure, review the structure interpretation and source revision agreement before choosing any display correction. A podium overlapping terrain can have a different meaning from a buried occupied roof; this audit does not decide that without evidence.

The centre of 261605 lies approximately **410 m outside the project's approximate section 10.6 review polygon**, but inside the user's original Mui Wo acquisition envelope. It stays in this 13-case audit. Review sections are not administrative or surveyed settlement boundaries. The earlier centre-sample gap for 226308 was a per-sheet grid interpolation limitation: original adjoining triangles cover its outline, so it is not an omitted terrain source.

## Validation and integration hand-off

[Source audit](exact-source-audit.json) retains the 13 identities, original attributes, native triangle extrema, clipped above-roof areas, hashes and revisions. [Staging evidence](refinement-staging.json), [neighbour/seam checks](neighbour-seam-checks.json) and [runtime checks](runtime-checks.json) record:

- Six focused Python tests pass. All six target flags clear; **25 intersecting forms** produce no new whole/partial roof flags, and the two dependent estimated-base updates prevent new floating bases.
- **2,180 half-metre edge checks** agree with the old parent within 2.49 × 10⁻¹³ m. The actual existing individual mesh builder and nested sampler check all 17,445 vertices; maximum Float32 mesh discrepancy is 0.00000382 m.
- All **1,080 grid boundary nodes** match the parent sampler; no child-grid node intersects mapped water.
- The existing **4,136.85 m** public route passes actual `Navigation.update` forwards and backwards, **63,975 frames each**, one initialisation and zero route resets. This is a CPU replay, not a new browser or performance measurement.

Root integration must preserve parent raw elevation arrays and source buildings, add these children to the Mui Wo parent's `patches`, and teach the existing renderer to omit their parent cells and draw every child exactly once. The current chunking path drops nested metadata; sampler support alone does not complete rendering. Apply the two guarded estimate updates and six derived audit-flag updates together. Then verify actual coarse/child mesh seams, detailed-roof faces, picking, collisions and the same public route in the live viewer. No shared code or live data is altered by the scripts here.

## What remains before whole section 10.6 can be accepted

- **Ground and water:** integrate these corrections and inspect their actual rendered edges; resolve or explicitly accept each of the seven source limitations using appropriate structure evidence. Retain the mapped shoreline and labelled illustrative estuary bed.
- **Buildings:** inspect the detailed roof face affected here, retain the 13 previously unmatched source-model identities, and review representative village/waterfront fallbacks among the existing 1,081 footprint forms. Imported counts alone do not validate architecture.
- **Public connections:** retain the verified ferry–beach–Wang Tong–Pak Ngan Heung–Tai Tei Tong–Luk Tei Tong core and arrival link; record the remaining public branch routes included in the section's acceptance scope. Resolve the old/new Wang Tong component interpretation and keep estimated approaches labelled.
- **Exploration:** replay walking and arrivals after publication, inspect source-deck junctions and verify village/waterfront flight clearance against the final terrain.
- **Presentation:** capture final fixed-camera day/night and 390 px mobile exports, inspect actual roof/shoreline placement, and measure frame performance after nested terrain integration. Previous integrated browser evidence remains valid only for its recorded baseline.
- **Provenance:** preserve all official IDs, model geometry, recorded elevations, raw source grids and footprint types; record any accepted approximation and distinguish the acquisition envelope from section boundaries.

## Reproduction and provenance

Run from the Astra worktree, using the existing Python environment and retained original source caches:

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-final-review/audit.py
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-final-review/fetch_terrain.py
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-final-review/refine.py
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-final-review/verify.py
node source-scripts/city/mui-wo-final-review/runtime_checks.mjs
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-final-review/test_refinements.py
```

Only the adjoining **10-SW-8C** terrain is newly acquired: two unmodified glTF/bin members, zero buildings and no photographs. Source index revision: **11 May 2026 HKT**. Range transfer: **1,951,911 bytes**, versus the 19,482,837-byte full archive. The 1,874,467-byte compact cache hash is `dfb88f5647d39a35d05433996a4f3f84c3cfae43ce920c64be0de42b4faf81f0`; it is **not a full-archive hash**. [Download provenance](../../../source-scripts/city/mui-wo-final-review/sources/10-SW-8C/download.json) retains URL, ETag, ranges, CRCs and individual source hashes. Large source ZIP/raw terrain geometry remain ignored and reproducible through the existing downloader.

The refinement bundle SHA-256 is `0680395f9a50338a435889b48200c7eb41af7c7f8f7b5c9e00840b882f79ba6b`. Expected unchanged live-parent SHA-256 is `95e288a0ad14f8389ed4daaad0a7af8657251b2bc0af9f282233448fbcf06648`.

Produced by Codex/Astra. Sources: [Lands Department 3D mapping](https://www.landsd.gov.hk/en/survey-mapping/mapping/3d-mapping.html), retained official index/glTF metadata and the existing attributed source packages. Coordinates remain EPSG:2326, elevations HKPD. No archived Lantau reference image is modified or used as precise present-day geometry.
