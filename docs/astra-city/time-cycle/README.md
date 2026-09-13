# Adjustable city timelapse · HKS-189

The 24-hour dial, playback button and speed slider form one visible group at the top of Time, before date and live-clock settings. This extends `CityEnvironment.timeLapse`; it does not introduce another city clock or timer. Markup and responsive control-sheet styles are coordinated with HKS-190.

The slider now displays **1×–7,200× normal speed**, in whole multipliers. At 1×, one simulated second equals one real second. The default is **450×**, preserving the previous one-hour-in-eight-seconds pace. The adjacent note translates the speed into a full day: 24h at 1×, 24m at 60×, 3m 12s at 450×, 48s at 1,800× and 12s at 7,200×. The range is keyboard accessible and reports the normal-speed multiplier through `aria-valuetext`. Internally, the existing clock still uses simulated minutes per second; the UI converts the multiplier by dividing by 60.

The existing calendar date advances through midnight, month/year boundaries and leap days. Each step still runs the existing `applyClock()` path: solar/lunar position, directional light and shadows, sky colour, day/night exposure and the original building occupancy schedules. Business/residential/retail activity retains its existing researched curves and overnight minimum.

Playback uses the existing render callback's monotonic timestamp, independently of the capped physics delta. It therefore retains its advertised speed at lower frame rates. Starting/stopping or changing speed resets the elapsed sample. Pause, hidden-tab visibility, Stargaze and Reduced Motion hold playback; the following running frame starts afresh without catching up skipped time. Speed and enabled state are preserved during these suspensions, with the reason shown beside the control.

Selecting a time on the dial, typing an exact time, choosing a preset or changing the date stops playback. Selecting Live Hong Kong time also stops it. Pressing Play switches the sky to Manual while retaining the selected date/time. Changing the speed alone does not start playback. Live HKO weather observations and astronomical tide predictions retain their own actual-time clocks and source timestamps; accelerated sky playback does not re-date those feeds.

The small `time-cycle.js` helper derives playback state and advances the existing timestamp. Diagnostic `environment.timeCycle` includes enabled/running, speed, full-day duration and suspension reason. `environment.sunLight` exposes actual light/target positions and the shadow matrix for browser verification.

## Verification

From the repository root:

```sh
node --test 3d-viewer/city/tests/time-cycle.test.js
node 3d-viewer/city/tests/time-cycle-browser.mjs
```

Reserve the shared GPU slot before running the browser script. It uses the running city at port 4176 and accepts `CITY_URL`/`CHROME_PATH` overrides.

Six focused tests cover speed units/bounds, midnight/year/leap-day/multiple-day progression, suspension/resume, the existing sun and lighting schedules, and the monotonic 10 fps/no-catch-up policy. The browser script measures actual playback speed, keyboard/touch operability, midnight wrapping, light/shadow-matrix changes, occupancy, 180 rendering frames at 30 min/s, pause/Reduced Motion/Stargaze, manual/Live semantics, source-clock independence and 390/320 px layouts. Its final result and screenshots are saved alongside this note.

The displayed speed is a time conversion, not a promise that every simulated minute will receive a rendered frame. At high speeds, intermediate times are skipped visually between frames while elapsed simulation time remains correct. Live celestial time remains available separately; timelapse is an explicit user-controlled simulation.

## Recorded browser result

The latest browser run passed all **10 groups** with no page or console errors. At 1,800× (30 simulated min/s), 180 desktop frames measured **16.7 ms median / 16.8 ms p95**. Short sampling windows measured 7.32 and 29.29 simulated min/s for requested 450× and 1,800×; the helper retains internal minute units and frame-boundary sampling affects short measurements.

The new first-open screenshots at 390×844 and 1024×768 were inspected: the full dial, toggle, multiplier readout, slider and day-duration note appear together without scrolling. Assertions also pass at 320×667, 760×800 and 1440×1000. The current government/OSM source summary matches the served manifest. Native keyboard Home selects 1× with a 24h day; ArrowRight advances by 1×. Actual touch input and playback continue to work. The five original clock regression cases plus the new multiplier-to-elapsed-time case pass.

## Visibility and units follow-up

The user reported that the speed slider appeared missing. The served page contained it, but earlier tests scrolled it into view and missed the initial visibility problem. The controls have been regrouped at the top of Time; the speed track and thumb are also more distinct. The browser regression now checks the whole dial/play/speed/duration group at scroll position zero across 320, 390, 760, 1024 and 1440 px. Source summary verification also checks the current **346,115 building forms · Lands Department + OSM** label; 42,892 was the earlier OSM dataset. This label change adds no buildings or geometry.
