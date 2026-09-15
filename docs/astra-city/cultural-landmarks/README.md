# Space Museum and Cultural Centre — HKS-207

This bounded pass adds **10 native government models**: three Space Museum parts and seven Cultural Centre/podium parts. The Space Museum dome and Cultural Centre's distinctive roof replace generic extrusions. Their two opaque shells opt out of invented procedural window grids; other buildings retain the existing city lighting. Original source materials and geometry remain intact.

The original eight-group tourist trial did **not** select these two landmarks. Their government data was already cached; omission from the processing selection explains the gap. This explicit follow-up includes the main Cultural Centre mesh under its source name **Auditoria Building**, not just records named Cultural Centre.

[Before/after comparisons](comparison.html) · [Counts](coverage.json) · [Installed browser evidence](browser/after/verification.json) · [Source provenance and commands](../../../source-scripts/city/cultural-landmarks/README.md)

## Accounting and limitations

- 16 source parts: all three museum parts detailed; seven of 13 Cultural Centre/podium parts detailed. Six open-sided canopy identities lack separate exact-reference government models. Actual auditorium roof triangles project over 84–94% of those footprints, but this is not proof of identity equivalence; their fallback records remain.
- Model payload: **825,208 compressed bytes**, **29,699 triangles**, reused from sheet 11-SW-4D revision 2025-12-22. No new model downloads or AI processing calls.
- Existing surveyed heights and all base forms are preserved. Native dome/west-wing roofs exceed their separate footprint survey tops; native roof geometry is retained instead of flattened.
- Terrain remains unchanged at the existing 5 m resolution. The raised restaurant has supporting podium triangles. Small podium/gallery substructures intersect terrain locally. Studio Theatre retains a small foundation-edge depression also present in native terrain; this is documented in the source reports, not silently flattened.
- Fixed **1× vertical scale** throughout. No epic-mountain multiplier, native geometry shift or second terrain-elevation addition.
- These are non-textured government meshes. Source geometry and recognisable silhouettes improve; architectural finishes, six canopy identities and broader Kowloon route/section acceptance remain open. No whole-region completion claim.

## Validation

All ten models pass the shared native loader, surveyed-field preservation, source picking and triangle collision checks. Browser views cover all ten, daytime/night, mobile viewport, walk/Fly entry and failed-load fallback/Retry. Final after evidence uses installed assets (`live: true`), without staged model or terrain responses. The material opt-out is covered by the official-model tests; existing default lighting remains enabled. Mobile measurements are desktop Chrome viewport emulation, not physical-phone performance certification.

Executors: `kowloon_cultural_models` acquired/audited sources; Root reviewed materials, placement, integrated, tested and published to the Astra feature branch. User review is tracked in HKS-207 under HKS-125. Draft PR #298; R2 delivery remains HKS-206, with no production release here.

## Reproduce

From the Astra worktree, use the existing Python environment for acquisition/source geometry scripts. Run acquisition, candidate validator and contextual audits before preparing a review. The publisher is intentionally not idempotent: it rejects an already installed catalogue or changed reviewed inputs.

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/cultural-landmarks/acquire.py
node source-scripts/city/building-batch/validate_candidates.mjs --candidates source-scripts/city/cultural-landmarks/compact
/tmp/astra-city-venv/bin/python source-scripts/city/cultural-landmarks/canopy_audit.py
/tmp/astra-city-venv/bin/python source-scripts/city/cultural-landmarks/support_context.py
/tmp/astra-city-venv/bin/python source-scripts/city/cultural-landmarks/studio_terrain_context.py
python3 source-scripts/city/cultural-landmarks/review.py prepare
REVIEW_CONFIG=source-scripts/city/cultural-landmarks/browser-config.json node source-scripts/city/building-batch/browser.mjs after
python3 source-scripts/city/cultural-landmarks/review.py publish
python3 source-scripts/city/cultural-landmarks/review.py publish --apply
python3 source-scripts/city/building-batch/inventory.py
REVIEW_CONFIG=source-scripts/city/cultural-landmarks/browser-config-live.json node source-scripts/city/building-batch/browser.mjs after
python3 source-scripts/city/cultural-landmarks/report.py
```
