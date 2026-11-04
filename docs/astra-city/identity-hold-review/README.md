# Government identity holds — HKS-214

Executor: GPT-6 Astra, 9 September 2026 (Hong Kong). This pass resolves **five of nine acquired matching holds into native parts approved for integration**, with four required source-native terrain children and one retained surveyed-podium dependency. It stages a guarded subset; it does not publish buildings or certify complete landmark assemblies. The other four retain specific, measured holds. The eight non-government entries are classified as OSM façade parts of The Center, not eight missing government buildings.

[Decisions and hashes](decisions.json) · [Footprint/source audit](audit.json) · [Browser contact sheet](contact.html) · [CPU checks](cpu-validation.json) · [The Center comparison](center.json)

| Source UID | Integration result | Required dependency or retained limitation |
| --- | --- | --- |
| landsd/205478:0 — The Masterpiece | Native tower/annexe approved | Retain K11 surveyed podium UID256535; all66 low-rim vertices inside volume or within0.139m of actual wall surface |
| landsd/297401:0 — West Kowloon Station | Native curved roof approved | Native terrain child;11 lower foundation contacts remain2–2.334m underground, no wholly buried faces |
| landsd/314191:0 — Airport Terminal1 component | Native ribbed roof component approved | Native terrain child; six small vertical foundation triangles retained underground, no buried upward faces; not allTerminal1 |
| landsd/81387:0 — Langham hotel ancillary | Native access/railing part approved | Native terrain child restores buried lower geometry; office-tourist membership remains unapproved |
| landsd/93890:0 — Aigburth | Native tower/substructure approved | Native terrain child; retain tall hillside retaining walls below grade, no wholly buried faces |
| landsd/142159:0 — Queensway ancillary | Held: zero actual footprint overlap | Native reference/current footprint conflict |
| landsd/143421:0 — Flagstaff ancillary | Held: zero actual footprint overlap | Native reference/current footprint conflict |
| landsd/233905:0 — Champion podium | Held:57.47% actual footprint coverage | Full podium component assembly |
| landsd/235988:0 — Island Shangri-La podium | Held:37.22% actual footprint coverage | Remaining podium source geometry |

[Physical acceptance](physical-acceptance.json) · [Guard](guard.json) · [Terrain dependencies](approved-terrain.json) · [Supplemental inventory](supplemental-source-inventory.json)

## Source accounting

All nine exact GeoRefNo archive members are already downloaded, checksum-verified and retained. **None is a source-download absence.** A matching filename alone does not prove one-to-one BuildingCSUID correspondence. No global matcher thresholds or retained acquisition manifests were edited.

The fresh government query contains exactly nine records, has no transfer-limit flag, and confirms unchanged IDs and heights. Retained footprints match the live geometry to less than 0.0011 m Hausdorff distance except the station (0.159 m; 99.92% intersection over larger area). This is documented simplification/rounding/source comparison, not a claim of identical geometry bytes. The two zero-overlap cases remain conflicts against the current source footprint, rather than presumed stale local IDs.

The reusable audit decodes actual source node transforms using the existing decoder. It compares unions of indexed triangle projections, retaining concavity and holes, against source footprints; elevated tower slices separate tower identity from native low annexes. Projected area is identity evidence, not ground contact or structural support proof.

The Center's eight `way/13237323…` entries retain `part:true`, `material:glass`, `minimum:30` and parent `way/148228888`. They lack government CSUIDs because they are OSM components. The already installed native `landsd/67579:0` covers 89.75–100% of their projected areas. This supports treating them as component-overlap work, but does not establish equivalent geometry at every height or permit automatic deletion. No aliases or fabricated government keys were created.

## Prepared assets and browser evidence

The five new candidates total **92,011 triangles and 2,569,464 compressed bytes**. Existing packer checks retain expanded source attribute bits, node transforms and materials. Five actual loader/picking/collision CPU checks passed. Twenty-nine final normal-scene browser captures cover desktop before/after, 15:00/22:00, and 390×844 Chromium mobile emulation. Every intended after-view model was active and source picking returned its UID; the final run had zero browser errors, camera occupancy or horizontal UI overflow.

The subsequent physical pass adds20 final after-views covering all five models at15:00/22:00 on desktop and390×844 Chromium mobile emulation. All source UIDs are active, picking agrees, complete bounds fit the camera, and there are no browser errors, camera occupancy or horizontal overflow. Named inspected images and their hashes are recorded in [physical acceptance](physical-acceptance.json); this does not claim every automated image was manually inspected.

The physical review tests actual indexed source triangles and original surveyed fallback volumes against rendered terrain, rather than accepting a low-rim scalar screen alone. Masterpiece's66 contacts meet K11 volume/walls without moving geometry. Native terrain restores Langham's15 previously buried faces and Aigburth's46. Station's11 remaining lower contacts and Aigburth's tall retaining-wall bottoms lie below grade while their connected walls remain exposed; neither has a wholly buried face. Aigburth's final terrain sampler has30/34 low-rim points within2m, and a deepest29.864m below-grade wall corner; this is explicitly accepted as retained substructure after incident-face and clear NE-view inspection, not reported as a perfect contact test. Airport's six remaining buried triangles are three0.1506m-high vertical strips; no upward faces or sampled interior roofs are hidden. Original source coordinates and geometry remain unchanged at1×HKPD.

Four staged terrain children contain349,059 grid nodes, sampled from retained nativeTINs with unchanged parent boundaries and raw water masks. One-metre grid spacing is a sampling interval, not claimed survey accuracy. Airport required three adjacent source sheets, downloaded into this pass's private working cache; other terrain sources were reused. The guarded parent hashes must match before installation; root must check the final combined terrain and neighbouring buildings after integration. The patches' original diagnostic flags remain in evidence, alongside separate explicit physical acceptance, so exceptions are visible rather than silently reclassified as scalar passes.

Transport/access geometry uses `proceduralWindows:false` to avoid invented office windows on opaque roofs and open stairs. At night those non-textured native roofs remain dark; this pass does not add real glazing or terminal illumination. Residential lighting remains procedural. Langham's exact UID may be integrated while its old office-tourist grouping remains held. No universal walking route, whole-terminal, photoreal-material or real-device sustained-performance acceptance is claimed.

The earlier `identity-approved/` catalogue intentionally retains the identity-only stage. Final five-part `approved/` catalogue and guarded plan are emitted by `prepare_publication.py`; required terrain children are inseparable placement dependencies, and K11 fallback UID256535 must remain. The supplemental inventory hashes these five UID/asset pairs as snapshot`aa59f0309028012f`; it does not overwrite the previous459-part snapshot. Packed assets and raw terrain sources are ignored working material for the sharedR2 snapshot, not yet production assets. Root owns ledger recording, installation, final runtime checks and Linear.

## Reproduce

Run from the Astra worktree with the model-improvement skill's pinned Neon reservations for all nine canonical government keys. The Center comparison additionally reserves `building:landsd/67579:0`. Keep separate receipts; the OSM IDs do not have invented government reservation keys.

```sh
python source-scripts/city/identity-hold-review/audit.py
# Optional fresh HTTP snapshot; this never changes viewer/inventory:
python source-scripts/city/identity-hold-review/check_live_records.py
python source-scripts/city/identity-hold-review/audit.py
python source-scripts/city/identity-hold-review/center.py
python source-scripts/city/identity-hold-review/prepare.py
node source-scripts/city/building-batch/validate_candidates.mjs --candidates source-scripts/city/identity-hold-review/candidates --out docs/astra-city/identity-hold-review/cpu-validation.json
node source-scripts/city/identity-hold-review/browser.mjs
python source-scripts/city/identity-hold-review/accept_identities.py
node source-scripts/city/identity-hold-review/support.mjs
python source-scripts/city/identity-hold-review/native_terrain.py
python source-scripts/city/identity-hold-review/langham_terrain.py
node source-scripts/city/identity-hold-review/support.mjs --terrain-bundle docs/astra-city/identity-hold-review/terrain-patches.json --output docs/astra-city/identity-hold-review/support-with-terrain.json
node source-scripts/city/identity-hold-review/surfaces.mjs
node source-scripts/city/identity-hold-review/browser_terrain.mjs
python source-scripts/city/identity-hold-review/prepare_publication.py
```

The acceptance JSON is a deliberate human/agent visual decision; a new source revision or changed evidence requires reinspection before regenerating its pinned hashes. `prepare_publication.py` rejects stale evidence, assets, terrain parents, screenshots and mismatched activity; it stages files only.

The scripts read SQLite in query-only mode. They do not alter source caches, shared databases, model-review ledgers, viewer assets or terrain. Native EPSG:2326/HKPD remains at 1×. Browser injection is confined to its private page context. `accept_identities.py` verifies input/asset/screenshot hashes, CPU results, live footprint continuity, expected view activity and explicit per-UID decisions before emitting the identity-only catalogue. A different source revision requires a new review.

## References

- [Lands Department building layer](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0): exact current IDs, geometry and heights; bounded [HTTP provenance](live-footprints-provenance.json).
- [Aedas — West Kowloon Station](https://www.aedas.com/en/project/hong-kong-west-kowloon-station/): project architect and curved station architecture.
- [Hong Kong Airport Authority photo gallery](https://www.hongkongairport.com/en/media-centre/gallery/photos.page): Terminal 1 exterior forms.
- [New World Development — The Masterpiece](https://propertysales.nwd.com.hk/property/masterpiece): residential component of K11, 18 Hanoi Road.
- [Cordis experiences](https://www.cordishotels.com/en/hong-kong/experience/cordis-experience/): separate office tower and hotel identities.
- [Langham Hospitality — Cordis Hong Kong](https://www.langhamhospitality.com/en-US/Investments/Cordis-Hong-Kong/): hotel/mall/MTR connection; not proof of this individual ancillary object's route.

## Pedder follow-up

[Pedder source audit](pedder-source.json) and [decision](pedder-decision.json) retain a specific height/architecture hold for landsd/69002:0. Fresh government data still reports5.5–43.8mHKPD; native roof surfaces cover almost the entire footprint above43.8m, with a broad47.885m roof and54.080m rooftop maximum. Native projection matches99.9966% of Pedder's footprint, while only1.82m² overlaps ChinaBuilding, so the evidence does not support reassignment to AnsonHouse. AMO/HKTB confirm nine storeys but provide no roof elevation resolving the source discrepancy. No scaling, clipping, source reassignment or new publication was performed. Reproduce with `python source-scripts/city/identity-hold-review/pedder_source.py`; add `--refresh` for a bounded new government response, then review changed evidence.
