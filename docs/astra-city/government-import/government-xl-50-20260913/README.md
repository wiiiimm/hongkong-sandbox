# Government XL batch of 50 — 13 September 2026

This bounded batch selected the 50 largest uninstalled XL government source models (10,000–49,999 triangles) that had a unique exact viewer match. All source recovery, conversion, identity, projection, foundation, terrain, runtime, neighbour and browser work was performed with deterministic local scripts. No per-model AI call, AI modelling, simplification or model-geometry edit was used.

| Final user status | Source models |
| --- | ---: |
| Installed | 9 |
| To do | 0 |
| Held for human decision | 0 |
| Held for AI processing | 0 |
| Held for unknown state / later local scripted processing | 41 |
| In process | 0 |

WEST9ZONE (`landsd/229310:0`) is installed from the byte-identical 30,359-triangle government mesh. A bounded source-terrain patch resolves the coastal terrain seam. The adjacent Florient Rise Tower 2 fallback remains visible and is supported by the unchanged source podium across 99.998% of its footprint.

1881 Heritage (`landsd/264745:0`) is installed from the unchanged government podium. Its separate basic tower remains visible; the source roof supports 100% of the tower footprint with a 4.7 cm overlap.

Seaside Sonata Tower 3 (`landsd/274763:0`) and Ocean Pride Towers 3 and 5 (`landsd/162512:0`, `landsd/219311:0`) are installed from their unchanged government meshes. Deterministic low-rim checks prove that their existing basic podiums support them, so no terrain or geometry edit was needed. All five installations passed staged and live desktop/mobile load, picking, collision, framing, fallback, retry, and retained-support visibility checks.

A second supported-tower pass installed the unchanged government mesh for `landsd/236065:0` and The Grandiose Blocks 1, 2 and 3 (`landsd/81678:0`, `landsd/81008:0`, `landsd/81151:0`). Their separate native podium sources were installed with them. Deterministic support-contact and staged/live browser gates passed without model-geometry changes.

The other 41 models retain their current viewer fallbacks. Their blockers overlap:

- 25 still need a deterministic source-assembly suppression or support map.
- 9 include below-grade source surfaces that need a source-preserving exception or terrain resolution.
- 6 need the stricter viewer identity/component policy resolved.
- 10 retain native terrain coverage, ground-contact, or below-grade diagnostics.
- 1 has an existing review that must be resolved before a new publication decision.
- 4 now have narrower third-pass blockers: a parent water-mask boundary, an unfilled parent-terrain hole, native-overlap evidence drift, or incomplete tower support with neighbour regression.

These are local pipeline/processing holds. None is classified as requiring AI modelling or a user decision. The exact per-model reason combinations and next steps are in `second-pass/final-script-pass/final-results.json.gz`.

The original 50-result checkpoint remains in pinned Neon job `9963d69f1a4c5c150cb119ba7409204fc9beca9c0ddb49ba2b4e85d9d7334585`. Third-pass snapshot `04d8813ba3dacd9e` records the earlier 5-installed/45-held checkpoint. Current review snapshot `e804b1639a55b028` records 9 installed and 41 held rows. Third-pass job `8a8785c85c67137ff82059ea857f957cfa3546393a463b4c48aabf8be0fe324c` stores the four refined local-compute blockers and confirms zero rows in process. The resulting public count is 408 ready government-source forms and 422 enhanced source forms overall.

Use `xl-final-sync.py` for the original checkpoint and `xl-third-pass-sync.py` for the refined terrain/support checkpoint. Resume held models by blocker group from the frozen final results and third-pass evidence; do not repeat source acquisition or completed diagnostics when their hashes still match.
