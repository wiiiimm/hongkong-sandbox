# Tai O public village walk

The completed walk joins the promenade landing approach, Wing On Street, Tai Chung Bridge, Tai O Market frontage, Kwan Tai Temple frontage and Kat Hing Street. The retained OSM route is **604.938 m**: 53 original source nodes plus the current rounded arrival and its exact projection onto the same public path, grouped into 12 segments. Its six stops include a short return along the market frontage. The final stop remains on Kat Hing Street before the unreviewed Sun Ki Bridge approach.

The checked walking line is **607.015 m** in plan. Actual `Navigation.update` replay completed **607.352 m forward and 607.238 m in reverse**, using one initial arrival per direction and no position resets along the route. The difference includes normal swept movement around corners. Parent integration independently completed **607.735 m** through the real browser, with source picking, both approach cards and inspected desktop/mobile exports. Browser evidence lives alongside the parent completion report.

## Sources and access

- [Transport Department](https://www.td.gov.hk/en/transport_in_hong_kong/public_transport/ferries/service_details/index_t.html) locates the Tai O ferry landing at the promenade steps; [CEDD's public landing list](https://www.cedd.gov.hk/eng/about-us/organisation/ceo/pwd/port-main/public_piers/nti/index.html) identifies the two promenade landings. This walk starts above the tidal steps and excludes ferry boarding.
- [Islands District Office](https://www.islands.gov.hk/en/explores-tai-o-tai-chung-bridge-tai-o-creek-pedestrian-bridge.php) identifies Tai Chung as the pedestrian drawbridge between Market Street and Wing On Street. The conflicting OSM `bridge:structure=floating` tag remains raw evidence; the official drawbridge description is preferred.
- [Commissioner for Heritage Office](https://www.heritage.gov.hk/en/financial-assistance-for-maintenance-scheme/information-on-applications/2017-2018/kwan-tai-temple/index.html) documents Kwan Tai Temple on Kat Hing Back Street and a 06:00–17:00 public-access arrangement. This walk visits the outside frontage only.
- [Hong Kong Tourism Board](https://www.discoverhongkong.com/eng/place-to-go/travel.guide-solo.html) lists visitor premises on Kat Hing Street. This supports the visitor-street context without granting access to residential decks.

OSM geometry comes from the retained `source-scripts/city/snapshots/outlying-west.json.gz`, snapshot **2026-09-06 05:51:35 UTC**. Its compressed SHA-256 is retained in `route.json`. Projection reuses `build_city.xy` and EPSG:2326. Official public-reference links were checked on 7 September 2026; no archival map images were used.

Private/restricted access, indoor paths, tidal landing stairs and ambiguous residential decks are excluded. The original OSM chain has no mapped steps or marked road crossings. The final simulation separately adds the explicitly estimated bridge approaches below. One pedestrian approach records unmarked lanes and is flagged for possible service-vehicle conflict. The promenade source's imagery-distortion caveat remains in provenance; the destination description now gives useful visitor guidance.

## Bridge-entry discrepancy and explicit estimates

The OSM Wing On shortcut crosses a solid railing in the original 3D bridge model. Nearby iB1000 `STP` features 1109131981/1109131982 and `PA` features 1109097753/1810305569 locate public access northeast of the bridge, but the 3D mesh also contains railing across that exact plan strip. The sources disagree; neither source is silently altered.

A separate connector uses the **existing southeast mesh opening**, with its exact floor-boundary intersection at `[-30659.7580, 3685.2581]`. It joins the retained public street to the source floor. Its intermediate horizontal alignment is explicitly estimated, at most **1.7284 m** from the original shortcut. Source lines, IDs, hashes and the discrepancy are recorded in `source-scripts/city/tai-o-completion/route-entry.json`; the [entry diagnostic](route-entry-review.png) shows both sources and the final walking line.

The visible Wing On estimate has four 0.2145 m risers, approximately 0.6047 m treads and a 0.8 m level landing at 3.2 m HKPD. It reaches the original 4.058 m deck and meets current terrain at the public street. The level landing is necessary for the unchanged 0.55 m walking radius and 0.32 m step limit. The short Market Street estimate follows its unchanged public source edge, linking the 2.629 m source deck to current terrain. Neither approach is an as-built stair survey or an accessible-ramp claim.

## Runtime contract and acceptance

`centreline`, `nodeIds`, original segment tags and source URLs stay intact. `walkCentreline` holds 2,459 checked positions. `walkSampleSources` identifies either an original edge/fraction or the separately documented connector edge/fraction. Only 66 samples need additional lateral clearance adjustments; the largest is **0.30 m**, within the planner's 0.75 m bound. Stops retain source indices and gain `walkIndex`. The [route plan](route-plan.png) shows this relationship.

`route-navigation.json` binds acceptance to the walking-line hash and live terrain, bridge and building-tile hashes. Both directions execute the real navigation method, with the real terrain sampler, mapped-water rejection, building index and source/estimated floor triangles. Forward and reverse use 9,843 and 9,834 frames respectively; there are no collision overrides or inter-waypoint teleports. Removing the public bridge floors blocks at mapped water. Raising water to 3.8018 m HKPD blocks the low promenade after approximately 1.04 m. That high-water value is a deliberate regression fixture, not a tide forecast.

The runtime copy is `3d-viewer/city/data/tai-o-route.json`. `continuousWalkVerified: true` describes this bounded public route; it does not certify all Tai O paths, private platforms, stair accessibility or surveyed house-pile geometry.

## Collision correction

Detailed models previously filled their whole axis-aligned bounding rectangle when mesh geometry extended beyond an outline. This blocked public streets beside rotated houses. The corrected index retains solid source footprints and clips actual model triangles to the actor's vertical span. Real walls and elevated overhangs remain collidable; open-sided structures retain roof/post behaviour. Aircraft clearance includes actual model tops through the existing streamed index.

The source-line diagnostic uses the same 2,449 samples for both representations: **860 old rectangle contacts versus 34 precise contacts**, removing 826 false contacts. Those 34 remaining contacts match native footprint clearance and are handled by the documented walking alignment; the diagnostic deliberately uses ground height without bridge support. `route-preflight.json` is labelled diagnostic-only, not final movement acceptance. No source footprint, model vertex or recorded height changes in this correction.

A bent-stair regression also caught mismatched mitres at coincident horizontal positions. Shared cross-sections now keep risers vertical, preserving exact top-face counts and sharing the same Float32 geometry for visible decks and walking support.

## Reproduction

Run from the Astra worktree. The retained source infrastructure payload is already included; if regenerating it first, run `infrastructure.py` without `--publish` before the entry step.

```sh
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/tai-o-completion/route_build.py
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/tai-o-completion/route_entry.py
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/tai-o-completion/infrastructure.py --publish
node source-scripts/city/tai-o-completion/route_align.mjs
node source-scripts/city/tai-o-completion/route_navigation.mjs --publish
node source-scripts/city/tai-o-completion/route_audit.mjs
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/tai-o-completion/route_plot.py
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/tai-o-completion/route_entry_plot.py
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/tai-o-completion/route_test.py
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/tai-o-completion/infrastructure-test.py
node --test 3d-viewer/city/tests/tai-o-route.test.js 3d-viewer/city/tests/infrastructure.test.js 3d-viewer/city/tests/model-collision.test.js 3d-viewer/city/tests/bridges-render.test.js
```

Four route-source tests, five original-mesh source tests, three continuous-route regressions and the focused bridge/model tests pass. Source generation deliberately resets runtime acceptance until the complete replay passes again. Superseded failed movement reports and the earlier timing sample were removed; the current source diagnostic remains clearly separated from final route acceptance.
