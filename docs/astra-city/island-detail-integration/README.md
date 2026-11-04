# Island government-model integration — HKS-192, HKS-170, HKS-171

Astra integrated **302 additional original government models**: 291 in Mui Wo, seven in Tai O and four in Pui O. Existing government/OSM footprints, native model geometry and recorded elevations remain intact. All 346,115 city forms remain; the 1,859 embedded models plus 1,020 progressive models now provide 2,879 unique detailed replacements across the city. Progressive budgets still determine what is resident on screen.

| Unchanged review area | Before | Available in viewer after integration |
| --- | ---: | ---: |
| Mui Wo, 2,408 forms | 1,327 / 55.1% | **1,618 / 67.2%** |
| Tai O two-sheet slice, 1,030 forms | 532 / 51.7% | **539 / 52.3%** |
| Pui O buffered slice, 919 forms | 681 / 74.1% | **685 / 74.5%** |

These are detailed-source coverage figures, not whole-region completion. Mui Wo's acquisition pass found 312 matches, but final placement review holds 21: seven material native roof/terrain conflicts and 14 unsupported elevated bases. Their basic forms remain visible. The other 291 passed the screen, including four valid towers on separately retained podiums. Small accepted native roof-edge differences are bounded and documented in [Mui Wo's placement evidence](../mui-wo-detail-completion/INTEGRATION.md); imported government models are not claimed to be perfectly surveyed architecture. Temporary/open-sided structures and unmatched source revisions account for most remaining coverage gaps. No inferred building is counted as a government model.

## Ground and source preservation

Seven nested terrain refinements use retained government TIN geometry, including one reused Mui Wo patch from the earlier b90c15f5 package. The other four old Mui Wo refinements remain staged. The renderer now omits covered parent cells across drawing chunks and renders each child once, matching the already-recursive walking sampler. Seven patches contain 17,477 sampling vertices; 1 m spacing is a sampling interval, not source survey accuracy. Existing coarse ground, coast/hydro and parent sample arrays remain unchanged.

Six existing terrain-estimated building bases follow the corrected ground. Every one has both recorded government base/top values null; their heights and source fields remain unchanged. Exact previous values, source bundle hashes and replacement values are guarded by the publisher. No native government model was lifted or reshaped. Remaining source/terrain disagreements retain explicit audit flags.

The Tai O Heritage Hotel is now visible with its native roof, colonnade and end structure instead of being buried by the coarse ground. Compare [before](browser/before/tai-o-landsd-211618-0-day.png) and [after](browser/after/tai-o-landsd-211618-0-day.png).

## Verification

- All **228 city tests** pass, including nested chunk boundaries and the existing source terrain, lighting, flight and navigation checks.
- Publisher tests cover identity rejection, successful preservation and an injected installation failure with rollback. Assets are prepared first, destination collisions rejected, and the manifest installed last.
- Actual complete terrain rendering: **35 rays**, each hits one surface agreeing with the walking sampler. Shared triangle-edge hits are avoided by non-grid-aligned probe positions.
- **2,764 records** in modified tiles compared with the pre-publication commit; every source/model/footprint field preserved, apart from explicitly allowed estimated bases and derived terrain diagnostics. Roads and parks remain unchanged.
- Actual Chrome browser: **18 models** (seven representative Mui Wo models and all eleven Tai O/Pui O additions), source picking/collision, native bounds/elevations, day/night, three mobile views, safe walking arrivals, Fly-picker entry and advancing flight. Deliberate model failure retains fallback and Retry restores detail. No page/shader errors.
- Progressive count, triangle and memory budgets pass. Desktop and mobile-sized Chrome runs measured approximately **16.7 ms median / 16.7–16.8 ms p95** frame intervals. This is not physical-phone thermal or heap validation.
- The subagents independently checked every acquired asset with the actual compact loader, source geometry and collision checks; their terrain packages include neighbour, seam and route evidence. Root reviewed publication code independently with the Pui O agent, addressed its findings, then verified the combined viewer.

[Combined CPU evidence](verification.json) · [browser evidence](browser/after/verification.json) · [publication/provenance](publication.json). Before images, extra Mui Wo correction views and after images are retained in browser/. Baseline views are separate from final acceptance.

## Reproduce

From the Astra worktree:

```sh
# For an unmodified parent checkpoint only; rejects repeated or stale publication.
python3 source-scripts/city/island-detail-integration/publish.py source-scripts/city/island-detail-integration/plan.json
python3 source-scripts/city/island-detail-integration/publish.py source-scripts/city/island-detail-integration/plan.json --apply
# Can be rerun after committing, using publication.beforeCommit for comparison.
node source-scripts/city/island-detail-integration/verify.mjs
node source-scripts/city/island-detail-integration/browser.mjs after
python3 source-scripts/city/island-detail-integration/test_publish.py
node --test 3d-viewer/city/tests/*.test.js
```

Serve 3d-viewer on port 4176 for browser checks. Original source archives, source hashes, rejected matches and acquisition inventories remain under the three area detail-completion packages. No historical map imagery was used or altered. Source geometry is attributed to Lands Department / HKSAR Government; OSM supplements and illustrative façade/foundation behaviour retain their existing attribution.
