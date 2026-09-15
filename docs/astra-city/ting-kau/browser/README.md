# Bridge-cluster browser acceptance

Run `node source-scripts/city/ting-kau/browser.mjs before` or `after` from the Astra worktree **only after coordinating the shared GPU slot**. `CITY_URL` and `CHROME_PATH` may override the localhost:4176 viewer and system Chrome. The script injects read-only/debug references into the served `app.js` response; repository runtime files are not patched. The after phase uses the actual source/cable layers and normal application click handlers, streamed building meshes, terrain rays and navigation.

All comparison cameras use 7 September 2026, manual weather, haze 35%, tide0.30 m HKPD and 15:00; night captures use 22:00. Camera coordinates and actual diagnostics are recorded per image. The baseline captured 10 views with no page/shader/data errors;159 frame samples gave16.7 ms median / 16.8 ms p95 desktop,16.7 / 16.7 mobile. The terrain ridges are plainly visible in the inspected Tsing Ma under-span and Ting Kau overview images. These baseline timings describe that browser run, not a universal performance guarantee.

The injected cameras leave the existing location caption unchanged: the initial unrecognised `district=mawan` falls back to Central. The saved camera/target coordinates, geometry and minimap identify the actual bridge views. This is a fixture-caption limitation, not a claim that the bridges are in Central. Cameras/date/haze remain fixed for comparison.

After acceptance checks:

- Seven original source models and their source HKPD bounds; no duplicate rendered triangles. Matched original footprint records remain available while their seven façade extrusions are absent.
- Twenty-one completely replaced mapped bridge proxies; two original Tsing Yi approach tails retain their exact staged paths.
- Both separately labelled cable packets with zero official/source triangles; actual pixel ray and trusted mouse selection for both source bridges and both cable illustrations.
- Nine vertical rays against the rendered terrain reach the illustrative −4 m bed; all four sampled foundation sites remain land. Source bridge collision is present at the deck and absent below. No motorway deck gains walking support.
- Actual light-aircraft flight beneath Tsing Ma at 35 m HKPD, with normal frame-driven movement and collision handling.
- Layer toggling also hides cable picking; matched day/night/foundation/under-span images;390 px and320 px layouts; desktop/mobile frame timings; no shader/page/data errors.

The final AFTER run **passed** against the published source-corrected foundation terrain: 16 captures, no page/shader/data errors. Desktop and mobile each retained 159 measured frame intervals: **16.7 ms median / 16.8 ms p95**. The desktop view used 136 draws / 1,649,397 triangles; the narrow mobile view used 56 draws / 1,025,749 triangles. These are the observed fixed-camera runs, not a universal performance guarantee.

Both source cards and both cable cards were selected through actual mouse clicks. The seven government building records remain present while their duplicate façade meshes are suppressed. Real UI entry into Fly completed from the far-panned bridge camera, then normal navigation crossed the span at 35 m HKPD from z−6921 to z−7100. Sixteen recorded position samples bracket the crossing without collision or a false-land climb. The final screenshot is taken after the plane passes below the span, so the flight log supplies the actual crossing evidence.

Image inspection covered both day overviews, both repaired islands, source/cable cards, night, 390/320 px layouts and flight. Three additional terrain rays at previous land spikes now hit 2.17, 7.12 and 6.40 m HKPD, matching the published source correction. The mobile images retain the fixed comparison cameras and therefore crop the long bridge ends; they demonstrate layout and source rendering, not a complete engineering elevation.

The earlier review discovered and repaired the foundation-mask defect described in [the source correction](../foundations/README.md). Browser integration also exposed a native `fetch` receiver error in the new cable adapter; its focused regression now passes. A separate preset/Fly arrival race was fixed by root and is covered by the final real-button check. One added spike test initially selected mapped water just outside the southern shore; that fixture coordinate was corrected to the adjacent actual land spike. Failed-run images are removed after success. None of these earlier failures is reported as an open final production defect.

See [final verification](after/verification.json) and [image inspection](after/image-inspection.json). No browser or code assertion certifies complete engineering detail, navigational clearance or public access.
