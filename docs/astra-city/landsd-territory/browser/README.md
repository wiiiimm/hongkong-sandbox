# Territory browser verification

GPT-6 Astra, 6 September 2026. Final result: **passed**, with no page or console errors. The full source and live-merge audits remain separate; this checks the running City UI and WebGL renderer.

## Coverage

| Visit | Visible forms | Official forms | Median / p95 frame time |
| --- | ---: | ---: | ---: |
| Central | 25,720 | 25,356 | 16.7 / 18.4 ms |
| Kowloon waterfront | 19,819 | 19,544 | 16.6 / 18.1 ms |
| Tai O | 2,340 | 2,310 | 16.7 / 18.5 ms |
| Peng Chau | 4,685 | 4,530 | 16.7 / 18.8 ms |
| Cheung Chau | 4,138 | 4,119 | 16.7 / 18.2 ms |
| Sha Tin | 14,792 | 14,522 | 16.7 / 18.1 ms |
| Yuen Long | 50,030 | 49,947 | 16.7 / 18.1 ms |
| Mui Wo | 6,490 | 6,420 | 16.6 / 19.0 ms |

All eight arrivals were clear of the actual building collision volumes and supported more than 2 m of keyboard walking. Actual roof clicks opened the matching source card in each area. Live government requests for Central and the Mui Wo market returned the selected OBJECTIDs and identical recorded base/top values, including the market’s null elevations. Hiding Buildings removed its pick meshes and prevented re-selection; restoring the layer worked.

Building cache stayed at or below 30 tiles; regional and bridge caches stayed below their 24-tile limits. Mui Wo loaded all 275 retained detailed models. Their `OUTLINE HEIGHT` label and official non-textured roof attribution are already demonstrated by the Pak Ngan Heung Public Toilet and YICK YUEN cards in [the existing independent model browser report](../../mui-wo-buildings/review/live-model-check.json); those entries were read and reused rather than rerunning that check.

The same Kowloon close view contained 342,798 bright rendered pixels at 21:00 and 23,990 at 04:00. Some lights and street illumination remain on, and the surrounding geometry remains legible. Reduced-motion mode disables shimmer. Peng Chau’s 390×844 view and open settings panel have no horizontal overflow.

## Timing and transfer evidence

The final clean run used Chrome 152.0.7977.76 and ANGLE Metal on Apple M4 Pro at a 1440×1000 drawing buffer. Each view records 180 animation-frame intervals after 20 warm-up frames. No other agent browser or regression process ran during this final pass. These are steady-view local measurements, not a production network, flight, long-route or mobile-device benchmark.

App readiness was 0.595 s; all initially requested sections settled in 3.832 s. Completed local-server transfers at that point totalled 92.1 MB: 34.1 MB of geometry and 2.94 MB of activity sidecars, plus terrain, scripts, catalogue and other resources. The complete eight-visit run transferred 220.1 MB. HTTP routing disables the browser cache; the local server transfers plain JSON. These figures must not be presented as compressed deployment download sizes.

Startup requested 16 activity sidecars and never requested global `activity.json`. The existing tile loader fetches geometry and profiles concurrently with the same cancellation signal; readiness includes both. The accompanying `activity-streaming.test.js` suite passes 13 tests/subtests covering HTTP failure/Retry, malformed or incomplete per-building profiles, cancellation and late responses, profile baking, and legacy global-activity compatibility.

## Images and run records

All 15 final PNGs were opened and visually inspected: eight neighbourhood overviews, three source cards, the same night view at 21:00/04:00, and two mobile layouts. Building coverage and selection outlines are visible, source text is readable, and the darker view retains isolated lights. No blocking visual regression was found. Simple façades and coarse terrain/coast boundaries remain apparent; this is not a street-by-street architectural acceptance.

`verification.json` contains the final states, frame samples, source responses and inspected-image list; `requests.json` contains the completed-request byte/timing records. `initial-run-summary.json` preserves the first pass’s console measurements and explains its fixture failure: the test incorrectly expected recorded-height wording for the correctly estimated Mui Wo market. Seven areas and mobile passed on that initial run. Only the assertion changed; no production change was required. The final pass uses the corrected assertion against the same production assets. `muiwo-failure.png` is the retained initial diagnostic image, not an unresolved UI defect.

```sh
node 3d-viewer/city/tests/landsd-territory-browser.mjs
node --test 3d-viewer/city/tests/activity-streaming.test.js
```

The script reuses the established regional and Mui Wo browser patterns. A read-only test-response getter exposes existing app objects for roof framing and geometry probes; travel, clock, layer, source selection and movement all use the actual UI. No application hooks or model geography are changed by the browser test.
