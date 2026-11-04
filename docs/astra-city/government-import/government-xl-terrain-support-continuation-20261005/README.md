# Twelve more XL source holds — completed compute continuation

Codex root, 5 October 2026; HKS-203 / HKS-215 / HKS-199. This is fresh local
source/terrain/support work after the three earlier installations, not a repeat
of the frozen next-100 pass. No AI architectural review, geometry generation,
source elevation changes or acceptance tolerance increases were used.

**Zero new installations; twelve primary technical holds; zero in process.**
Fifteen exact original overlapping components were recovered and fully tested.
Two interfaces pass, thirteen fail; a passing interface alone is not installation.
Current XL352 remains **42 Installed / 310 Held**, independently checked against
current Neon review snapshot `b8d42e765476890d`. No viewer assets or progress change.

| Primary source | Current blocker | Completed work |
| --- | --- | --- |
| Coronation Circle 10664 | Seven overlapping-form/support migrations | Original terrain, complete foundation and runtime pass; seven exact original components recovered and tested |
| Stonecutters main pumping station 270142 | Source footprint identity | Exact source exists; detailed projection fails existing identity policy before terrain work |
| Royal Green Tower 3 11093 | Source footprint identity | Same exact-ID source; detailed projection fails existing identity policy |
| South Hillcrest 198440 | Source footprint/component identity | Detailed projection spills beyond the target into a related podium; existing identity policy fails |
| Two Harbourfront 118230 | Source clearance | Replacement Whampoa grid retains existing terrain; foundation and three neighbours pass, but source penetration is about 1.971m |
| Ching Hin House 26653 | Source clearance | Exact old native planes retained; all five installed native meshes and 25 neighbours pass, but penetration is about 0.753m |
| Hanford Plaza 276187 | Source clearance and nine neighbours | Four correct adjoining original quadrants resolve full source coverage; clearance and neighbour checks still fail |
| Sham Shui Po Park Swimming Pool 265480 | Source clearance/foundation and three neighbours | Original terrain/runtime checked; full foundation and clearance remain blocked |
| Market In 313033 | Source clearance and seven neighbours | Original terrain and complete foundation checked; clearance/neighbours remain blocked |
| Model 258470 | Five overlapping tower/support migrations | Original terrain/foundation pass; two already installed native meshes pass; five exact originals recovered and tested |
| West Kowloon Station Bus Terminus 255415 | One overlapping source and one disjoint neighbour | Original terrain/foundation/runtime pass; exact 231056 component recovered, with 57 unresolved interface samples |
| WEST9ZONE component 227099 | Two overlapping towers | Original terrain/foundation/runtime pass with installed 229310 preserved; recovered Florient Rise originals have one and two unresolved samples |

The initial three coarse-clean identity rows hit an unlabelled assertion. Those
historical results are retained; fresh v2 receipts record `source-identity-fit`
with exact bounded-projection evidence before acquisition. The v3 classifier uses
the existing acceptance policy's exact-ID/unique-match/detailed-projection proof
when that proof actually passes; no identity threshold is changed. Retained native
models passing their full checks are excluded from coarse diagnostic blockers.

Hanford's east-only trial leaves southern source coverage missing. The intervening
northern-sheet trial is preserved and rejected. Actual index polygons and TIN
bounds identify the correct four quadrants: 6-SW-11A/B/C/D. The final v5 source
coverage passes; clearance and neighbours still prevent publication. The new
`terrain_source_preflight.py` uses the indexed polygons and the exact world-z to
HK1980 northing transform, so future acquisition does not rely on guessed sheet
names. It also shows the bus terminus is wholly in 11-NW-24A; the earlier 19C
transfer was unnecessary and grants no extra acceptance evidence.

`indexed-preflight.json` runs the reusable helper on all twelve sources, with pinned
source/index/context/policy hashes: three route directly to identity investigation,
and Hanford is the only bounding box requiring adjoining indexed sheets. Actual
TIN coverage and every downstream gate remain required. Six real-source routing
and identity regressions plus fifteen terrain/sampler checks pass (21 total).
This is source routing, not the removed good-enough/skip-screening pipeline.

Complete current primary and support results are in `result.json`; each links its
individual completed Neon job and evidence. Aggregate fenced Neon job
`52b2b4100f68ba53ab090525f9a14cfd6edeae291329a0d393ad64dfe4679c42`
has exact readback after rechecking all sixteen underlying job results and evidence
hashes. Ownership is released; no active workers or queued follow-ups remain.
Current human status is Held technical/unknown. No AI or human decision requirement
has been established by these failures. Original download/decoded/model caches
remain local-only; committed receipts preserve provenance and diagnostics, not an
R2 backup. Do not rerun completed dated commands or overwrite their checkpoints.

Next work is exact original component/contact investigation grouped by shared
failure, or other independent sources. Preserve the 0.5m embedding allowance;
WEST9ZONE's 0.512283m failure is still a failure. Do not shift sources, crop original
model faces or approve a whole assembly on a single passing interface. No whole
building, territory, architectural quality or phone-FPS completion is claimed.
