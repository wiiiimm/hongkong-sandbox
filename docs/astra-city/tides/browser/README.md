# City tide and wave browser verification

The primary Astra agent ran `node 3d-viewer/city/tests/tides-browser.mjs` against the actual city at `http://127.0.0.1:4176/city.html?district=muiwo`. All six check groups passed with zero page, console or shader errors. The browser was closed after the run.

- Manual −1 m and +4 m HKPD levels visibly changed 84,535 canvas pixels at the same Mui Wo camera. Low water remains above the renderer's −4 m seabed. All three ferry waterlines follow the rendered sea level.
- The high-tide walking arrival stays outside buildings and within the explicit 20 cm shallow-wading allowance. The captured arrival is at 3.833 m with water at 4 m; it is not claimed to be dry. Separate focused tests cover rejection of deeper entry and retreat towards shallower ground after water rises.
- Live mode requests yesterday/today/tomorrow for Cheung Chau and Quarry Bay, converts source CD heights to HKPD correctly, displays the 24-hour graph/source/trend, and locks manual tide input.
- Stargaze suspends water changes; leaving Live restores the saved 0.65 m manual level exactly.
- Wind-driven waves animate; Reduced Motion freezes their movement.
- Tide controls fit both 390 px and 320 px viewports without horizontal overflow.

HKO weather, wind and tide requests are explicit deterministic fixtures with the real API schemas. The sine-generated tide heights are test values, not the day's real tide. Source fixtures and datum validation are separately documented in [the restoration notes](../RESTORATION.md). `verification.json` records the intercepted URLs and state.

At the unchanged 1440×1000 Mui Wo overview, 180 local frames measured **16.7 ms median / 16.8 ms p95**, with **91 draw calls and 2,378,853 triangles**. This was the reduced-motion default-state rendering probe on this machine; it is not a cross-device performance guarantee.

Saved final images were inspected for visible shoreline change, readable graph/units and mobile layout:

- [Low tide](muiwo-low-tide-1440x1000.png)
- [High tide](muiwo-high-tide-1440x1000.png)
- [Live prediction graph](muiwo-live-prediction-1440x1000.png)
- [Mobile controls](tide-controls-mobile-390x844.png)

The +4 m view deliberately exercises the manual simulation limit. Low-lying terrain can be covered by the single sea plane; this is not a hydraulic flooding forecast. The full city suite passes **128/128** tests after integration. The original viewer has its own [compatibility evidence](../original-browser/verification.json).
