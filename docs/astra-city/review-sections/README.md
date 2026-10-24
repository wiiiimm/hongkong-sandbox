# Numbered Hong Kong review sections — HKS-194

GPT-6 Astra, 7 September 2026. Root: controls, renderer, readiness, integration and browser acceptance. Curie: reproducible section geography and independent topology checks. Implemented on the isolated `codex/astra-hong-kong-city` comparison branch.

## Use the overlay

Open `city.html`, select **#132** beside the view buttons, or enable **Places → Review sections · 132**. The layer defaults off and downloads its data only when first enabled. Click a numbered marker to open its matching checklist ID, name, readiness, remaining checks and Linear links. The selector includes every section even when labels overlap or lie off screen. **Show this section** fits its boundaries; **All Hong Kong** shows the full district coverage. Numbers thin out when zoomed out to keep them readable. Zoom in or use the selector to reach smaller areas.

The layer reuses the existing terrain sampler, controls, place arrivals, camera and rendering scene. It does not replace terrain or building data. Borders follow the terrain and remain visible through buildings as a debug aid. Labels avoid controls and one another, provide 44 px touch targets and support keyboard selection. Existing place labels return to their previous setting when the grid is disabled. Stargazing temporarily suppresses the grid. High overhead debug views scale the atmospheric fog for map legibility during rendering; the environment's manual/live weather values are restored unchanged after each frame.

## Geographic meaning

All 132 stable IDs match `SECTION-CHECKLIST.md`. The geometry partitions 18 retained Home Affairs Department district polygons, including their marine jurisdiction. Smaller section borders are inferred project review areas, **not official neighbourhood boundaries**. Explicit source island polygons prevent Soko/Po Toi and other groups being assigned solely to the nearest mainland anchor. Multipart areas and holes are retained.

The HAD service was retrieved on 7 September 2026. Its records expose a 2016 lifespan and no later revision field; this is not a claim that the boundaries are a new survey. Four existing saved-place anchors cross their assigned official district, and the retained Chek Lap Kok outline crosses into the source Tuen Mun boundary. Source coordinates and district borders remain unchanged; exceptions are recorded in [the geography notes](geography.md) and [audit](geography-audit.json). The UI identifies sections with those saved-place exceptions. No historical Lantau reference images were used or edited.

## Readiness and updates

Current section counts are **0 Ready, 0 Close to ready, 6 Under review, 126 Base mapped**. Under review: Central 01.1–01.3, Mui Wo 10.6, Tai O / north-west Lantau 10.10 and Ma Wan / bridge approaches 11.5. Tai O's verified village slice does not sign off the wider section. Staged Central, Mui Wo and Tsing Ma work cannot count as live acceptance.

Six gates cover ground/water; buildings/skyline; streets/public space; walking/flight; day/night/mobile; sources/review evidence. A gate is verified only with `state: verified`, `scope: section` and retained evidence. **Close to ready** requires at least four gates, including ground and buildings, with no known blockers. **Ready** requires all six and no blockers. This is an explicit project acceptance policy, not a percentage inferred from building totals.

`source-scripts/city/review-sections/build_readiness.py` owns the current evidence ledger and correct regional issue links. To record a completed section-wide review, update its checks/evidence and blockers in that publisher, regenerate `section-readiness.json`, run the tests and update the corresponding Linear leaf/parent/milestone. Readiness is a versioned snapshot, not a live Linear API feed. Do not change geographic IDs to update status; rebuild the boundary dataset only when inputs or the partition policy change.

## Verification

- 167 city unit checks, including evidence policy, invalid/truncated inventories, holes, membership and the exact checklist/Linear mapping.
- Nine independent geography checks: source hashes and complete 18-record download; 132 IDs; finite valid geometry; labels/bounds; no pairwise area overlap; full district coverage; explicit island ownership; all 149 in-district place anchors and four documented exceptions; multipart/hole preservation; mobile data budget.
- Actual Chrome city UI: optional-layer HTTP failure/retry, disable-during-load race, cancellation of delayed arrivals and pending Walk requests, marker selection, all 132 selector entries, section/territory framing, night and stargazing behaviour, toggles, previous place-label setting and 320/390/1440 px layouts. No browser page errors.
- Central A/B measurement: three additional draw calls (212 → 215), unchanged 2,718,287 triangles and approximately 16.7 ms median frames. Exact samples and screenshots: [browser verification](browser/verification.json). These are desktop Chrome measurements, including mobile viewport emulation; physical-phone performance is unverified.

Source geometry payload: 132 areas, 147 components, 39 holes, 23,233 vertices; approximately 1.02 MB raw / 304 KB gzip. Browser lines densify long edges at up to 100 m intervals and batch by readiness, with one selected-border draw. There is no extra draw call or section-data request while the default layer is off.

Run from the worktree root:

```sh
python3 source-scripts/city/review-sections/build_readiness.py
/tmp/astra-city-venv/bin/python source-scripts/city/review-sections/build.py
/tmp/astra-city-venv/bin/python source-scripts/city/review-sections/test_geography.py
node --test 3d-viewer/city/tests/*.test.js
node 3d-viewer/city/tests/review-sections-browser.mjs
```

Browser checks expect the existing preview at `http://127.0.0.1:4176`. Original source bytes and hashes are retained beside the publisher. See [source plan](geography-source-plan-3000x1900.png), [desktop tracker](browser/desktop-section-tracker.png), [territory overview](browser/hong-kong-overview.png) and [mobile tracker](browser/mobile-320-tracker.png).
