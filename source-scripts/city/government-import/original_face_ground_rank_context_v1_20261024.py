"""Exact finite diagnostic for rank cancellation; source coordinates stay unchanged."""
from fractions import Fraction as F
import numpy as np
import shapely
from original_face_ground_crossing_v2_20261009 import face_ground_context as previous
from exact_original_paired_finite_clearance_v2_20261010 import verify


def face_ground_context(face, ground, polygons=None, tree=None):
    try:
        return previous(face, ground, polygons, tree)
    except AssertionError as error:
        if str(error) != 'Projection rank mismatch':
            raise
    source = np.asarray(face, float)
    normal = np.cross(source[1]-source[0], source[2]-source[0])
    projection = shapely.MultiPoint(source[:, [0, 2]]).convex_hull
    assert normal[1] == 0 and projection.geom_type == 'Polygon'
    exact = verify(source, ground)
    witnesses = []
    for piece in exact['allExactFiniteSourceGroundPieces']:
        ordinary = piece.get('priorOrdinaryPrismProofVerbatim')
        assert 'exactCompleteFiniteColumnProof' not in piece, 'Collapsed ground needs separate witness adapter'
        if ordinary:
            for point in ordinary.get('allExactSourcePrismIntersectionVertices', []):
                witnesses.append((F(point['exactGapM']), piece['originalGroundFace'], point))
    assert witnesses
    gap, ground_id, point = min(witnesses, key=lambda row: row[0])
    assert gap == F(exact['exactCertifiedLowerClearanceM'])
    position = [float(F(value)) for value in point['exactOriginalSourcePoint']]
    return dict(verticalFace=False, groundProjectionCovered=exact['groundProjectionCovered'],
                minimum=dict(minimumGapM=float(gap), position=position,
                             terrainHeight=float(F(point['exactFiniteGroundHeightM'])), terrainFace=ground_id),
                maximumObservedGapM=None, groundFacetPairs=len(exact['allExactFiniteSourceGroundPieces']),
                continuousMaximumCertified=False, floatingIntersectionArithmetic=False,
                exactRankCancellationProof=exact, rawPriorFailure='Projection rank mismatch',
                diagnosticOnly=True, geometryChanges=0, installationApproved=False)
