# Weather haze and sky clarity · HKS-195

Astra/root integrated the Weather control; Heisenberg supplied the bounded official visibility/AQHI adapter. The existing scene fog and catalogue-star shader are reused. The original game remains available.

**Weather → Haze & sky glow** adjusts background atmospheric attenuation and the illustrative night-sky response. Zero manual haze removes background distance fog in clear weather; deliberate rain/fog remain independently controlled. New visitors start at35%, clearer than the previous fixed atmosphere (equivalent to50%). The saved manual preference survives reload, including zero, with safe handling of unavailable storage.

With **Live · HKO**, fresh measured visibility from the nearest usable HKO reporting station controls fog directly. The disabled range shows the reported distance; **Use my haze setting** enables a visual override while the other live weather continues. Manual preference is never overwritten by arriving observations. Stargaze can use either observed visibility or that override; its existing rain/cloud suspension stays intact. Real feed timestamps do not advance with the city clock or timelapse.

The EPD AQHI source and original station catalogue are reused and displayed separately with station, general/roadside type and source time. AQHI is a health-risk index; it is not converted into metres of visibility or presented as a night-sky measurement. Sky glow and the conversion from visibility to rendering remain illustrative. Visibility is a station observation rather than a territory-wide survey; locations between stations can differ. See [feed provenance and verification](../air-visibility/README.md).

## Rendering

The existing FogExp2 is retained. In manual mode the prior30km background density is scaled by4×haze²; extra deliberate weather fog is added. In automatic mode density uses sqrt(−ln0.02)/reported_visibility, replacing the weather estimate rather than counting rain/fog twice. HKO's100m and50km reporting caps are labelled as bounds in the source readout; using the bound for rendering is an approximation. Star positions, catalogue geometry, astronomy, city time and light schedules do not change. Existing sky uniforms adjust the faint-star cutoff; background colour changes provide an illustrative night-glow response. Daylight, cloud cover and moon effects remain.

Visibility expires after30minutes and AQHI after90minutes, with5minutes of future-clock tolerance. Expired/unavailable visibility falls back explicitly to the saved manual haze and estimated weather fog; a stale station measurement remains labelled stale rather than becoming a fabricated zero. Each feed has independent error/retry handling, timeout, cancellation and station selection. Source errors do not disable the manual control.

## Verification

Commands from the Astra worktree:

```sh
node --test 3d-viewer/city/tests/atmosphere.test.js 3d-viewer/city/tests/air-visibility-data.test.js 3d-viewer/city/tests/weather.test.js 3d-viewer/city/tests/sky.test.js
node 3d-viewer/city/tests/atmosphere-browser.mjs
```

The final focused suite has37 tests. The actual city browser passes five grouped checks: scene fog and same-camera map comparison; fixed-time Stargaze comparison; mock HKO visibility/EPD AQHI with Live/manual/Stargaze transitions; saved zero/non-zero preferences through reload; and320/390px controls,44px targets, keyboard operation and no horizontal overflow. Desktop viewport1440×1000. Zero page errors. Actual rendering and exported images were inspected. Feed HTTP/CORS checks use real endpoints; deterministic browser source-transition assertions use labelled test fixtures. Physical mobile hardware and every district's atmospheric appearance are not claimed verified.

[Browser results](browser/verification.json) · [Map before-equivalent50%](browser/lantau-day-50.png) · [Clear map](browser/lantau-day-0.png) · [Heavy haze](browser/lantau-day-100.png) · [Clear sky](browser/night-sky-0.png) · [Hazy sky](browser/night-sky-100.png) · [Live observations](browser/live-visibility-and-aqhi.png) · [Mobile320px](browser/weather-mobile-320.png)

In the fixed Stargaze comparison, the catalogue visibility counter increases669→768 at the same date, camera and astronomical state. This is catalogue eligibility, not a pixel count or a prediction of naked-eye visibility. No geometry is added by the control.
