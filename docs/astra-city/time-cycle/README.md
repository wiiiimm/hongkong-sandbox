# Adjustable city timelapse · HKS-189

The existing 24-hour dial's playback button now has a speed slider beside it in the Sky controls. This extends `CityEnvironment.timeLapse`; it does not introduce another city clock or timer. Markup and responsive control-sheet styles are coordinated with HKS-190.

The slider uses simulated minutes per real second, from 1 to 120 in half-minute steps. Its default is 7.5 min/s, preserving the previous one-hour-in-eight-seconds pace. The adjacent note translates that into a complete day: 24 minutes at the slowest setting, 3m 12s by default, 48s at 30 min/s, and 12s at the fastest setting. The range is keyboard accessible and reports its unit through `aria-valuetext`.

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

Five focused tests cover speed units/bounds, midnight/year/leap-day/multiple-day progression, suspension/resume, the existing sun and lighting schedules, and the monotonic 10 fps/no-catch-up policy. The browser script measures actual playback speed, keyboard/touch operability, midnight wrapping, light/shadow-matrix changes, occupancy, 180 rendering frames at 30 min/s, pause/Reduced Motion/Stargaze, manual/Live semantics, source-clock independence and 390/320 px layouts. Its final result and screenshots are saved alongside this note.

The displayed speed is a time conversion, not a promise that every simulated minute will receive a rendered frame. At high speeds, intermediate times are skipped visually between frames while elapsed simulation time remains correct. Live celestial time remains available separately; timelapse is an explicit user-controlled simulation.

## Recorded browser result

The final browser run passed all nine groups with no page or console errors. At 30 simulated min/s, 180 frames measured **16.7 ms median and p95** (212 draw calls, 2,719,063 triangles). Short 0.8-second sampling windows measured 7.31 and 29.23 min/s for requested speeds 7.5 and 30; frame-boundary sampling accounts for the small difference.

Both desktop images were inspected at 1440×1000: the clock advances from 08:00 to 12:01 while building faces, directional shadows and sea glint change. The 390×844 mobile image deliberately shows the scrolled speed-control area; the upper part of the dial is above that scroll position. The slider and play button are readable and operable. At 390 px the range is 350 px wide; at 320 px it remains 288 px wide, with no horizontal document/content overflow. The separate HKS-190 control-sheet evidence includes the complete mobile dial view.
