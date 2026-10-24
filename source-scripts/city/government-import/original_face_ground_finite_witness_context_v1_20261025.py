"""Replace impossible floating witnesses with exact finite source/ground proofs.

No clearance tolerance, geometry, or acceptance rule changes. The previous
diagnostic remains verbatim whenever a witness is outside source bounds.
"""
from fractions import Fraction as F
import numpy as np
from original_face_ground_rank_context_v1_20261024 import face_ground_context as previous
from exact_original_paired_finite_clearance_v2_20261010 import verify


def finite_source_bounds_contain(face, point):
    tri = np.asarray(face, dtype=float)
    p = np.asarray(point, dtype=float)
    return bool(np.all(np.isfinite(p)) and np.all(p >= tri.min(0)) and np.all(p <= tri.max(0)))


def face_ground_context(face, ground, polygons=None, tree=None):
    prior = previous(face, ground, polygons, tree)
    minimum = prior.get('minimum')
    if not minimum or finite_source_bounds_contain(face, minimum['position']):
        return prior
    exact = verify(face, ground)
    witnesses = []
    for piece in exact['allExactFiniteSourceGroundPieces']:
        ordinary = piece.get('priorOrdinaryPrismProofVerbatim')
        if ordinary:
            for p in ordinary.get('allExactSourcePrismIntersectionVertices', []):
                witnesses.append((F(p['exactGapM']), piece['originalGroundFace'],
                                  p['exactOriginalSourcePoint'], F(p['exactFiniteGroundHeightM'])))
        collapsed = piece.get('exactCompleteFiniteColumnProof')
        if collapsed:
            for p in collapsed['allExactBasicFeasibleColumnVertices']:
                witnesses.append((F(p['exactGapM']), piece['originalGroundFace'],
                                  p['exactSourcePoint'], F(p['exactGroundPoint'][1])))
    assert witnesses, 'Exact proof must provide a finite witness'
    gap, ground_id, coordinates, height = min(witnesses, key=lambda row: row[0])
    assert gap == F(exact['exactCertifiedLowerClearanceM'])
    point = [float(F(v)) for v in coordinates]
    assert finite_source_bounds_contain(face, point)
    return dict(groundProjectionCovered=exact['groundProjectionCovered'],
                minimum=dict(minimumGapM=float(gap), position=point,
                             terrainHeight=float(height), terrainFace=ground_id),
                maximumObservedGapM=None, continuousMaximumCertified=False,
                floatingIntersectionArithmetic=False, exactFiniteWitnessProof=exact,
                rawPriorImpossibleWitnessVerbatim=prior,
                rawPriorFailure='Floating minimum lies outside complete source face bounds',
                diagnosticOnly=True, geometryChanges=0, installationApproved=False)
