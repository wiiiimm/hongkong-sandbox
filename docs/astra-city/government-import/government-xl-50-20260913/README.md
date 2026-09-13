# Government XL batch of 50 — 13 September 2026

This bounded batch selected the 50 largest uninstalled XL government source models (10,000–49,999 triangles) that had a unique exact viewer match. All source recovery, conversion, identity, projection, foundation, terrain, runtime, neighbour and browser work was performed with deterministic local scripts. No per-model AI call, AI modelling, simplification or model-geometry edit was used.

| Final user status | Source models |
| --- | ---: |
| Installed | 1 |
| To do | 0 |
| Held for human decision | 0 |
| Held for AI processing | 0 |
| Held for unknown state / later local scripted processing | 49 |
| In process | 0 |

WEST9ZONE (`landsd/229310:0`) is installed from the byte-identical 30,359-triangle government mesh. A bounded source-terrain patch resolves the coastal terrain seam. The adjacent Florient Rise Tower 2 fallback remains visible and is supported by the unchanged source podium across 99.998% of its footprint. Staged and live desktop/mobile browser checks passed, including load, picking, collision, framing, fallback and retry.

The other 49 models retain their current viewer fallbacks. Their blockers overlap:

- 31 need a deterministic source-assembly suppression map.
- 9 include below-grade source surfaces that need a source-preserving exception or terrain resolution.
- 10 need the stricter viewer identity/component policy resolved.
- 14 have native terrain coverage, ground-contact or below-grade diagnostics.
- 1 has an existing review that must be resolved before a new publication decision.

These are local pipeline/processing holds. None is classified as requiring AI modelling or a user decision. The exact per-model reason combinations and next steps are in `second-pass/final-script-pass/final-results.json.gz`.

All 50 final results were written to and read back from the pinned Neon database under completed job `9963d69f1a4c5c150cb119ba7409204fc9beca9c0ddb49ba2b4e85d9d7334585`. Review snapshot `7e5ad5d98b43c2a4` records the 49 held rows, while WEST9ZONE’s installed evidence is preserved in `second-pass/west9zone-install/installed-acceptance.json`. The resulting public count is 400 ready government-source forms and 414 enhanced source forms overall.

Use `xl-final-sync.py` for idempotent state verification. Resume held models by blocker group from the frozen final results; do not repeat source acquisition or completed diagnostics when their hashes still match.
