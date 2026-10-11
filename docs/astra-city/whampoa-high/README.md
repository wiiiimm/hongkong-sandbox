# Whampoa estates native high pass — HKS-226

Executor: GPT-6 Astra, High reasoning. Government native geometry reused unchanged; no bespoke texture creation or new government downloads. Feature-branch integration for review, not production deployment or a complete-neighbourhood claim.

## Source membership

Site 8 uses Gourmet Place / Whampoa Plaza, `landsd/324574:0`, CSUID `3769918450T20050430`. The operator's Gourmet Place and Screen World retail areas are not evidence for duplicate building geometry. Sources: [Gourmet Place](https://www.thewhampoa.com/en/store/detail-777.html), [Screen World](https://www.thewhampoa.com/en/store/detail-835.html), [Rating and Valuation Department address list](https://www.rvd.gov.hk/doc/en/urban_201504.pdf).

Site 12 uses all nine Bamboo Mansions towers plus shared podium `landsd/105379:0`, CSUID `3771318579P20060311`. The podium contains all nine tower footprints. The operator calls this retail area [Home World](https://www.thewhampoa.com/en/category/index-4.html). The distinct Site 10 WizZone podium `landsd/224899:0` contains five Banyan towers and is excluded. Original source naming, base/top attributes and exact matching IDs remain retained alongside descriptive labels.

11 source assets total **150,907 compressed bytes**. Cached non-textured government models from sheets 11-NE-21A/C, revision 27 October 2025, were restored using retained content-addressed R2 bundles. `source-scripts/city/whampoa-high/selected-sources.json` retains exact restore keys and checksums; private credentials and extracted caches are excluded from Git. [Government dataset](https://portal.csdi.gov.hk/geoportal/?datasetId=landsd_rcd_1742809441342_98380).

## Placement acceptance

Every native asset, node transform and surveyed height remains unchanged at **1× metres/HKPD**. Native model bounds and footprint height attributes are distinct; they are not forcibly equalised. Towers retain stepped bases on their actual source podium.

Triangle-level support checks use every unique low-rim vertex and nearest actual podium surface. Most points are within 0.5 m; four points across Blocks 1/5 exceed that tolerance, maximum 0.653 m. The evidence retains these exceptions rather than changing tolerance. Native assembly and visual inspection support preserving those source seams without inventing deformations. This is not structural engineering certification.

The old coarse ground buried lower visible surfaces. The bounded 1 m native terrain extension has 137,971 samples, complete native-source coverage, and preserves all 29,751 existing ship-patch samples exactly. Ten-metre boundary transitions join the parent ground and preserved ship patch. No water masks, building elevations or old ship vertices were changed. The guarded publisher validates non-overlap, alignment and old-sample identity.

After correction, zero upward-facing source triangles are wholly buried. One small downward-facing podium underside triangle at 6.057 m HKPD lies 0.40–1.03 m below ground and is retained as below-grade source geometry. Ten other models have no wholly buried triangle. See `support.json`, `surfaces.json`, `terrain.json` and `validation-patched.json` for source-level evidence.

## Browser and comparison

`staged/after/verification.json` checks all 11 native components for loading, source heights, source-surface picking/collision and rendered terrain/sampler agreement. Both section walk arrivals and propeller-flight smoke checks passed. Mobile viewport checks and deliberate asset failure/fallback/retry also passed. These are collision and control smoke checks, not exhaustive pedestrian routes or rooftop landing certification.

`live/after/verification.json` repeats these checks against the installed manifest and files; `comparison/verification.json` covers all five locations at 1440 px and 390 px. Actual PNG outputs are retained. Mobile measurements are desktop Chrome emulation, not physical-phone benchmarks. Windows reuse the existing illustrative city lighting; native government source colours are not photographic facade textures.

The standalone comparison retains all original basic/light geometry. Site 12 high includes the newly verified podium, so its ten-component assembly must not be marketed as an equal-component size comparison against the original nine-tower trial. Existing ship/Cultural Centre/Space Museum assets remain reused; Cultural Centre's six unmatched canopy forms remain outside this comparison.

## Reproduce and resume

From this feature checkout, use the model-improvement skill and pinned Neon/R2 setup. Reserve the 11 canonical UIDs before publishing or recording shared review results.

1. `python source-scripts/city/whampoa-high/restore.py --env-file PRIVATE_ENV_PATH` restores source bundles from R2.
2. `stage.py`, then `terrain.py`, reproduce candidates and native terrain extension (NumPy/Shapely and existing local building inventory required). These do not grant approval; keep the reviewed `approved/catalogue.json` and inspect output/hash differences before regenerating a publication plan.
3. Use the existing `building-batch/validate_candidates.mjs` with the candidate folder and `terrain-replacements.json`; `support.mjs` and `surfaces.mjs` retain diagnostic evidence. The replacement comparison assumes the pre-integration ship manifest entry; use the preserved parent/patch and original commit for a fresh before/after rerun after integration.
4. Guarded publisher: `model-integration-20260909/publish.py PLAN --receipt PRIVATE_RECEIPT --phase whampoa-estates-high` dry-runs; `--apply` installs validated scope. Already-installed source/terrain must not be overwritten by an unreviewed rerun.
5. Run `REVIEW_CONFIG=source-scripts/city/whampoa-high/browser-live.json node source-scripts/city/building-batch/browser.mjs after`, then `node source-scripts/city/whampoa-high/verify-comparison.mjs`.
6. `register.py --receipt PRIVATE_RECEIPT --commit COMMIT` appends an idempotent fenced review event; earlier light-trial history is retained. `building-progress/export.py --refresh` and `building-progress/generate.mjs` refresh the public count after accepted DB recording.

Runtime outputs are committed to the feature PR. The retained source bundles are on R2; this pass does not claim production runtime R2 publication.
