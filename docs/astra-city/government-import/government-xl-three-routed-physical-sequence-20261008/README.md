# Three exact routed XL originals — complete physical checks

Codex, 8 October 2026, HKS-203. All three physical checks are complete and their exact results and evidence hashes have been verified against Neon. Zero installations. Original models and acceptance limits are unchanged.

| Source | Result | Neon job |
|---|---|---|
| Olympian City Two (landsd/265851:0) | terrain-construction-guard:('Requires retained native patch handling', ['city/data/government-native-229310-0.json', 'city/data/government-native-239397-0.json']) | `15c964637de0fb4b95d1469d766da7d3b4a9567443a5c837b52f31174b09c90c` |
| China Ferry Terminal (landsd/285642:0) | sampled-terrain-above-model-bottom; terrain-intersects-source-over-0.5m; terrain-regresses-neighbour:landsd/168176:0; terrain-regresses-neighbour:landsd/238208:0; terrain-regresses-neighbour:landsd/238209:0; terrain-regresses-neighbour:landsd/239018:0; terrain-regresses-neighbour:landsd/239238:0; terrain-regresses-neighbour:landsd/239450:0; terrain-regresses-neighbour:landsd/239862:0; terrain-regresses-neighbour:landsd/250396:0; terrain-regresses-neighbour:landsd/252498:0; terrain-regresses-neighbour:landsd/277648:0; terrain-regresses-neighbour:landsd/282670:0; terrain-regresses-neighbour:landsd/282676:0; terrain-regresses-neighbour:landsd/336540:0; terrain-regresses-neighbour:landsd/336541:0; terrain-regresses-neighbour:landsd/81118:0; terrain-regresses-neighbour:landsd/85626:0; whole-source-foundation | `87b47edd4aa8b8e5e7d4818946853db6e98b778bb53b1b92082e767e26745597` |
| Rooftop Garden (landsd/222781:0) | sampled-terrain-above-model-bottom; terrain-intersects-source-over-0.5m; terrain-regresses-neighbour:landsd/191831:0; terrain-regresses-neighbour:landsd/191861:0; terrain-regresses-neighbour:landsd/198900:0; terrain-regresses-neighbour:landsd/323954:0; terrain-regresses-neighbour:landsd/336669:0; terrain-regresses-neighbour:landsd/336670:0; terrain-regresses-neighbour:landsd/336671:0 | `e29ea278c70ee94442f0baaa34e85822fc0398999f667a73eadf517f8d67f681` |

Olympian City Two needs retention of two existing disjoint terrain patches. Its separate fresh run is `government-xl-olympian-two-multi-retained-terrain-20261008`; verify the actual process/result before reporting activity. China Ferry Terminal and Rooftop Garden retain actual terrain burial/neighbour conflicts. Neither failure establishes corrupted source data or a need for AI modelling.

Full indexed XL remains 521 total, 197 installed-verified and 324 remaining. A physical-phase result is not installation credit. No historical Lantau map imagery was used.
