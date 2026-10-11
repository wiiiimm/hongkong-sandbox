# Tide and wave restoration · HKS-180

Implemented by the Astra weather agent in the existing city worktree. The city now reuses the original viewer's tide interpolation, animated wave normals, rain pocks, sun glitter, wet shoreline band and shore foam. This slice does not complete the broader HKS-180 typhoon/manual-feature issue.

## Original comparison

| Feature | Original viewer | City adaptation |
| --- | --- | --- |
| Tide inputs | HKO HHOT for Cheung Chau or Quarry Bay; yesterday/today/tomorrow, 72 hourly heights | Same two stations and HHOT daily requests; explicit source dates, cached-day provenance and failures |
| Interpolation | Linear `tideAt`; endpoint clamping | Same extracted function; city checks coverage and missing hours before interpolation |
| Vertical scale | Normalises a ±12-hour prediction window into a 0–1 slider and scales sea movement by terrain span | Preserves prediction metres, converting Chart Datum to HKPD |
| Manual tide | 0–100%; leaving Live adopts the last live fraction | −1 to +4 m HKPD; leaving Live restores the saved manual value, consistent with city weather |
| Prediction graph | ±12 hours, hourly series, rising/falling/slack | Same window and trend threshold; root UI breaks curves at missing hours and labels predictions |
| Waves | Three analytic normal octaves, rain normal noise, sun microfacet glitter; whole-plane positive bob | Exact shared shader passes; frame-time-driven animation, zero-mean illustrative heave no larger than ±0.18 m |
| Wet shore/foam | Terrain tint above sea level plus the existing tileable canvas texture | Same shared GLSL and texture factory; illustrative 0.6 m vertical wet band, 0.132 m foam edge, reduced intensity at night |
| Pause/reduction | Original behaviour retained | Pause and Stargaze hold effects and tide level; Reduced Motion freezes wave time and removes heave/rain jitter |
| Low-water clamp | Artificial `SEA_MIN` needed for original zero-height sea bed | No copied clamp: city ocean geometry is below the HKPD tide range |
| Storm surge | Stylised signal-dependent positive offset | Not included in this slice; HHOT is never labelled an observed total water level |

`main.js` retains its existing behaviour, source/station choices, tidal range normalisation, minimum sea level, weather locks and live-to-manual policy. The shared function bodies were extracted. One existing defect was also repaired: terrain-only density changes (including boot's saved density restore) cleared the sea from the material-update list, leaving wave uniforms at their initial zero values. `rebuildTerrain()` now re-registers the current sea without retaining disposed sea materials during a full source change. The regression fixture confirms identical original terrain/sea shader source for all wet/water combinations and identical canvas gradient draw sequence.

## Source and datum

HKO's [prediction notes](https://www.hko.gov.hk/en/tide/enotes.htm) identify the tide heights as metres above Chart Datum and place that datum 0.146 m below Hong Kong Principal Datum. The city therefore applies **heightHKPD = heightCD − 0.146 m**. HKO computes the astronomical predictions; this adapter interpolates published hourly values. The feed assumes average meteorological conditions, so weather-driven differences and storm surge are not measured or reconstructed here.

The [official API documentation](https://www.hko.gov.hk/en/weatherAPI/doc/files/HKO_Open_Data_API_Documentation.pdf) documents `HHOT`. Its JSON fields are `MM, DD, 01, …, 24`; column 24 means midnight at the start of the following HKT day. All internal sample times are UTC epoch milliseconds. No local sky-calendar or accelerated day-cycle value is passed to the prediction clock.

Quarry Bay's tide-gauge position comes from [HKO's station catalogue](https://www.hko.gov.hk/en/cis/stn.htm): 22°17′28″N, 114°12′48″E. Cheung Chau's tide-gauge position comes from the coordinate table in [HKO's 2022 Tide Tables](https://www.hko.gov.hk/tc/tide/tide_tables/2022/files/TideTable2022.pdf): 22°12′51″N, 114°01′23″E. These are gauge positions, not the same-name weather stations. Automatic selection chooses the nearer of these two anchors only. A uniform sea plane and two stations do not resolve tide differences throughout Hong Kong.

The six retained, unedited daily responses for 5–7 September 2026 are in `3d-viewer/city/tests/fixtures/tides/`. Their `provenance.json` records exact official query URLs, retrieval times, byte lengths and SHA-256 hashes. They are test fixtures, not a fallback live feed. No archival map image was used or modified.

## Controller and integration

`createTideData({fetchImpl, now, timeoutMs})` exports `setManual(levelHKPD)`, `setLive(boolean)`, `setStation('QUB'|'CCH')`, `refresh()`, `update({paused,suspended})`, `state` and `dispose()`. The default is Manual at 0.3 m HKPD. `TIDE_STATIONS` is keyed by code; `chooseTideStation({lat,lon})` returns a station object.

State includes `mode`, `status`, `station`, `manualLevelHKPD`, `restingLevelHKPD`, `basis`, `prediction` and `error`. `basis` distinguishes manual settings, usable predictions and the explicitly labelled manual fallback. A prediction contains `time`, `heightCD`, `heightHKPD`, `trend`, a 72-point hourly `series`, `sourceUrls`, `fetchedAt`, `checkedAt` and `sourceFetches`. Each daily source entry records its own retrieval time and whether that day came from cache. `fetchedAt` is retrieval time, not an HKO issue or gauge observation timestamp.

The controller requests at most three daily files per refresh. Automatic refresh follows the original five-minute interval; successful button refreshes have a one-minute floor and failures a ten-second retry floor. Requests have a 12-second abort deadline. Manual mode makes no request on load. Cancellation/generation checks prevent late responses from overwriting Manual or another station. Missing hours remain null; neither interpolation nor the graph bridges them. An expired/missing current sample uses the saved manual sea level and labels that fallback. Pause/Stargaze prevent new requests and retain the current level, then resume at actual current time.

`makeWater()` returns the existing `mesh`, `material`, `time` and `strength`, plus `setLevel`, `update`, `levelAt`, `state`, `attachShoreline` and `dispose`. Root integration sets the tide level, calls `update` once per frame, and attaches the terrain once with `water.attachShoreline(terrain)`. The shoreline effect reuses the existing terrain materials; it adds no mesh or draw call and preserves standard logarithmic-depth and fog chunks. Disposal restores the materials' previous compilation callbacks and releases the water's texture/geometry/material.

`restingLevelHKPD` is stable against short wave heave. Root navigation uses it for admission to paths and permits retreat towards shallower ground if the tide rises around the walker. `renderedLevelHKPD` and `levelAt` include the instantaneous small heave, for camera clearance and ferries. Shader time, wave phase, wave offset, normal/rain/glint strengths, shoreline material count and wet-band width are exposed for diagnostics.

## Validation

From the repository root:

```sh
node --test 3d-viewer/city/tests/tides.test.js
node 3d-viewer/city/tests/tides-original-browser.mjs
```

The browser script requires the running viewer at port 4176, Playwright's installed dependencies, and a reserved shared GPU slot. `ORIGINAL_URL` and `CHROME_PATH` may override its defaults.

Nine focused tests cover the official response schema and HKT midnight, datum sign, missing hours, current-time interpolation, request bounds, failures/recovery/expiry, late-response cancellation, exact manual restoration, pause/resume, wave limits/reduction/disposal, shore attachment, and compatibility with the original functions. The retained `original-water-functions.json` contains only the relevant original functions, with revision and full-source hash, so tests also run in shallow checkouts.

Root's actual-city browser evidence is in `browser/verification.json`, including low/high tide shore changes, floating ferries, walking admission, both stations and the graph, Stargaze/manual restoration, wave/reduced-motion behaviour and 390/320 px layouts. The original-viewer smoke and images are in `original-browser/`.

## Limits

Wave appearance and small heave are visual approximations driven by the existing weather settings; they are not a wave buoy measurement or a hydrodynamic model. Foam and instantaneous wet tint are illustrative, without beach-specific run-up or persistent drying. The water is a single plane rather than spatial tides, a sea-level inundation model or volumetric water. Terrain resolution and shoreline sampling constrain where it intersects dry ground. Actual measured tidal observations, storm-surge modelling and the remaining typhoon controls are still separate work.
