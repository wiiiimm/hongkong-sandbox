# The city goes to sleep

Created by GPT-6 Astra, 6 September 2026, on `codex/astra-hong-kong-city`.

Every building uses the same 24-hour clock, with deterministic building/window
variation that survives tile reloads. Homes, offices, retail and overnight uses
follow distinct schedules. Window coverage is averaged at long distances to
reduce aliasing. Roads and bridges retain warm street lighting overnight; rural
footpaths are not illuminated by this layer. Existing merged geometry and shared
uniforms drive the effect without a point light for each window.

## Circular 24-hour clock

Drag or tap the clock under **Light & Atmosphere**: midnight is at the top,
06:00 on the right, noon at the bottom and 18:00 on the left. The blue/gold ring
represents the illustrative night/day cycle. Pointer movement selects five-minute
steps and wraps continuously across midnight. **Set time** accepts any minute.

Keyboard: arrows change 15 minutes, Shift+arrows five minutes, Page Up/Down one
hour, Home midnight and End 23:45. The focused dial announces the full time and
city phase. The separate time input provides a familiar accessible alternative.

The **20:00**, **00:00** and **04:00** shortcuts remain. **Time lapse** advances
one simulated hour per eight seconds of animation time, wraps midnight and starts
paused. Manual selection pauses playback. Help and a hidden document pause
advancement. New city sections immediately inherit the current clock.

## Simulated activity

[Area research and classification provenance](AREA-RESEARCH.md) distinguish sourced
building/land uses from artistic occupancy assumptions. All current 42,892 forms
have an activity entry; uncertain classifications are identified in the inspector.

| Time | Homes | Offices / daytime | Overnight uses | Mixed / unknown | Retail |
| --- | ---: | ---: | ---: | ---: | ---: |
| 18:00 | 60% | 86% | 84% | 74% | 94% |
| 20:00 | 87% | 68% | 92% | 78% | 93% |
| 21:00 | 90% | 34% | 92% | 78% | 93% |
| 22:00 | 83% | 16% | 88% | 70% | 88% |
| 00:00 | 48% | 8% | 65% | 34% | 14% |
| 02:00 | 16% | 4% | 42% | 12% | 4% |
| 04:00 | 5.5% | 2.5% | 24% | 4.5% | 2% |
| 06:00 | 30% | 14% | 42% | 20% | 7.5% |

These are nominal activation thresholds with up to 20% building variation and
smooth window fades, not measured occupancy or population statistics. All profiles
reach their minimum at 04:00. Ambient light remains sufficient for exploration.
Illustrative dawn runs 05:30–07:12. Exact astronomy and live weather are still
required by the [original-game parity plan](../FEATURE-PARITY.md).

Nearby windows stay steady. Distant lights receive subtle independent atmospheric
shimmer and gradual attenuation, with a switch and reduced-motion support. The
animation clock is separate from city time, so changing time does not randomly
reshuffle the windows or their shimmer phases.

## Verification

Serve `3d-viewer/` locally on port 4176, then run from the worktree root:

```sh
npm --prefix 3d-viewer/city test
npm --prefix 3d-viewer/city run test:clock
npm --prefix 3d-viewer/city run test:lighting-render
npm --prefix 3d-viewer/city run test:night
npm --prefix 3d-viewer/city run test:browser
```

The 23 unit/data checks include all 1,440 valid input minutes, midnight wrapping,
profile continuity, source hashes and complete activity coverage. Clock browser
checks select all 24 hours, drag across midnight, use keyboard/exact entry/touch,
pause playback and change reduced-motion preferences while the page is open.

`render-verification.json` isolates actual WebGL façades with fixed geometry and
lighting. Nearby frames are identical; distant frames vary subtly; switching off
shimmer or switching to daytime restores identical frames. Actual rendered homes
brighten, offices dim first and shops stay active later.

`verification.json` compares the same Kowloon scene at six times, confirming fewer
bright pixels towards 04:00, surviving lights, visible surroundings and returning
daylight. It also covers streamed Tung Chung, walking at night, midnight playback,
mobile controls and PNG export. The wider browser suite exercises walking, flying,
search, layers, regional streaming and recovery from a failed tile download.

PNG dimensions appear in filenames. The postcard is the actual exported canvas
PNG, checked from its file header. `clock-mobile.png` is a native-resolution crop
of the mobile control. Imagery uses the existing attributed terrain and OSM
sources. No reference maps or original-game files were changed by this update.
