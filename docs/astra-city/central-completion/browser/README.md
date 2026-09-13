# Central and corridor model acceptance — HKS-193

Astra/Kant verified the integrated city in local Chrome 152 with actual WebGL on 7 September 2026 (HKT). All 37 published Central/corridor models passed. HKS-193 remains in progress for geographic placement and continuous public routes.

`verification.json` records the complete functional run: original UID/source-card clicks, unchanged recorded HKPD elevations, indexed native geometry, compiled shared night-shader uniforms, precise source-face collision, above-roof clearance, and model budgets. The deliberate Blue House download failure left the original outline available; the existing Retry control then loaded the exact model successfully. There were no page or shader errors.

`exports-verification.json` independently confirms that an already selected fallback card changes from `HEIGHT` to `OUTLINE HEIGHT` after Retry, without another click or camera move. Its clean exports use actual source-face visibility to choose unobscured camera views. Buildings and terrain are never hidden for the images.

## Measured performance and mobile scope

| Viewport | Local startup | Frame median | Frame p95 | Maximum sampled model reservation |
| --- | ---: | ---: | ---: | ---: |
| 1440 × 1000 | 3.16 s | 16.7 ms | 16.8 ms | Desktop profile enforced |
| 390 × 844 | 2.92 s | 16.7 ms | 16.8 ms | 107,867,236 bytes |
| 320 × 844 | 2.90 s | 16.7 ms | 16.7 ms | 107,980,804 bytes |

Each timing sample covers 120 animation frames. Mobile checks use touch-enabled narrow desktop Chrome contexts, not physical phones, and are not a sustained thermal/heap benchmark. They visit HSBC, Bank of China Tower, HKCEC and Western Market at night. The observed maximum was six resident models and 256,088 triangles, within the mobile limits of 24 models, 450,000 triangles, 48 MiB source geometry and 128 MiB total reserved model memory. The reservation includes conservative collision/index costs; it is not a measured browser heap total. Opening controls caused no horizontal overflow at either width.

The application catalogue now contains 718 models because the separately verified Pui O package is also published. These checks exercise the 37 Central/corridor entries and confirm that the wider catalogue does not trigger eager loading of every model.

## Source placement findings

Every visit records current terrain height/resolution, model source bounds, original base/top, and terrain differences at native vertices within 1 m of the source minimum. These measurements are diagnostics, not proof that every low vertex should lie on the ground: native basements, slopes and separate source podiums can legitimately differ.

Retained official support forms remain beneath the corresponding exact UID replacements:

| Model | Retained form | Original base–top (HKPD) |
| --- | --- | ---: |
| Shun Tak Centre / West Tower | `landsd/264206:0` | 4–21.6 m |
| One IFC | `landsd/232441:0` | 3.5–33.9 m |
| Hopewell Centre | `landsd/334311:0` | 6.5–56.3 m |

Hopewell's native model begins at 25.146 m and overlaps its separate podium vertically; no source component was deleted to conceal that composition. None of the 37 records received a new illustrative foundation or a terrain-based height shift.

Unresolved local intersections are explicit:

- The Center's lowest 1 m of native vertices lie 2.32–2.96 m below the current 5 m terrain.
- Blue House `landsd/180764:0` has corresponding differences of −2.65 to −2.31 m; components `145002` and `180759` also have partial intersections.
- Cheung Kong Center's podium/ancillary components cross sloping terrain, with local minima near −9 m and medians around −2.39/−3.85 m.

Recorded source elevations remain immutable. These areas need source ground/entrance review before approving walking routes. Native models are untextured, with illustrative materials/windows; coarse or faceted source roof shapes are retained rather than smoothed into invented geometry.

## Inspected exports

The final PNG files themselves were opened and visually checked, including:

- `clean-desktop-B344751569101063C0.png` and `clean-desktop-hsbc-night.png`: HSBC structure and night presentation without the selection wireframe.
- `clean-desktop-B342131624601063C0.png`: One IFC and surrounding retained forms.
- `clean-desktop-B336871654501063C0.png`: Shun Tak's detailed upper form above the retained podium.
- `clean-desktop-B357141507201063C0.png`: Hopewell and its surrounding hillside.
- `clean-desktop-B358761603301063C0.png`: HKCEC and the waterfront.
- `clean-desktop-B335321647401063C0.png`: Western Market's native roof and façade.
- `clean-mobile-390-B335321647401063C0-night.png` and `clean-mobile-320-B344751569101063C0-night.png`: narrow-screen night presentation with the existing control dock.

Selected-card exports are retained separately. The existing yellow source-edge highlight is dense on HSBC; the clean images show the actual model clearly. The first pass stopped after six successful models because its single camera angle could not find an unobscured podium click ray. `first-pass.json` preserves that test-fixture failure. The corrected test searches real camera angles and `--resume` retained the six completed checks. No production geometry was changed for this correction. Clean-camera exports were subsequently recaptured after actual image inspection found neighbouring buildings obscured two initial views; the final images preserve all surrounding geometry.

## Reproduction

Run from the Astra worktree while its static preview is available and no other browser benchmark is active:

```sh
node 3d-viewer/city/tests/official-models-browser.mjs
node 3d-viewer/city/tests/official-models-browser.mjs --exports
```

`CITY_URL` and `CHROME_PATH` can override the local defaults. `--resume` preserves successful desktop entries from the immediately preceding report while continuing untested models; use a normal run for a fresh complete acceptance. The script adds a test-only served-module inspection hook for camera framing and state. Picking, clock controls, source cards and Retry use the existing application handlers. No elevated/public walking route is approved by this model test.
