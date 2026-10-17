# Guarded lossy pilot — 12 October 2026

Executor: Codex. Thirteen installed sources, including Elements, Hong Kong Central Library, West Kowloon Station and Avalokitesvara Statue, were measured at three distinct tiers (39 derived files). No historical-map references were used. Originals and complete scene poses/materials remain unchanged.

| Candidate | Existing source gzip bytes | Candidate gzip bytes | Original triangles | Candidate triangles |
| --- | ---: | ---: | ---: | ---: |
| High | 13,079,010 | 7,390,730 | 496,913 | 496,913 |
| Balanced | 13,079,010 | 6,326,387 | 496,913 | 490,000 |
| Lightweight | 13,079,010 | 5,334,670 | 496,913 | 487,310 |

Every output passed independent viewer-decoder readback against its derived mesh. Position rounding created zero new collapsed faces, reversed faces or area from original degenerates. The guard protected 1,625 / 2,559 / 18,918 faces respectively; source positions are restored rather than dropping or inventing tiny geometry. Small files can grow due to codec overhead: 7 / 7 / 8 outputs were smaller, and every negative is retained.

The high candidate preserves all original vertices, unused vertices, face count and corner order. Balanced and lightweight use border-locked, extrema-pinned attribute-aware simplification and compact every attribute consistently. Requested triangle ratios (65% and 35%) are targets, not promises: source seams and error caps substantially limit achieved reductions. Simplifier error is a weighted absolute quadric estimate, not a Hausdorff or visual bound. Rounding errors use Float64 source node matrices; literal/GPU Float32 placement, current terrain/support, rendering, collision, mobile frame time and peak memory remain untested.

The source selection for this pilot was the earlier 4,272-source accepted cohort. The user subsequently authorised processing every installed source regardless of review flags. The complete cohort and verified database delivery are recorded separately in `../installed-enhanced-meshopt-variants-v2-20261012/`. No pilot output was published to the runtime catalogue.

Requests contain the original local workspace path; when reproducing elsewhere, replace that root prefix with the new repository root while preserving recipe/source hashes. Exact recipes, requests, raw results and content-addressed artifacts remain available for inspection.
