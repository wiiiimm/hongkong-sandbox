# Prepared Linear update — awaiting approval

The Linear save tool rejected the implementation report on 6 September 2026, stating that posting internal implementation details, counts, performance, commit references and limitations required approval for that payload and destination. These notes are local only. HKS-164 remains In Progress; HKS-116 remains In Progress. The following is the proposed text for the existing Astra milestone and its issues, not for the separate comparison milestone.

## HKS-164 — append report; move to In Review

Implemented on `codex/astra-hong-kong-city` at `c85ac0b`: all 2,408 government records in the supplied Mui Wo envelope, including temporary, open-sided and unnamed structures. The original envelope had 318 OSM forms. The source retains 1,967 recorded height differences and 441 explicit estimates. Overlapping OSM massing is replaced while retaining related names and uses.

Reused the official 5 m terrain and 275 individually matched government building models from tile 10-SW-12C through the existing city pipeline. Open-sided structures use roofs/posts. Source elevations and model/outline revision differences remain explicit. Source conversion, browser picking, day/night, mobile layout and before/after views were verified; the checkpoint passed 89 JavaScript and 10 converter checks. Google satellite and fully loaded Open3Dhk views were reviewed at all five requested Mui Wo areas.

Source, screenshots and validation are in `docs/astra-city/mui-wo-buildings/`. The bounded coverage fix is ready for review. Remaining local terrain disagreements include 194 outline roofs wholly below the sampled ground and 374 partly intersecting it; these are documented without silently altering source heights. Full Lantau acceptance remains open. No merge or deployment has occurred.

## HKS-116 and Astra milestone — append progress; keep In Progress

The regional checkpoint `5ae3900` adds 153 destinations across all 132 sections (196 total), 2,923 mapped local surfaces and mapped footbridge rendering. HKS-153 is already In Review.

The territory integration reuses the existing official government download and the Astra tile pipeline: 342,223 source IDs become 342,225 polygon components, plus 3,890 retained OSM forms, for 346,115 total forms across 452 tiles. All IDs, elevations, structure types, component geometry and overlap policy have independent verification. The Mui Wo 275 detailed models remain integrated. Lighting data streams alongside nearby tiles, with existing office/retail/home schedules and research evidence preserved.

Heisenberg handles detailed-model/reference and arrival review; Curie verifies complete source coverage, geometry and replacement; Kant verifies browser operation and performance; root integrates publication and use classification. Evidence is retained in `docs/astra-city/landsd-territory/` and `docs/astra-city/arrival-repairs/`. Complete local terrain, shoreline, architecture and connected-route acceptance remain open by region. Original-game feature parity remains open under HKS-117.


Final territory validation: all 102 city JavaScript checks pass; all 190 walking arrivals pass after six small mapped-path repairs. Browser checks pass in eight representative areas with zero errors, including source selection, collision-aware walking, night/layer behaviour and mobile layout. Local desktop median frame times are 16.6–16.7 ms (p95 18.1–19.0 ms). These are local observations; region-level terrain and architecture acceptance remains open.
