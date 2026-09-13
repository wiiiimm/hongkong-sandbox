# HKS-214 — source component support and native terrain review

This pass stages **59 unchanged government model parts** for the root's combined guarded integration. All 59 have exact loader-verified UID/CSUID/model/hash correspondence, every audited native lower-rim vertex has source-supported contact, and **59/59 normal-scene plus 59/59 isolated exported views** have clear, complete framing. The two contact sheets were visually inspected: tower silhouettes, stepped roofs, rooftop components and low podium pieces are retained. Small Manhattan Heights pieces are source components, not claims that those pieces alone represent the tower.

[Decisions](decisions.json) list approved and held UIDs and the exact support dependencies. [Contact sheet 1](contact-1.png) and [contact sheet 2](contact-2.png) show all 59 isolated source components. Full-resolution JPEGs and raw detailed reports are reproducible local evidence; compressed reports are retained alongside this note.

## What changed

The initial 208 ground-gap flags sampled a building's source footprint, not necessarily a physical lower wall. Native government meshes often have **open undersides**: an interior downward ray hits the roof, not a foundation. Treating that height as the bottom would falsely reject otherwise coherent buildings.

The script now loads unchanged compact geometry through the **actual runtime loader**, tests real indexed triangle surfaces and checks every unique vertex within 0.35 m of the native minimum Y against other triangles at a 0.5 m contact tolerance. The terrain band is ±2 m. Actual runtime fallback roof triangles are also included, with holes preserved, only where LandsD source base/top values remain unchanged. Estimated heights, self-UID and same-CSUID contacts cannot qualify.

Across the assigned 242 source parts, the final baseline audit includes 286 native model contexts and 519 surveyed fallback contexts. It finds 70 complete lower-rim triangle contacts, four terrain-contact rims, 33 foundation-context rims, 61 partial contacts and 74 no-contact cases. Bounds only narrow searches; they never count as supporting evidence.

The stable dependency closure yields 59 accepted **component placements**, accounting for the root's 24 grounded parts and seven separately assigned cultural/roof parts. Some supports remain basic government forms. The required `supportDependencies` must be preserved, or the support check repeated when replacing them. Proposed tourist/landmark membership remains separate and is not silently approved.

## Native terrain follow-up

The source TIN audit covers 54 retained source entries and explains 570 lower-rim discrepancy samples. It generated 14 source-only 5 m grids, followed by ten parent-aligned 1 m child proposals. These preserve original HKPD metres, existing water masks and exact outer parent heights.

**Only five patches are eligible for browser validation.** They cover six ground components and additionally support the Sino Plaza tower, giving a separate seven-part terrain-dependent catalogue. The other five patches are held: resampling across sharp retaining edges introduces local burial even when exact source point samples agree. Do not publish them or shift building heights to conceal this.

[Terrain patch evidence](terrain-patches.json) records parent hashes, zero boundary mismatch and zero changed water-mask nodes. `eligibleForBrowserValidation` is mandatory. Coarse-root child patches must be added through the manifest because the app assigns `terrainData.patches` from that manifest. Existing parent children must be appended once, with their `coarseCells` removed from the parent draw.

## Review limits and validation

- Four triangle-contact tests pass, including bbox false positives, vertical seams and open-bottom roof rays; two native-TIN interpolation tests pass.
- Exact source meshes, nodes and elevations remain unchanged. No runtime manifest, terrain, SQLite or source geometry was edited by this agent.
- Every accepted part has a scene and isolated image. Isolated views remove unrelated buildings for diagnosis; normal-scene framing is separately recorded. Additional close foundation views were inspected for Four Seasons and Standard Chartered; the occluded Four Seasons Place view was explicitly replaced by a labelled isolated source/podium view.
- Finite contact checks are not structural engineering, exhaustive disconnected-mesh stability proof, or architectural completion of a named landmark. Root still runs the combined publication, picking, collision, streaming and browser gates.
- Publication is not performed here. The prepared plans are `source-scripts/city/assembly-support-review/plan.json` and `plan-terrain.json`.

## Reproduce

Use Node 24+ and the existing Python environment with NumPy/Shapely. Acquire complete canonical UID reservations before running these scripts; receipts are local `/tmp/astra-support-*-lease.json`, with audited Neon batch names beginning `HKS-214-`. Long runs used `reservations.py run`, which renewed leases and released them on completion.

1. `review.mjs --selection <reserved UID JSON>` regenerates raw `report.json`.
2. `native_terrain.py` reuses verified native TIN caches; `terrain_patches.py` stages parent-aligned variants.
3. `decisions.py` then `prepare.py` stages the dependency-aware base catalogue.
4. `framing.mjs`, `framing-extra.mjs` and `contact.mjs` produce inspectable model evidence.
5. The terrain variant uses `review.mjs --terrain-bundle docs/astra-city/assembly-support-review/terrain-patches.json --output docs/astra-city/assembly-support-review/report-terrain-variant.json`, followed by `decisions.py --report ... --base-approved ... --output ...`, `prepare.py --terrain` and `framing-terrain.mjs`.

Raw large reports can be restored from their adjacent `.json.gz` files with `gzip -dk` before analysis. Model payloads come from the pinned `3887f2f23fbad306` cache and retain their original hashes; no further source download is needed on this device.

## Exact native TIN follow-up

The seven grid-dependent source parts passed replacement-aware browser review in `visual-acceptance-terrain.json`. Creative Media Centre preserves all 19,881 nodes from the installed roof patch; the combined patch must replace that descriptor rather than overlap it.

`exact_tin.py` stages two bounded patches retaining native triangles and retaining faces in their cores. Only the outer 10 m transitions to the parent; transition facets are split against parent triangle boundaries. Existing grid metadata remains for extents and parent-cell omission; `nativeMesh` supplies shared render/collision geometry. Source manifests and buffers are hash checked. Projected coverage and boundary errors are recorded in `exact-tin.json`. `test_exact_tin.py` verifies vertical-wall retention and source-plane-preserving clipping.

`prepare_exact.py`, `exact_surface_review.mjs` and `framing-exact.mjs` check four exact source components with the new shared Float32 sampler and actual browser renderer. Eight normal/isolated exports passed. `visual-acceptance-exact.json` records the exposed facade/roof and retained underground geometry judgement. Highcliff and Summit components have no wholly buried triangles. The 39 Conduit podium has five buried downward faces and two lower retaining/basement wall triangles, but no buried upward roof. These are source-part approvals, not acceptance of the whole named landmark.

`plan-exact.json` stages the unchanged source models for parent publication alongside both exact TIN patches. Parent must recheck combined manifest coverage/seams and source hashes; this review never modifies the runtime manifest. The local payload copies can be reproduced from the pinned preflight cache; they are not duplicated in this evidence commit.

## Further foundation and exact-terrain pass

A second pass reviews the remaining foundation flags against actual native facade and roof triangles rather than requiring every lowest vertex to touch terrain. `foundation-surface-review.json` and 40 exported normal/isolated views cover 20 parts. Seventeen are accepted on unchanged rendered terrain in `visual-acceptance-foundation.json`; HKDI and Belcher's Tower 2 retain explicit lower upward-surface terrain holds.

The Peak Tower source component is separately accepted with its exact native TIN patch: previously buried upward-face area falls from approximately 86 m² to zero. `visual-acceptance-peak.json` preserves the distinction between this source UID and complete named-landmark architecture.

`visual-acceptance-exact-next.json` accepts Queensway Government Offices, Centrium and two Branksome Crest components with three source-preserving TIN patches. No whole native triangles remain buried in these four. Branksome263590 has an explicit native dependency on232907; integrate and stream both together.

Publication plans: `plan-foundation.json` (17), `plan-exact-next.json` (4), `plan-peak.json` (1). The scripts stage only exact existing source models. Parent must validate the combined patch arrangement and refresh deployment/manifest checks. `followup-ledger-sync.json` records22 approvals-for-integration and2 continued holds; none of these artefacts independently publishes runtime content.

Reproduction uses tracked files: `prepare_followup.py --name foundation --uids source-scripts/city/assembly-support-review/selection-foundation.json`; analogous named passes accept `--terrain docs/astra-city/assembly-support-review/exact-tin-next.json` or `exact-tin-peak.json`. `accept_followup.py` can read the tracked `visual-acceptance-<name>.json` as its `--notes` input. Restore source assets through the existing immutable cache workflow before running on another device.

## Border-sheet and below-grade completion

HKDI (22089) and Belcher's Tower 2 (255427) were previously held. Their native terrain was partially present but omitted from the whole-bounds coverage index. The acquisition helper reused both original terrain pairs from verified caches with zero network bytes; HKDI's three neighbouring sheets required 7,055,543 bytes, without photographs/textures.

An exact HKDI TIN rectangle retained a 3 cm quantised source-sheet seam. The approved `grid-hkdi.json` proposal therefore uses a 1 m source-sampled grid: all 59,291 nodes are covered by native triangles, with zero parent-boundary error. This is interpolation between surveyed-source samples, not an exact TIN or 1 m accuracy claim. It removes all buried upward native faces; normal/isolated exports were inspected. `plan-hkdi.json` references only this approved grid. The experimental `exact-tin-extra` and `exact-tin-hkdi` outputs are not approved for publication.

Belcher's below-grade review verifies every fully buried face is below the same-CSUID LandsD surveyed base of 69.9 m; the highest is 58.483 m. The visible native tower/facade/roof remains clear. `plan-belowgrade.json` accepts this source component with unchanged terrain and preserved basement geometry. No inferred building shift or podium was added.

The new cache payloads under `native-terrain-extra/sources` and `staged/*/TERRAIN*` are deliberately ignored; manifests, source hashes, transfer ledgers and scripts are tracked for R2 checkpoint/resume. `two-context-ledger-sync.json` records both approvals in the instructed combined Neon snapshot.
