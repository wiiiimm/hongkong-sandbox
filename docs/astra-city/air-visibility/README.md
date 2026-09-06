# Live visibility and air-quality observations

The bounded controller in `3d-viewer/city/air-visibility-data.js` supplies measured visibility and separately labelled AQHI to the existing weather UI. It reuses the original game's AQHI endpoint and station assets; it does not create another weather renderer or convert AQHI to visibility, pollution concentration or sky brightness. The root agent owns fog/UI integration and its browser verification.

Both official JSON endpoints returned HTTP 200 and `Access-Control-Allow-Origin: *` to an HTTPS GET carrying the local preview Origin. [The retained response check](endpoint-verification.json) includes timestamps, payloads, response headers, URLs and SHA-256 hashes. This was a direct endpoint/header check without launching a GPU browser; root subsequently tested the integrated UI using deterministic feed mocks.

## Sources and interpretation

- [HKO LTMV](https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=LTMV&rformat=json&lang=en) uses `fields` plus `data` arrays: HKT `YYYYMMDDHHmm`, station name and a value such as `17 km` or `N/A`. The parser resolves field names, so column order can change. HKO's [visibility notes](https://www.hko.gov.hk/en/vis/vis_index.shtml) identify automatic ten-minute averages at Central, Chek Lap Kok, Sai Wan Ho and Waglan Island. Their reporting endpoints are censored: 100 m means at most 100 m, and 50 km means at least 50 km. These limits are exposed explicitly. Visibility includes the combined effects of fog, rain and haze; a separate rain/fog opacity must not be added to the measured visibility mapping.
- [EPD AQHI via DATA.GOV.HK](https://dashboard.data.gov.hk/api/aqhi-individual?format=json) returns `station`, `aqhi`, `health_risk` and `publish_date`. The observed publication string has no timezone suffix and is interpreted as HKT. AQHI `10+` keeps that label; missing/invalid AQHI never becomes zero. EPD describes [AQHI as a health-risk index](https://www.aqhi.gov.hk/en/health-advice/health-effects.html), and distinguishes general from roadside exposure. We prefer the nearest fresh general station; a fresh roadside observation is only a labelled fallback if general readings are unavailable. No health advice or optical calibration is inferred.
- Selection reuses `3d-viewer/data/hko-stations.json` and `epd-aqhi-stations.json`, whose coordinates are explicitly approximate. Central aliases Central Pier. The missing Sai Wan Ho anchor comes from HKO's [2023 station table](https://www.hko.gov.hk/tc/publica/smo/files/SMO2023.pdf): 22°17′08″N, 114°13′33″E, projected WGS84 → EPSG:2326 as E841313.4, N816297.1. This is a station-selection anchor, not exact visibility-meter placement. Chek Lap Kok can use an alternative airport meter according to HKO. No archival Lantau imagery was used.

## Integration contract

```js
const data = createAirVisibilityData({fetchImpl, now, timeoutMs: 12000});
data.setPosition(x, z); // Also accepts {x, z}; city HK1980 origin is reused.
await data.setLive(true);
await data.refresh(); // Throttled; concurrent calls coalesce per feed.
data.poll();           // Existing animation loop may call this; no permanent timers.
const state = data.state;
await data.setLive(false);
data.dispose();
```

`state` contains `mode`, `disposed`, active `visibilityMetres`, and separate `visibility` / `aqhi` objects. Each observation carries `station`, `distanceMetres`, `updatedAt`, `checkedAt`, `receivedAt`, `source`, `sourceURL`, `fresh`, `status`, `error` and `selection`. Visibility adds `visibilityMetres`, `observedVisibilityMetres` and `limit`; AQHI adds `aqhi`, `aqhiLabel`, `healthRisk` and `stationKind`.

Top-level `visibilityMetres` is null unless Live, fresh and usable. Nested `visibilityMetres` is also null when stale/future; `observedVisibilityMetres` retains an old reading solely for explicitly dated status text. `fresh` describes the observation's age even in Manual; it does not authorise applying it. Missing coordinates/readings cannot become a fabricated nearest observation. With no valid city position, the selection label explicitly says the first usable station was used and distance is null.

Freshness limits are application policies: visibility 30 minutes, AQHI 90 minutes, and a five-minute future clock tolerance. They are checked whenever state is read. Both feeds refresh every five minutes; explicit refresh is capped at once per minute, failed requests may retry after ten seconds. Each feed has its own timeout/cancellation and publishes success independently. A failed request can retain a previously fresh reading only until its original expiry. Manual/dispose invalidates pending generations, aborts requests and clears active metres immediately, even if a mocked transport ignores its AbortSignal.

Run `node --test 3d-viewer/city/tests/air-visibility-data.test.js` from the worktree root. All 17 focused cases pass: source parsing/limits, HKT/calendar validation, missing/non-finite readings, nearest selection, general/roadside distinction, stale/future display metadata, independent failures/timeouts, cancellation/disposal, throttling and cache expiry. The controller contains no terrain/model mutations and did not use the GPU slot.
