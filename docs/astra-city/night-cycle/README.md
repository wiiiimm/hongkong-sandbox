# The city goes to sleep

Created by GPT-6 Astra, 6 September 2026, on the isolated comparison branch.

Every building form uses the same 24-hour clock, with per-building and per-window
variation that stays stable through tile reloads. Windows fade independently as
activity falls, instead of globally dimming all windows together. Warm home lights
and cooler office lights are mixed; a soft façade glow suggests light spill.
At distance the shader averages window coverage to reduce aliasing. Roads and
bridges retain illustrative warm pools of street light overnight; rural footpaths
are not illuminated by this layer. Lighting uses the existing merged geometry
and shared material uniforms, without adding a point light for each window.

## Simulated activity

These are artistic schedules, not measured Hong Kong occupancy. Mapped building
use chooses the profile where available; unspecified uses get a mixed profile.
Roof shapes, exact window placement and luminaire positions are not surveyed.

| Time | Homes | Offices / commercial | Overnight uses | Mixed / unknown |
| --- | ---: | ---: | ---: | ---: |
| 20:00 | 84% | 57% | 93.5% | 77% |
| 00:00 | 44% | 18% | 72% | 32% |
| 02:00 | 16% | 7.5% | 48% | 13% |
| 04:00 | 6% | 3.5% | 26% | 6.5% |
| 06:00 | 30% | 18% | 45% | 23% |

These are nominal window activation thresholds, with deterministic variation of
up to 20% by building and smooth per-window transitions. They are not displayed as
population statistics. Hospitals/hotels and similar mapped uses retain a larger
share of lit windows. All profiles reach their minimum at 04:00. Ambient lighting
also falls towards 04:00 but stays above zero so walking and flight remain usable.
Early risers begin waking after 04:00; illustrative dawn runs from 05:30 to 07:12.
The original game's accurate sky/time and live weather remain separate parity work.

## Controls

Use the full-day slider or the **20:00**, **00:00** and **04:00** shortcuts under
Light & Atmosphere. **Time lapse** advances one simulated hour per eight seconds
of animation time, wraps midnight and can be paused. It starts paused. Manual
scrubbing or choosing a preset pauses it. The help dialog and a hidden document
pause advancement. New districts inherit the current clock immediately.

## Verification

```sh
npm --prefix 3d-viewer/city test
npm --prefix 3d-viewer/city run test:night
```

The focused browser test compares the same Kowloon camera at six times. It reads
pixels directly from the rendered scene (without UI) and verifies decreasing
bright-pixel counts and luminance to 04:00, surviving lights and visible surfaces,
then returning daylight. Pixel counts are image checks, not a count of individual
windows or buildings. It also exercises midnight time lapse, pause, streamed
Tung Chung, night walking, mobile presets and native-resolution PNG export.

`verification.json` contains observations and test results. PNGs here are direct
browser captures at their filename dimensions; `night-postcard-390x844.png` is the
actual exported canvas PNG, whose dimensions are checked from its file header.
All imagery uses the project's existing attributed terrain and OSM building
sources. No reference maps or original-game files were changed.
