# Mui Wo government model remainder · 14 September 2026

This frozen pass covers the 23 government models left by the Lantau inventory outside the already installed Mui Wo set. It uses exact Lands Department assets and source TINs with local scripts only.

## Terminal result

- 23 checked
- 7 installed and live in the feature-branch viewer
- 16 held for a later local source-terrain/contact pass
- 0 held for AI
- 0 held for a user decision
- 0 in process
- 0 building geometry edits and 0 AI modelling calls

The seven installed UIDs are `landsd/192816:0`, `landsd/195736:0`, `landsd/257154:0`, `landsd/299367:0`, `landsd/299375:0`, `landsd/299376:0`, and `landsd/299384:0`.

The sixteen holds and their measured reasons are recorded per UID in `resolution/final-results.json.gz`. Nine have native source surfaces below the model base (one of those also lacks complete native terrain coverage), and seven do not establish ground contact.

## Verification

The installed subset passed exact ID/CSUID matching, unique viewer matching, source hash checks, all-vertex/triangle-centre/low-edge terrain contact, mobile runtime budgets, loader/picking/collision checks, 32-form terrain-neighbour checks, and staged/live desktop/mobile day/night browser checks. Both terrain refinements preserve their outer seams and the parent water mask. The eastern refinement retains current terrain beneath two unrelated basic buildings and blends to the source TIN outside a three-metre collar.

Neon job `dd04409541613296ce49fbdd0d3fa6418393fdb6683aa411fa43091fa1ed8d41` stores all 23 terminal outcomes under review snapshot `a32a426fe241cd0b`.
