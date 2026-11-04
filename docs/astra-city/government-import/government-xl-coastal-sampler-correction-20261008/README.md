# Coastal sampler correction — HKS-203

Codex, 8 October 2026. The production terrain sampler now follows actual rendered coastal slopes and mapped water cuts. Government model bytes, native poses, terrain mesh inputs and acceptance limits are unchanged. No historical map imagery or AI modelling was used.

## Proven defects and correction

The grid renderer already applies the land floor/seabed policy to vertices. The sampler incorrectly applied another 1.2 m floor after triangle interpolation, producing a phantom shelf over mixed coastal faces. The new regression fails on unchanged commit `f1f2a261` and passes after removing that second clamp. Walking now rejects the genuinely submerged slope.

The renderer also passes root hydro geometry to every regular terrain descendant. The sampler did not, so it queried regular land faces that had actually been clipped away in mapped channels. It now propagates the same hydro context through regular descendants, while complete native source meshes retain their actual heights above the bed. Original mapped-channel tests are unchanged; the Tai O display-height test now checks actual vertex y instead of repeating the erroneous extra floor.

## Verification

- All 319 city unit tests pass across 51 files; exact command, code hash and output hash are in `final-unit-tests.json`.
- Focused 1280×900 desktop and 390×844 mobile browser fixtures pass production renderer ray intersections, sampler heights, submerged-walk rejection, dry arrival and nonempty WebGL renders. Both exported PNGs were inspected for framing and legibility. This is not whole-city browser or model installation acceptance.
- Baseline coastal, hydro and Tai O failures are preserved. Earlier fixture browser timeouts were missing root shared rendering modules on the fixture HTTP server; final server serves those modules. A favicon 404 does not affect module loading or checks. Failed fixture metadata is retained.
- Final fresh physical checks for exact originals162768/285642/335494 are verified in Neon `2cc2e9492dff33508394401adba26b58072973b23b85961fadadba28f41b8d86`. All sampler disagreements resolve (maximum4.244e-7m), but each retains independent identity/contact/foundation failures. Zero newly installed.
- This correction evidence is verified in Neon `84616125d4635d6958ca09219ec4c13f32cf63bae2daf4c5eea2dacdf6854ca5`. The initial recorder attempt failed before result write because its reservation transaction needed dictionary rows; that attempt is terminal failed, and the corrected fingerprint is complete. Reservations are released.

Earlier three-source measurements remain historical under their intermediate runtime hash. `intermediate-geo.js.txt` archives the exact intermediate code. Do not rebind those old checks to the final sampler. Use `government-xl-three-final-coastal-sampler-rechecks-20261008` for final current measurements.

Full indexed XL remains **521 =197 installed-verified +324 remaining**; the original327-model goal remains open. Six prepared architectural/source-coverage reviews remain unapproved; no such review was started. Linear remains pending after the previously reported automatic approval rejection; no retry or bypass.

Reproduce unit verification with `node --test 3d-viewer/city/tests/*.test.js`. Browser capture runner requires a fresh output path:

```sh
node source-scripts/city/government-import/check-coastal-sampler-browser.mjs --out docs/astra-city/government-import/NEW-FRESH-BROWSER-PATH
```
