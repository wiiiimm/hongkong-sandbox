"""Whole rational residual polygon/boundary coverage by authentic current faces.

Composes unchanged exact clip/subtract/segment-parameter kernels. Saved rational
gap coordinates never pass through float conversion. No geometry repair.
"""
from fractions import Fraction as F
from exact_original_projection_coverage_v2_20261010 import clip,subtract,signed_area
from upton_saved_uncovered_packed_ancestor_boundary_attribution_draft_v1_20261013 import segment_parameter


def polygon(values):return [tuple(F(v)for v in p)for p in values]


def closed_boundary_cover(a,b,triangles):
    assert a!=b;intervals=[]
    for face,t in triangles:
        part=[a,b]
        for u,v in zip(t,t[1:]+t[:1]):
            part=clip(part,u,v,True)
            if not part:break
        if not part:continue
        ts=[segment_parameter(p,a,b)for p in part];assert all(t is not None for t in ts)
        intervals.append(dict(originalCurrentFace=face,exactClosedParameterInterval=[min(ts),max(ts)]))
    merged=[]
    for q in sorted(intervals,key=lambda q:q['exactClosedParameterInterval']):
        lo,hi=q['exactClosedParameterInterval']
        if merged and lo<=merged[-1][1]:merged[-1][1]=max(merged[-1][1],hi)
        else:merged.append([lo,hi])
    return dict(exactOriginalGapEdgeXZ=[a,b],allCurrentPlaneClosedIntervals=intervals,
                completeClosedParameterUnion=merged,wholeClosedGapEdgeCovered=merged==[[F(0),F(1)]],
                endpointOnlyIncidenceNeverWholeEdgeCredit=True,noToleranceOrSnap=True)


def cover_whole_polygon(values,triangles):
    poly=polygon(values);area=abs(signed_area(poly));assert area>0
    if signed_area(poly)<0:poly.reverse()
    original=list(poly);remaining=[poly];positive=[];boundary=[]
    for face,t in triangles:
        assert signed_area(t)>0
        part=poly
        for a,b in zip(t,t[1:]+t[:1]):
            part=clip(part,a,b,True)
            if not part:break
        if abs(signed_area(part))>0:positive.append(dict(originalCurrentFace=face,exactWholeMaskIntersectionPolygonXZ=part,exactPositiveIntersectionAreaM2=abs(signed_area(part))))
        remaining=[part for piece in remaining for part in subtract(piece,t)]
    for i,(a,b)in enumerate(zip(original,original[1:]+original[:1])):
        boundary.append(dict(edge=i,**closed_boundary_cover(a,b,triangles)))
    uncovered=sum((abs(signed_area(p))for p in remaining),F(0))
    return dict(exactWholeSavedResidualPolygonXZ=original,exactWholeResidualAreaM2=area,
                exactUncoveredByOriginalCurrentAreaM2=uncovered,remainingUncoveredPolygonsXZ=remaining,
                allPositiveAreaCurrentCounterpartIntersections=positive,completeWholeGapBoundaryProofs=boundary,
                wholeClosedResidualCovered=uncovered==0 and all(q['wholeClosedGapEdgeCovered']for q in boundary),
                allSavedRationalCoordinatesPreserved=True,noNominalAreaOrNearbyAliasCredit=True,
                noCoveragePhysicalOrInstallationAcceptance=True)
