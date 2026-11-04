# Block 37: complete original wall/ground context

This is a new source-local diagnosis for `landsd/228547:0`, model
`B340653488502062G0`, source gzip SHA256
`aacc1b1911b1f282646fd49e1b8551a7b5ed6b481855feff5f03169579681e0f`.
It preserves the original mesh, one metre per Hong Kong Principal Datum metre,
root pose and strict failed placement/foundation results. Nothing is installed.

Every one of the 13,914 original faces was intersected with the byte-pinned
historical drawn terrain. All upward faces clear the terrain; their continuous
minimum is **+0.4489955902 m**. Outside the 25 closed buried components,
**857 faces** extend more than 0.5 m below ground. **829 are exactly vertical**;
the other 28 have normal-Y ratios between approximately −0.02982 and +0.01785.
Every affected face has an exposed upper witness. Its maximum is not certified
continuously. The continuous wall minimum is **−2.6820039749 m**, worse than the
previous vertex/centroid sample minimum of −1.0258539455 m. These intersections
must not be described as a false positive in the old placement test.

The affected exterior faces belong to one 4,049-face component. It is open and
nonmanifold: 622 boundary edges, 55 three-face edges, two four-face edges and two
orientation conflicts. Of the 622 boundary edges, 474 have both vertices at or
below the diagnostic 9.01 HKPD low-plane cut; 146 lie above it and two cross it.
This cut is a description of authored topology, not an acceptance threshold.
Casting world coordinates to Float32 reproduces the same incidence counts, so
rounding is not a topology repair. The 25 buried crossing components each contain
92 faces; the exact rational self-intersection check examines all face pairs in
each component separately. It does not certify interactions with other shells.

`buried-face-separation.json` additionally checks all 224 original faces previously
classified as wholly buried by vertex/centroid sampling against every other
original connected component. None of their exact-coordinate AABBs overlap another
component's face, which excludes such intersections for those explicit face indices.
It does not certify continuous burial membership, above-ground component interactions,
or foreign scene geometry that is absent from this original source.

`diagnostic.json.gz` retains the first coverage method, which unions separately
clipped intersection fragments. That method reports 3,980 uncovered faces,
including 333 affected walls, because clipping introduces floating seam slivers.
`coverage-v2.json.gz` instead unions full original intersecting terrain facets.
It covers **all 13,914 faces**, including all 857 affected walls, with no buffers,
snapping or tolerance credits. `coverage-fixture.json` is one original offending
face and its intersecting terrain triangles; the v2 test also retains a genuinely
missing-terrain fixture that remains uncovered. The minimum algorithm is unchanged.

The original model was rendered in its native pose, and the exported PNG was
inspected. It shows a broad roof/podium surface with authored perimeter walls and
equipment. The footprint overlay is the explicitly pinned historical source
selection, not a fresh current identity approval. The exact provider OP relationship
identifies a single one-storey Podium, structure 942359, OP `NT34/96`, for CSUID
`3406534885P20050804`. Basement/storey remarks and building type are null. Provider
Podium classification does **not** itself identify open-bottom walls or authorise
the buried components. No historical map imagery was used.

## Conservative conditions for a future source-specific route

These conditions are a proposal. No condition below substitutes for the existing
strict path, and this checkpoint grants no skip, install or placement credit.

1. Bind the exact original source bytes, complete face membership, units, root pose,
   actual drawn-ground bytes and current identity/footprint. Inspect source authorship
   and provider context sufficiently to classify the open-bottom exterior role
   positively. A generic Podium label or a plausible capture alone is insufficient.
2. Account for every original component and every below-ground face. The 25 closed
   shells need exact outward topology, self-intersection checks, exposed upper
   surfaces and independent positive below-grade component classification. Whole
   original source interactions and foreign/unrelated actor protections remain
   mandatory; individual shell checks do not prove them.
3. Restrict a wall-contact interpretation to positively identified authored exterior
   walls that continuously cross the actual ground and retain exposed upper exterior.
   Establish the role and intended open bottom from the original source, including
   the upper boundary defects. Do not extend a wall interpretation to roofs, floors,
   buried upward faces, arbitrary inverted faces, detached decorations or omitted
   components. Exact/robust continuous checks are needed before acceptance; the
   present floating intersection diagnostic is evidence, not that contract.
4. Keep the existing clearance limits for every roof, upward face, floor and all
   other nonclassified faces. Preserve the raw −2.682 m wall minimum and the original
   strict failures in any typed result; do not overwrite them as passes.
5. Run fresh complete acceptance against the current surface, including reliable
   ground-contact/support coverage, identity, neighbours, raw source preservation,
   actual browser/runtime rendering and desktop/mobile checks. Open-bottom visual
   contact cannot grant support to unrelated floating towers or waive neighbour gaps.

The next concrete steps are positive source-role evidence for the open component
and the 25 column-like components, followed by a reviewed typed contract if that
evidence is sufficient. Otherwise retain the current model and this complete held
reason in Neon for a later source/context investigation. No AI geometry modelling
was performed; AI was used to write code and interpret evidence.

## Reproduction

Run from the worktree with a current fenced reservation for the source:

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/government-import/xl-terrain-recovery-20261009-block37-wall-context.py
/tmp/astra-city-venv/bin/python source-scripts/city/government-import/xl-terrain-recovery-20261009-block37-coverage-v2.py
/tmp/astra-city-venv/bin/python source-scripts/city/government-import/xl-terrain-recovery-20261009-block37-shell-context.py
/tmp/astra-city-venv/bin/python source-scripts/city/government-import/xl-terrain-recovery-20261009-block37-buried-separation.py
node source-scripts/city/government-import/render-source-footprint-evidence.mjs --inputs docs/astra-city/government-import/xl-terrain-recovery-20261009-block37-wall-context/render-inputs.json --out docs/astra-city/government-import/xl-terrain-recovery-20261009-block37-wall-context/captures
```

First generation requires fresh output paths. Already bound diagnostic outputs are
immutable; follow-up methods require new versioned paths. Tests require no source
lease or network:

```sh
cd source-scripts/city/government-import
/tmp/astra-city-venv/bin/python -m unittest test_original_face_ground_crossing_20261009.py test_original_face_ground_crossing_v2_20261009.py
```

That command executes nine distinct wall/ground tests, including the real
clipped-intersection seam and a missing-ground counterexample.
