# HKS-221 — scripted citywide audit

The corrected pipeline audited **346,115 source forms across 452 current tiles**. Full execution including initial Neon persistence took **234.985 seconds**; the unchanged run under another batch label took **27.102 seconds**, reused **346,115 cached results**, and performed **zero new terrain checks**.

Current source declarations contain 2,404 native-catalogue entries, 1,859 embedded models and 341,852 basic forms. Catalogue/embedded counts are not the separate manually installed-and-verified review ledger, and do not establish visual acceptance.

Terrain diagnostics found 25,302 envelopes with their base above every sample, 35,179 with roof below at least one sample, and 19,892 below every sample. Categories overlap. These are **source footprint-envelope review candidates**, not confirmed buried or floating native models: towers may have podium support and actual native roof shapes differ. No model was moved, downloaded, accepted or published.

All actual terrain checks use the existing exact sampler at source elevations. Self-intersection, native triangle/collision checks and visual inspection remain explicitly unperformed. Seven engine tests and five real pinned-Neon tests passed. The latter prove grouped transaction rollback when even one final lease expires after COPY.

See verification.json for exact hashes and the authoritative R2 archive root. The prior classification error is retained only as compact superseded provenance. Resume commands and implementation details are in source-scripts/city/citywide-audit/README.md. Use the pinned modelling branch; unchanged reruns reuse accepted results across batch names.
