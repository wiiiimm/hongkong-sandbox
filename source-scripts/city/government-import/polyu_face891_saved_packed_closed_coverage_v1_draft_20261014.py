"""UNEXECUTED exact XZ coverage of saved face891 pieces; no repartition.

Projection coverage is not 3D/source-plane equality, height/MAX, physical or
installation approval. Inside source shadows are not restored-parent facets.
"""
from fractions import Fraction as F
import hashlib
import numpy as np
import exact_original_projection_coverage_v2_20261010 as coverage


def rational_points(values):
    return [tuple(F(v) for v in p) for p in values]


def projected(values):
    return [(p[0], p[2]) for p in values]


def bounds(poly):
    return (min(p[0] for p in poly), min(p[1] for p in poly),
            max(p[0] for p in poly), max(p[1] for p in poly))


def separated(a, b):
    return a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1]


def exact_zero_3d(triangle):
    a, b, c = triangle
    u = tuple(b[k]-a[k] for k in range(3)); v = tuple(c[k]-a[k] for k in range(3))
    return all(u[i]*v[j]-u[j]*v[i] == 0 for i, j in [(0,1),(0,2),(1,2)])


def production_determinant(t):
    # Same binary64 association as native-terrain.js, on captured Float32 values.
    (ax, _, az), (bx, _, bz), (cx, _, cz) = t
    return (bz-cz)*(ax-cx)+(cx-bx)*(az-cz)


def map_saved_packet(packet):
    assert packet['complete'] and packet['face'] == 891
    partition = packet['exactIdealPartition']; pieces = packet['exactOwnPlanePackedPieces']
    regions = []; rows = []; cursor = 0; digest = hashlib.sha256()
    groups = [('outside-retained-source', dict(polygon=p)) for p in partition['outside']]
    groups += [('inside-source-shadow-not-restored-parent', r) for r in partition['inside']]
    for ordinal, (role, region) in enumerate(groups):
        poly = rational_points(region['polygon']); ids = []
        assert len(poly) >= 3 and coverage.signed_area(projected(poly)) != 0
        for i in range(1, len(poly)-1):
            piece = pieces[cursor]; expected = [poly[0], poly[i], poly[i+1]]
            assert rational_points(piece['exactOwnPlanePoints']) == expected
            array = np.asarray(piece['packedPieceTriplet'], dtype='<f8')
            assert array.shape == (3,3) and np.isfinite(array).all()
            assert array.astype('<f4').astype('<f8').tobytes() == array.tobytes()
            digest.update(array.tobytes()); exact = rational_points(array.tolist())
            xz = projected(exact); area = coverage.signed_area(xz)
            determinant = production_determinant(array.tolist())
            collapsed = exact_zero_3d(exact)
            rows.append(dict(id=cursor, region=ordinal, role=role, points=xz,
                bound=bounds(xz), collapsed=collapsed, projectedArea=abs(area),
                productionDeterminant=determinant,
                heightAdmitted=abs(determinant) >= 1e-10,
                projectedPositive=bool(area), ownerMask=region.get('mask')))
            ids.append(cursor); cursor += 1
        regions.append(dict(id=ordinal, role=role, ownerMask=region.get('mask'),
                            points=projected(poly), packedPieceIDs=ids))
    assert cursor == len(pieces) == packet['packedFacetCount']
    assert digest.hexdigest() == packet['orderedOneFacePackedSHA256']
    assert sum(r['collapsed'] for r in rows) == packet['exact3DAreaZeroPackedFacets']
    assert sum(not r['heightAdmitted'] for r in rows) == packet['rendererExcludedProjectedFacetsAtExistingAbsDetLessThan1eMinus10']
    return regions, rows


def edge_coverage(a, b, triangles):
    """Complete closed intervals from positive projected finite triangles only.

    Degenerate projections stay inventoried but receive no surface/edge credit.
    """
    intervals = []
    for original in triangles:
        t = original if coverage.signed_area(original) > 0 else list(reversed(original))
        lo, hi = F(0), F(1)
        for p, q in zip(t, t[1:]+t[:1]):
            start, end = coverage.cross(p,q,a), coverage.cross(p,q,b); delta = end-start
            if delta == 0:
                if start < 0: lo, hi = F(1), F(0); break
            elif delta > 0: lo = max(lo, -start/delta)
            else: hi = min(hi, -start/delta)
        if lo <= hi: intervals.append((lo,hi))
    reach = F(0); gaps = []
    for lo, hi in sorted(intervals):
        if lo > reach: gaps.append((reach,lo))
        reach = max(reach,hi)
    if reach < 1: gaps.append((reach,F(1)))
    return dict(covered=not gaps and bool(intervals), exactParameterGaps=gaps,
                contributingClosedIntervals=len(intervals))


def closed_coverage(poly, rows, own_ids=()):
    """Exact rational target stays rational; do not round it through float API."""
    target = bounds(poly)
    selected = [r for r in rows if not r['collapsed'] and r['projectedPositive']
                and not separated(target,r['bound'])]
    own = set(own_ids); selected.sort(key=lambda r:(r['id'] not in own,r['id']))
    triangles = [r['points'] for r in selected]; remaining = [poly]
    for t in triangles:
        remaining = [p for part in remaining for p in coverage.subtract(part,t)]
        if not remaining: break
    area = sum((abs(coverage.signed_area(p)) for p in remaining), F(0))
    edges = [edge_coverage(a,b,triangles) for a,b in zip(poly,poly[1:]+poly[:1])]
    return dict(completeClosedXZCovered=area == 0 and all(e['covered'] for e in edges),
        exactUncoveredAreaM2=area, positiveAreaGapPolygons=remaining,
        completeBoundaryEdges=edges, conservativeClosedCandidates=[r['id'] for r in selected],
        degeneratePackedFacetsReceiveNoCoverageCredit=True,
        noToleranceOrBuffer=True, noHeightOr3DCoverageClaim=True)


def inspect(packet, progress):
    regions, rows = map_saved_packet(packet)
    # Complete source partition checks against whole emitted shadow and against
    # its role-specific surface. This permits genuine adjacent-role coverage in
    # the whole-shadow result without silently crediting it as retained outside.
    findings = []
    for region in regions:
        variants = {}
        for name, same_role, admitted in [('all-drawn-source-shadow',False,False),
             ('all-height-admitted-source-shadow',False,True),
             ('same-role-drawn-source-shadow',True,False),
             ('same-role-height-admitted-source-shadow',True,True)]:
            eligible = [r for r in rows if (not same_role or r['role']==region['role'])
                        and (not admitted or r['heightAdmitted'])]
            variants[name] = closed_coverage(region['points'],eligible,region['packedPieceIDs'])
        findings.append(dict(**region,coverage=variants))
        progress(dict(regionsCompleted=len(findings),totalRegions=len(regions),
                      role=region['role'],ownerMask=region['ownerMask']),findings[-1])
    return dict(complete=True, scope='ONE saved source-plane shadow, exact closed XZ only',
        rows=findings, completePackedFacetAccounting=rows,
        exact3DCollapsesUncredited=sum(r['collapsed'] for r in rows),
        exactZeroProjectedFacetsUncredited=sum(not r['projectedPositive'] for r in rows),
        rendererHeightIndexExcluded=sum(not r['heightAdmitted'] for r in rows),
        originalMaskOccurrenceAliases=packet['exactIdealPartition']['allOriginalMaskOccurrenceAliases'],
        regionUnionIsTheSavedIdealSourceFacePartition=True,
        restoredCurrentParentCoveragePending=True, sourcePlaneVerticalPackingResidual=packet['maxExactOwnPlaneVerticalPackingResidualM'],
        actualHeightMAXOrdinaryRuntimeWholeCandidateCoveragePending=True,
        physicalAccepted=False, installationApproved=False, sourceGeometryPoseEdited=False)
