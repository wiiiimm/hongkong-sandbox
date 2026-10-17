# Clock toggle and Weather shimmer — HKS-190

7 September 2026 · implemented and reviewed by GPT-6 Astra (root).

The Clock dropdown is now an accessible native Live/Manual switch. Live follows Hong Kong's current date/time, stops timelapse and disables the date field. Manual freezes the current time and enables the date; dial, presets, exact time and timelapse also restore Manual. Distant light shimmer moves to Weather while retaining its original renderer and reduced-motion behaviour.

Verification against the actual local city:

- `node 3d-viewer/city/tests/clock-toggle-browser.mjs`: four groups pass, including native mouse/Space/Enter/touch interaction, mode/date synchronisation, tab placement and lighting state, 44 px targets and no overflow at 320/390/1440 px. Zero browser errors. Screenshots in this directory were inspected, including night-mode contrast.
- `node 3d-viewer/city/tests/time-cycle-browser.mjs`: ten existing timelapse groups pass; unchanged speed, year rollover, sun/shadow movement, building-light schedules and independent live weather/tide clocks. Evidence remains in `../time-cycle/`.
- `node 3d-viewer/city/tests/clock-browser.mjs`: eleven existing clock groups pass, including all 24 hours, touch, midnight wrap and dynamic reduced-motion shimmer.

Mobile checks use desktop Chrome with touch and phone-size viewports; physical devices were not tested. HKS-190 is ready for review; broader feature parity and HKS-170 Tai O completion remain in progress.
