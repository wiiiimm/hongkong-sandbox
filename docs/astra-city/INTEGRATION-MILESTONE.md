# Whole-territory city integration milestone

GPT-6 Astra · 6 September 2026 · isolated comparison branch
`codex/astra-hong-kong-city`.

The geographic base, priority island pass, core sky/weather controls and original
aircraft collection are integrated in `/city.html`. Three subagents handled
bounded geography, astronomy and weather/aircraft tracks; the primary agent
integrated the UI, night schedules and browser fixes. The comparison remains in
its own worktree. No deployment or merge into the original game is part of this milestone.

| Delivered track | Result |
| --- | --- |
| Geographic base | 117,062 mapped building forms, 449 tiles and 43 destinations across all 18 districts; reproducible sources and estimated heights identified |
| Priority islands | Mui Wo, Tai O, Cheung Chau, Peng Chau and six additional Lantau village shortcuts; 15,093 house/village fallback-height corrections; 11 short walking checks |
| Safe arrivals | All 43 presets checked against fully dry terrain triangles and building collision volumes; five older arrival points repaired |
| Astronomy | Original ephemeris, 1,573 catalogue stars and 24 constellation figures; dated/live HKT, seasonal dawn/dusk, sun/moon, star selection and a sky camera |
| Moving observer | Reproducible HK1980 to WGS84 interpolation for free exploration, rather than fixed Central coordinates; accuracy limits documented |
| Weather | Manual rain/cloud/fog/wind/waves/snow; real HKO conditions, temperature/humidity and district rain, with separately timestamped station wind |
| Aircraft | All seven original models, corrected orientation/scale, revised materials/propellers/lights, missing 747 winglets, material batching and portrait-aware cameras |
| City sleep | Homes peak at 22:00, sleep from around 23:00; offices leave from 18:00; shops close from 21:00–23:00. Midnight uses the earlier 04:00 window levels, and the new 04:00 reserve is much smaller |
| Integrated controls | Places/Sky/Weather tabs, aircraft selection and model Retry, mobile contrast/overlap fixes, reduced motion and destination-preserving streaming during camera transitions |

## Verification

- **53 JavaScript unit/data tests** and **7 Python importer/height tests** pass.
- The main browser regression covers layers, search, walking, flying, cameras,
  collision, preset travel, cache bounds, deliberate tile failure/retry and PNG export.
  The cross-harbour regression confirms Mong Kok retains its destination blocks.
- The clock and night suites exercise the full 24-hour dial, exact entry,
  keyboard/touch, date rollover, progressively quieter windows and late-night walking.
  The façade fixture checks actual window output, distance shimmer and reduced motion.
- Integrated sky/weather checks cover seasonal daylight, live/manual transitions,
  New Year rollover, stargazing weather suspension/restoration and mocked HKO values.
  The separate weather pass also verified real HKO/archive access from the browser.
- Aircraft fixtures load every real GLB, check dimensions, lights and airborne gear,
  and verify stable GPU counts after two complete replacement cycles. The city
  suite covers selection, delayed responses, failure/Retry, climb/camera controls,
  midnight flight and mobile controls at 390 px and 320 px.
- The island walkthrough covers all 11 priority destinations, walking at least
  1.5 m at each, mobile Peng Chau, bounded streaming and zero unexpected errors.

Native-size rendered evidence and detailed assumptions are linked from
[the main README](README.md), [island review](islands/README.md),
[aircraft review](AIRCRAFT-REVIEW.md), [night-cycle notes](night-cycle/README.md)
and [integrated browser evidence](integration/verification.json).

## Still required

This completes the imported-base integration milestone, not every city section's
architectural or gameplay review. The terrain is still sampled at 70 m; fine
shorelines, Tai O tidal channels/stilt details, raised walking decks and interiors
remain unfinished. Shui Hau's building source is visibly sparse. Most heights
are inferred or estimated, and the generic prop aircraft remains visibly low-poly.

The full original flight physics/cockpits, take-off/landing, UFO game, sound,
typhoons, tides, radar, remaining overlays, geolocation, sharing and other
original controls remain required. [FEATURE-PARITY.md](FEATURE-PARITY.md) and
[SECTION-CHECKLIST.md](SECTION-CHECKLIST.md) preserve that work. The original
`/index.html` remains available throughout the transition.
