# Astra city weather integration

Implemented by the GPT-6 Astra weather subagent on 6 September 2026. All changes belong to `codex/astra-hong-kong-city`; original game sources and source references are unchanged.

## Supported in this pass

- Independent live and manual modes, preserving the user's manual settings when returning from live mode.
- Manual rain, cloud cover, fog, wind, waves and snow intensity; wind-from direction in degrees clockwise from north.
- HKO current report: original observation timestamp, nearest known reporting temperature station, available humidity station, territory weather condition, warning text and nearby district's past-hour maximum rainfall.
- Real observed wind from the nearest known reporting station, with speed, direction, gust, station and its own timestamp. The archive route delays these observations; the UI must retain that timestamp.
- Bounded local precipitation and cloud rendering, with no territory-wide particle allocation. Maximum counts are 2,400 rain streaks, 900 snow points and 80 instanced cloud cards, adding at most three draw calls.
- Reduced motion freezes clouds and hides moving precipitation. Pausing freezes animation and automatic polling. Stargazing can suspend the atmosphere without discarding either mode's settings.

## Public API

`city/weather.js` exports `createWeather({scene,camera,fetchImpl?,now?,timeoutMs?})` and `weatherAtmosphere(settings)`.

The created object exposes:

```js
weather.setManual({rain: .4, clouds: .75, fog: .1, wind: .3,
                   waves: .3, snow: 0, windFrom: 90});
await weather.setLive(true); // false restores saved manual settings
await weather.refresh();
const atmosphere = weather.update(dt, {
  position, reducedMotion, paused, night, suspended: stargazing,
});
const status = weather.state;
weather.dispose();
```

Intensity values are 0–1, clamped on input. Missing or invalid manual values retain their previous value. Wind-from wraps to 0–360°. In live mode `settings.windFrom` can be `null` for a missing or variable direction; there is then no directional particle drift. A UI synchronising its disabled direction input can use `settings.windFrom ?? 0`, but must not describe that UI fallback as an observed northerly.

`update()` returns `fogDensity`, `visibilityMetres`, `cloudCover`, `ambientMultiplier`, `sunMultiplier`, `skyMultiplier`, `wetness`, `waveStrength` and `windVector` in city coordinates. The city integration owns shared fog, sky, lights and water; the weather module does not overwrite those objects. `visibilityMetres` is an artistic visibility parameter, not an HKO visibility measurement.

State includes `mode`, `status`, `settings`, `manual`, `observation`, `updatedAt`, `checkedAt`, `error`, `windError`, `source`, `approximate` and animation `elapsed`. Status is `idle` in manual mode and `loading`, `live`, `stale` or `error` in live mode. `updatedAt` is the report's original timestamp; `checkedAt` is the client's successful retrieval time. The two must not be conflated.

`observation` preserves temperature/humidity/wind station names and per-feed timestamps. Rainfall retains its start/end times and district name. Forecast words in the territory condition do not mean that every district is currently receiving rain.

## Data and provenance

The implementation reuses the original game's published HKO endpoints, the DATA.GOV.HK archive approach from `main.js`, and approximate station coordinates in `3d-viewer/data/hko-stations.json`. It includes the original station-to-district associations. It does not modify those original files.

- [HKO Open Data API documentation](https://www.hko.gov.hk/en/weatherAPI/doc/files/HKO_Open_Data_API_Documentation.pdf) documents the `rhrread` current weather JSON endpoint.
- [HKO open datasets](https://www.hko.gov.hk/en/abouthko/opendata_intro.htm) describes current reports as hourly and on update, and the regional ten-minute wind data as provisional.
- [HKO regional weather portal](https://www.hko.gov.hk/en/wxinfo/awsgis/regional_portal.html) identifies wind speed units as kilometres per hour.
- [Current weather dataset on DATA.GOV.HK](https://data.gov.hk/en-data/dataset/hk-hko-rss-current-weather-report) provides the current report distribution.
- [HKO latest ten-minute wind CSV](https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_10min_wind.csv) supplies dated station observations; browsers obtain its archived snapshot through DATA.GOV.HK to allow CORS access, as the original game does.

No `references/lantau-maps/` image was used for this weather implementation. Station coordinates retain their original approximate status.

## Observation-to-appearance assumptions

These controls are an interactive visual interpretation, not a calibrated meteorological or marine model:

| Input | Visual use | Limitation |
| --- | --- | --- |
| District's maximum past-hour rainfall | Rain intensity `log(1 + mm) / log(36)`, clamped to 0–1 | Past-hour accumulation is not an instantaneous rain rate. District selection uses the nearest station's district association, not a surveyed boundary. |
| HKO condition icon | Sparse to full cloud coverage; a rain fallback only if a local district total is unavailable | Territory condition is not gridded cloud cover. Cloud locations and altitude are procedural. |
| Fog/mist/haze condition icon | Fog intensity 0.72/0.40/0.24 respectively | Humidity alone does not activate fog. Visibility is an artistic distance effect; no measured visibility feed is consumed. |
| Nearest station's observed wind | Strength `km/h / 65`, clamped; measured wind-from sets drift | Local rooftop shelter, turbulence and gust dynamics are not modelled. Variable/missing direction produces no directional drift. |
| Wind strength | Live wave intensity `wind × 0.85` | These are illustrative waves, not measured sea state, tide or swell. Missing wind produces calm wind/waves and an explicit availability message. |
| Snow | Manual visual option only | Live mode never derives snow from Hong Kong observations. No accumulation model in this pass. |

World +x is east and −z is north, matching the existing HK1980 city coordinates. A meteorological wind from the east therefore drifts towards −x.

## Network behaviour and error handling

Live requests are initiated by the user enabling live mode. Automatic refresh is every five minutes while active, except during pause or suspension. Manual refresh is limited to once per minute, or once per ten seconds after an error. Requests have a shared 12-second timeout; switching to manual or disposing cancels pending requests and prevents late data overwriting the user's settings. A cancelled request can be restarted immediately when live mode is re-enabled.

Invalid or missing current-report timestamps and unusable report bodies are rejected. Reports more than 90 minutes old are labelled stale; timestamps more than 15 minutes in the future are rejected. A failed refresh retains the last observation and visual state with an explicit stale/error status. No invented observation is substituted. Optional wind failure does not discard a valid main report, but clears the wind observation and exposes `windError`. Wind rows older than 90 minutes are excluded.

The HKO JSON endpoint was verified from the actual city browser origin. The regional CSV does not directly permit browser CORS; the existing archive method does, when an Origin header is present. The archive request asks for a snapshot 15 minutes before the client clock, and the returned CSV carries the authoritative station timestamp. The client never changes the timestamp to make archived wind look current.

## Validation

```sh
node --test 3d-viewer/city/tests/weather.test.js
node 3d-viewer/city/tests/weather-render.mjs
```

Eleven deterministic unit tests cover numeric controls, compass parsing, original timestamps, missing values, regional rain, humidity/fog distinction, caching/throttling, manual restoration, optional wind failure, offline recovery, stale/future data, late responses, request timeout, disposal and rapid live/manual toggles.

The Chrome WebGL fixture uses the city's `logarithmicDepthBuffer: true`, perspective camera and 100 km far plane. It verifies visible clouds, moving rain and snow, byte-identical output under reduced motion, precipitation suppression, stargazing suspension, shader compilation and disposal. Both custom cloud and snow shaders include logarithmic-depth and fog chunks. A separate real-network check on 6 September 2026 obtained the HKO 13:02 HKT report and a Star Ferry 13:30 HKT wind observation from the browser; fixture assertions do not depend on today's network or weather.

## Remaining original-game parity

This pass does not restore the original typhoon signals, regional lightning field/bolts/audio, radar and satellite loops, interpolated regional weather/cloud fields, air-quality haze, tide gauge/history and tide physics, snow accumulation, flooding, cockpit wet windscreens or procedural weather soundboard. Rain is a local camera envelope and does not yet collide with roofs, decks or terrain. Those features remain in the original viewer and should be migrated as separate bounded integrations rather than claimed complete here.
