# Tourist model trial: visible models ready for review

The guarded publisher adds **1,078 detailed government models** (1,075 Central, three Mui Wo), totalling **6,501,220 compressed bytes**. These assets and three catalogues are now under `3d-viewer/city/data/official-models/tourist-trial-*`, included in the PR and served by the Vercel preview. R2 production offload is separate work in HKS-206.

[Open the interactive before/after gallery](comparison.html). Drag the slider to compare the actual viewer with and without the new catalogues. Click the links below each comparison for full-resolution PNGs. The baseline uses the same terrain and source records; only the three trial model catalogues are disabled. All nearby base/model requests are settled before capture. Thirteen locations were checked: ten representative Central models and all three Mui Wo additions.

| Trial boundary | Forms | Detailed before | Added | Detailed after |
|---|---:|---:|---:|---:|
| Central crop | 3,265 | 27 | 1,075 | 1,102 (33.8%) |
| Mui Wo section 10.6 | 2,371 | 1,572 | 3 | 1,575 (66.4%) |
| Tai O crop | 1,430 | 539 | 0 | 539 (37.7%) |
| Ngong Ping crop | 476 | 0 | 0 | 0 |

These trial boundaries differ from earlier regional detail denominators. Territory-wide totals remain 346,115 forms, now with 3,957 detailed forms (1,859 embedded + 2,098 progressive). No whole region has been signed off.

## Selection and held work

The existing cached source pipeline staged 2,875 candidates. The conservative trial requires successful shared-loader/source-surface/terrain checks, no sampled ground warnings, native model base within 3 m of surveyed base, and model top within max(5 m, 15% of surveyed height) of surveyed top. It preserves original source vertices, nodes, materials, coordinates and elevations. No terrain or basic building tile was edited.

**1,797 candidates remain held** (1,786 Central, 11 Mui Wo). Overlapping reasons are in `screening.json` and the per-UID `held.json.gz`: 779 survey/model height disagreements, 1,008 terrain-above-bottom flags, 687 ground-gap flags, four sampled highest roofs below terrain, and one missing drawn terrain surface. The two Martin House records have model heights well below surveyed base/top and current terrain; one unnamed Central record and one Mui Wo record also have buried sampled roofs. The Central–Wan Chai Bypass Middle Ventilation Building has a missing terrain ray. These are held source/terrain review cases, not automatically shifted models. Piers, overhangs and slopes can produce legitimate bottom/ground differences; conservative holds are not declarations of source defects.

No additional unambiguous cached candidate was found for Tai O/Ngong Ping. Cached absence does not prove government unavailability. The 2,440 uncached matches, 16 ambiguous model identities and 73 records without government identity remain in the earlier batch report. Detailed models are separate from the full basic-building coverage.

## Verification

- Vercel preview for implementation `63a707c6` serves all three trial catalogues/1,078 models. Six sampled remote GLBs match expected compressed sizes and SHA-256, with correct gzip content handling. See `deployment-verification.json`; browser/GPU acceptance below was performed locally.
- 228 city tests, 20 inventory/batch/policy tests and three existing guarded-publisher tests pass. An actual terminated worker is recovered after simulated lease expiry; unchanged work is reused. The existing publisher's injected failure test verifies rollback.
- Every added file passes its SHA-256/size checks. Every new source UID, CSUID, surveyed base/top and retained fallback is verified; no duplicate progressive models. Original terrain, source tiles, tile counts and prior catalogue entries remain unchanged. See `publication-verification.json`.
- Actual Chrome checks passed at ten Central and three Mui Wo buildings: source picking/collision, retained surveyed heights, current terrain agreement and bounded model streaming. Day/night and 390 px mobile views pass with no page/shader/HTTP errors or horizontal overflow.
- Both areas pass walking arrival, Fly-menu aircraft selection and forward flight without collision. Injected model-download failures preserve the basic form; Mui Wo explicitly verifies that fallback is visible/pickable before Retry restores the detailed model.
- Representative frame samples: median about 16.7 ms before/after; p95 about 16.7–16.8 ms. These are desktop Chrome and mobile viewport emulation, not physical-phone or network performance guarantees. Detailed-model GPU/CPU cache budgets remain enforced.
- Visual review confirms more detailed roof/crown/setback geometry, including AIA Central and the Central Government Offices. These are untextured government forms with procedural city windows. A source name can refer to a building part (including the sampled Helena May part), not the complete landmark. No exhaustive architectural acceptance is claimed.

## Reproduce or continue

`source-scripts/city/building-batch/publication.py` prepares the conservative subset and invokes the existing island-detail guarded publisher. Its plan is bound to validation/source hashes and refuses stale inputs. Run preparation against the recorded pre-publication snapshot, not after these models have already been installed. Repeated publication refuses changed inputs/destination collisions rather than silently adding duplicates.

```sh
python source-scripts/city/building-batch/publication.py prepare
python source-scripts/city/building-batch/publication.py publish
python source-scripts/city/building-batch/publication.py publish --apply
python source-scripts/city/building-batch/verify_publication.py
node source-scripts/city/building-batch/browser.mjs before
node source-scripts/city/building-batch/browser.mjs after
python source-scripts/city/building-batch/write_review.py
```

Set `AREA=central` or `AREA=mui-wo` for a targeted browser rerun; area-specific outputs get a matching suffix. The committed Central outputs are `browser/before` and `browser/after`; the additional Mui Wo outputs are `browser/before-mui-wo` and `browser/after-mui-wo`. Local SQLite/cached candidates remain ignored; deployed approved GLBs and catalogues are tracked. Reports distinguish sampled placement screening, representative browser review and unresolved architecture/source work.

HKS-203/204 are ready for user review of this bounded trial. HKS-202 source acquisition and HKS-205 wider rollout remain open/gated; HKS-206 handles production R2 delivery. This is a feature-branch preview publication, not a production release.
