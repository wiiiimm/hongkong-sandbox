# HKS-214 — West Kowloon cultural model review

**Five native government model parts across four landmarks are approved for integration.** This review adds the source-backed exterior geometry and disables fabricated office-window grids on these cultural facades. The subagent did not publish the plan or alter viewer data.

Executor: Astra cultural model review subagent, 9 September 2026. Pinned candidate snapshot: `3887f2f23fbad306`. Exact source geometry stays at **1× metres/HKPD**. Total: **80,848 triangles / 1,812,443 compressed bytes**.

| Landmark | Exact source UID | Delivered review |
| --- | --- | --- |
| M+ Pavilion / Arts Pavilion | `landsd/168596:0` | Elevated exhibition volume, parapets and terrace/entrance detail; generic windows removed from mirrored/opaque shell |
| Xiqu Centre | `landsd/205817:0` | Curvilinear shell, shaped roof and corner openings; generic office windows removed from aluminium-screen facade |
| M+ | `landsd/279530:0` and `landsd/310908:0` | Podium/foundation and slender tower, native roof detail and undercroft; actual podium support proven; generic grids removed |
| Hong Kong Palace Museum | `landsd/283788:0` | Sculptural tapered envelope, facade recesses, stepped roof/terraces; generic grid removed |

## Source and placement evidence

All five have exact government CSUID matches and retained native model/source hashes in [source-identities.json](../../../source-scripts/city/cultural-model-review/source-identities.json). The runtime decoder verifies compressed hashes, geometry counts and complete transformed bounds against the source. No vertex, node transform, source elevation or source material bytes were changed.

The raised M+ tower is supported by the podium, not bare ground. **1,314 / 1,314** one-metre samples inside the actual tower footprint intersect native podium triangles within **0.0015–0.0028 m** of the tower's **32.297 m HKPD** bottom. Its roughly 26 m gap above terrain is therefore expected. [Triangle and terrain evidence](context.json).

The four ground-level parts have some lower source vertices beneath the current 70 m terrain. Maximum near-bottom intersections are 0.646 m (Pavilion), 0.706 m (Xiqu), 0.987 m (M+ podium) and 1.253 m (Palace Museum). No inspected vertex is more than 2 m below terrain. Fresh lower-angle views show viable exterior/ground relationships; no speculative elevation correction was applied. These small terrain residuals are recorded rather than hidden.

## Visual and interaction checks

- Five actual source models pass CPU decoding, native-surface picking/collision and rendered-terrain/sampler agreement.
- **24 final normal-scene captures**: desktop before, two desktop after angles, desktop night, and 390 × 844 mobile day/night for each landmark. **Four additional foundation views** inspect the lower geometry from the waterfront side.
- All five candidate IDs become active; native mesh picking succeeds; no browser errors, camera collisions or horizontal UI overflow. Normal exterior framing contains the full selected bounding box. Foundation views deliberately focus on lower geometry.
- The final southwest desktop day, mobile day/night and foundation images were inspected. Xiqu's northeast view has neighbour occlusion; the clear southwest and foundation views establish its visible exterior instead.
- The mobile official-model cache peaked at 31,640,556 resident bytes, within its existing 128 MiB budget; this is a bounded loading measurement, **not a real-device frame-rate or thermal benchmark**.

[Before/after review gallery](contact.html) · [Final browser report](browser/report.json) · [CPU validation](cpu-validation.json) · [Explicit per-part acceptance](visual-acceptance.json)

The initial wrong procedural-window captures remain under `browser-initial-window-stamps/` for comparison. The final `browser/` captures show `proceduralWindows: false` using the already-supported loader metadata; surrounding buildings keep their lighting. No shared renderer code changed.

## Architectural references and limits

The [M+ institutional building description](https://www.mplus.org.hk/en/the-building/) and [audio description](https://audioguide.mplus.org.hk/en/locations/audio-description-for-the-m-plus-building/) support the inverted-T podium/tower assembly, ceramic cladding and harbour-facing LED surface. The prepared geometry preserves those major volumes and its source-native openings. It does not invent a media display or additional glazing.

The [West Kowloon 2018 completed-facility report](https://webmedia.westkowloon.hk/documents/wkcda-cp-02-2018-eng-final.pdf) describes the elevated Pavilion and mirrored exterior. [Revery's completed Xiqu Centre project](https://reveryarchitecture.com/projects/xiqu-centre/) describes the curvilinear aluminium-fin facade and corner entrances. The [Palace Museum's building page](https://www.hkpm.org.hk/en/about/the-building) establishes the museum identity and architectural organisation. See [reference records](references.json).

This is approval of **available native exterior geometry and placement**, not photoreal finish, complete interiors, every nearby podium/annexe, walking routes, rooftop flight approaches, or whole-region completion. Native neutral materials remain; green ceramic colour, mirrored reflections, Palace Museum golden finish, fine Xiqu fins and source-authentic night illumination need separate material/lighting work. Disabling invented windows makes the shells quieter at night; it does not reproduce their real facade lighting.

## Root hand-off and reproduction

The guarded plan is [publication-plan.json](publication-plan.json); [guard.json](guard.json) pins the reviewed inputs, assets and evidence. Root applies the existing `island-detail-integration/publish.py` only after checking the guard, then verifies the installed routes and updates Neon/Linear. No R2 or live viewer write was performed by this subagent.

From the Astra checkout, with the restored pinned snapshot and existing pipeline dependencies:

```sh
# First claim all five complete building:landsd/<object>:0 keys using reservations.py.
python source-scripts/city/cultural-model-review/prepare.py
node source-scripts/city/building-batch/validate_candidates.mjs \
  --candidates source-scripts/city/cultural-model-review/candidates \
  --out docs/astra-city/cultural-model-review/cpu-validation.json
node source-scripts/city/cultural-model-review/context.mjs
node source-scripts/city/cultural-model-review/browser.mjs
CULTURAL_FOUNDATIONS_ONLY=1 node source-scripts/city/cultural-model-review/browser.mjs
# Inspect the fresh images and update explicit visual-acceptance.json before staging:
python source-scripts/city/cultural-model-review/prepare_publication.py
```

Use checkpoint heartbeats during interactive review. The current `reservations.py run` wrapper releases its group when the command ends; reacquire before further reserved work. Browser overrides use `CITY_BASE_URL`, `CHROME_PATH` or `CHROMIUM_EXECUTABLE_PATH`. Candidate/approved compressed assets are reproducible copies of the restored snapshot and excluded from Git here; their hashes and catalogues are tracked. No local SQLite writes occur.
