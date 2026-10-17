# Cached model batch — 7 September 2026

Root reused 77 retained staged manifests and the original government decoder/exact-attribute packer. No downloads or AI calls. The source SHA-256 and government identity/footprint checks staged **2,875 candidates**: **2,861 Central**, **14 Mui Wo**. Tai O and Ngong Ping gained no unambiguous candidates from these retained manifests. Trial membership remains 7,542 buildings; its area boundaries differ from previous regional percentages.

## Measured result

- 5,404 jobs complete; 2,875 candidates, 2,440 absent from retained staged models, 16 ambiguous model identities, 73 without government identity. Cached absence is not government unavailability.
- Final source stage: 66.60 s wall time; 34,826,020 compressed bytes; 14 existing compact assets reused. No new live models.
- Unchanged repeat: all 5,404 jobs reused, zero new jobs; 2.24 s including source/output hash checks.
- 17 inventory/selection/runner/packer tests pass. Coverage includes identity/hash/path/resource guards, exact shared packing, corrupt derivative recovery, source-input invalidation, lease ownership, interruption and overlap deduplication.
- Actual current-tile/shared-loader validation: 2875/2,875 model loads accepted; 2874 passed the combined source roof picking/collision and terrain checks; 1 explicit exception. Runtime-check loop 63.39 s; peak process RSS 651,280,384 bytes. CPU evidence only.
- 2874 rendered-terrain rays agree with the sampler within 0.004 m. One ray found no drawn terrain beneath the Central–Wan Chai Bypass Middle Ventilation Building (`landsd/335495:0`). This remains a review exception.
- Fresh overlapping terrain diagnostics: 4 sampled highest roofs below terrain; 1008 sampled terrain above model bottom; 687 sampled gaps below model bottom. Bottom/ground differences need context for slopes, piers and overhangs. None automatically changes a source height or approves placement.

## Review and reproduction

[Commands and limits](../../../../source-scripts/city/building-batch/README.md). The full catalogue, source matching proof, exceptions and per-model validation report are deterministic gzip JSON snapshots beside this file. Summary reports stay plain JSON. The 34.8 MB of candidate assets and SQLite ledger remain ignored under `source-scripts/city/building-batch/local/`; scripts reproduce them from retained sources. The full catalogue is a review inventory; `catalogue-index.json` in local outputs lists three runtime-compatible catalogues of up to 1,024 entries.

The validator exits 1 when exceptions remain; that is the intended gate, not permission to publish around them. Original geometry, elevations and materials are unchanged. No city screenshots or GPU/mobile performance are claimed in this CPU checkpoint. HKS-202 remains In Progress for bounded source acquisition; HKS-203 remains In Progress for contextual placement review, browser acceptance and guarded publication. HKS-204/205 remain gated. Live coverage and region readiness are unchanged.
