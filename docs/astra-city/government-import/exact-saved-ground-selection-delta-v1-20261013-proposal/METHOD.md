# Future saved-ground selection continuation

This isolated helper is prepared for ROOT review, 13 October 2026. No active pinned caller imports it. No production source arrays were loaded, numerical workers rerun, DB accessed or leases claimed. It changes selection computation only; no terrain, actor geometry, scope, kernel, tolerance or acceptance changes. No modelling AI or archival maps are used.

The existing `CompleteGround.select` contract is conservative closed projected AABB selection. It retains projected verticals, lines, points, box-only false positives, and the outward binary64 rounding halo around exact rational queries. Exact triangle clipping would produce a different subset and is therefore excluded from this continuation.

## Algorithm and completeness argument

Copy/freeze both entire ordered ground arrays with the unchanged `CompleteGround`. Match whole ordered binary64 XYZ triplets by bytes, using occurrence queues to handle duplicates. Verify every matched old/new triplet byte-for-byte, an injective matched occurrence map, exact old/new complement partitions, and no identical byte key left in both complements. Signed zeros, vertex order, all Y coordinates and duplicate counts remain significant. The result is a maximal bijection over unchanged occurrences plus complete removed/added inventories. Full ordered arrays, bounds and occurrence mapping are hash-bound and audited again at transaction boundaries.

Authenticate each complete prior selection from its already verified completed receipt and exact chunk bytes. Verify the original world/source-face bytes and complete actor/mode/face scope before invoking this helper. Check the prior selector's whole ground/bounds/query/count/flags/ordered-ID binding and the selected ordered ground tuple hash. Carry every prior selected matched occurrence to its new index; discard unmatched removed occurrences. Test every unmatched added occurrence using the identical rational-query outward float enclosure and closed binary64 AABB inequalities. Sort the combined new IDs and reconstruct the exact original selector schema with current whole-ground and bounds hashes.

For each matched occurrence, its entire byte-equal triplet has identical projected extrema, and the authenticated query has the same exact extent and outward enclosure. Thus its membership is identical. Every unmatched old occurrence is absent in the new complete input. Every unmatched new occurrence is freshly tested. These sets partition both whole inputs, so no new occurrence can be omitted or counted twice. Sorting yields exactly the complete oracle IDs, including closed boundary touches and collapsed projections. The generated binding equals `CompleteGround(new).select(points)` byte-value-for-byte-value in its schema; historical binding/kernel records remain separate and unchanged.

Prior membership already proves whether each removed old tuple was selected, so no old or removed AABB replay is necessary. The full arrays/bijection are checked once; per query the work depends on prior selected count K and changed added count D (subset hashing/mapping, D box tests and sorting K+D IDs), rather than two whole-ground scans. Query extents can overlap unchanged terrain anywhere: there is no changed-region bbox shortcut. No timing or production speedup is claimed. The synthetic 1,200-unchanged/two-added fixture performs two added AABB tests and zero unchanged tests per query.

## Trust boundary and future integration requirements

A self-supplied hash cannot prove an old selection complete. `authenticated_selection_sha` must be derived only after the prior completed receipt/chunk, exact original row, query/source-face bytes, old whole-ground hash and old relevant tuple hash are independently authenticated by the caller. If any authentication or schema/scope binding is missing, use the original complete selector; do not infer or repair a partial selection. This helper checks continuation of a trusted proof, not proof authenticity or finite clearance.

Future callers must iterate the identical complete UID/mode/selected whole face sets, retain all constructor and outside-scope context records, and verify current manifest/input pins before and after. In Upton this means the four complete actor records/all representations, owned13,312 faces, secondary392/native616, whole6,650 input scope, all1,911 BASIC rows/52 affected/2,114 selected faces, every role/root/zero/23-crossing/foreign obligation and original negative record. No favorable-only subset is permitted. No such caller integration is implemented here.

`completeSelectedTripletMultisetExactlyEqual` holds only when no selected old occurrence was removed and no added occurrence is selected. Then `newFaceByOldSelectedFace` is a byte-equal correspondence in the old kernel's exact selected order. Reuse the old kernel record verbatim with its old hashes, findings, negative/context/role records and baseline attribution. New selected ordering/hashes live in the new wrapper. If membership changes, run the unchanged existing finite kernel on the complete new selected array. Neither continuation nor equality grants positive/root/physical/installation credit, or changes retained negative findings.

## Synthetic verification

Sixteen tests compare IDs and the entire generated binding with the immutable complete oracle. They include 420 seeded random queries across12 full delta inventories, repeated identical triangles, duplicate count changes, reordered full arrays, parent splits, changed Y with same XZ, signed zero, vertex rotations, complete replacements, empty selections, closed boundaries, vertical/line/point projections, box-only false positives, rational outward-rounding halos, stale hashes/queries, omissions, incorrect flags, input mutation and maliciously rehashed incorrect occurrence maps. A separate fixture confirms negative kernel/context records are untouched.

Command (from `source-scripts/city/government-import`):

```
/tmp/astra-city-venv/bin/python -m unittest -v test_exact_saved_ground_selection_delta_v1_20261013
```

ROOT owns any future production integration, review, receipts, lease and actual execution. All current pinned callers, geometry and completed evidence remain unchanged.
