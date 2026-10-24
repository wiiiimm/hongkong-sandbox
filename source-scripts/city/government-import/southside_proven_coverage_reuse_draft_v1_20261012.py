"""UNEXECUTED draft: reuse only freshly proven exact projection coverage.

No external saved proof is accepted. The public call computes the unchanged
coarse v5 proof itself. A coverage negative takes the untouched paired v1 path.
The active Southside worker does not import this file.
"""
import hashlib
from fractions import Fraction as F
import numpy as np
import exact_original_face_conservative_clearance_v5_20261010 as coarse
import exact_original_paired_finite_clearance_20261010 as legacy


def _paired_after_fresh_positive_coverage(face, ground, coverage):
    source=np.asarray(face,float); terrain=np.asarray(ground,float)
    assert source.shape==(3,3) and terrain.ndim==3 and terrain.shape[1:]==(3,3) and len(terrain)
    assert np.isfinite(source).all() and np.isfinite(terrain).all()
    lo=source[:,[0,2]].min(axis=0); hi=source[:,[0,2]].max(axis=0); xz=terrain[:,:,[0,2]]
    ids=np.flatnonzero(np.all(xz.max(axis=1)>=lo,axis=1)&np.all(xz.min(axis=1)<=hi,axis=1))
    assert len(ids)
    assert coverage['exactProjectionCovered'] is True and coverage['noToleranceOrBufferCredit'] is True
    assert coverage['sourceFaceSHA256']==hashlib.sha256(source.tobytes()).hexdigest()
    assert coverage['completeGroundSHA256']==hashlib.sha256(terrain[ids].tobytes()).hexdigest()
    assert coverage['completeOriginalGroundTrianglesAccounted']==len(ids)
    original=[legacy.rational(p) for p in source]
    low=min(p[1] for p in original); gaps=[]; pieces=[]
    # These finite prism / collapsed-ground operations are copied unchanged
    # from the pinned legacy verify implementation; only coverage is reused.
    for j in ids:
        raw=terrain[j]; projected=[legacy.point(p) for p in raw[:,[0,2]]]; area=legacy.signed_area(projected)
        if area==0:
            touching=legacy.intersection(source[:,[0,2]],raw[:,[0,2]])
            if not touching:
                pieces.append(dict(originalGroundFace=int(j),closedProjectionDisjoint=True,groundHeightOrCoverageCredit=False)); continue
            gap=low-max(p[1] for p in map(legacy.rational,raw)); gaps.append(gap)
            pieces.append(dict(originalGroundFace=int(j),collapsedProjectionConservative=True,exactMinimumGapM=str(gap),groundPlaneCredit=False)); continue
        if area<0: projected.reverse()
        poly=original
        for a,b in zip(projected,projected[1:]+projected[:1]):
            if not poly: break
            poly=legacy.clip_source(poly,a,b)
        if not poly: continue
        a,b,c=map(legacy.rational,raw); u=tuple(b[k]-a[k] for k in range(3)); v=tuple(c[k]-a[k] for k in range(3))
        n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]); assert n[1]!=0
        paired=[]
        for x,y,z in poly:
            gy=a[1]-(n[0]*(x-a[0])+n[2]*(z-a[2]))/n[1]
            paired.append(dict(exactOriginalSourcePoint=[str(x),str(y),str(z)],exactFiniteGroundHeightM=str(gy),exactGapM=str(y-gy)))
            gaps.append(y-gy)
        pieces.append(dict(originalGroundFace=int(j),allExactSourcePrismIntersectionVertices=paired,exactMinimumGapM=str(min(F(p['exactGapM']) for p in paired))))
    assert gaps
    bound=min(gaps)
    return dict(contract='exact-original-source-prism-paired-finite-clearance-v1',completeOriginalProjectionCoverage=coverage,groundProjectionCovered=coverage['exactProjectionCovered'],allProjectedBoundingCandidateOriginalGroundFacets=list(map(int,ids)),allExactFiniteSourceGroundPieces=pieces,exactCertifiedLowerClearanceM=str(bound),existingOrdinaryClearanceBoundProved=coverage['exactProjectionCovered'] and bound>=F(-1,2),sourceFaceSHA256=hashlib.sha256(source.tobytes()).hexdigest(),completeCurrentGroundSHA256=hashlib.sha256(terrain.tobytes()).hexdigest(),sourcePlaneInversionUsed=False,rawPriorDiagnosticChanged=False,sourceGeometryChanges=0,rootOrContactCredit=False,fullAcceptance=False,installationApproved=False)


def verify(face, ground):
    """Return the legacy caller record; proof creation is internal and fresh."""
    a=coarse.verify(face,ground)
    if a['existingOrdinaryClearanceBoundProved']:
        b=None
    elif a['groundProjectionCovered']:
        b=_paired_after_fresh_positive_coverage(face,ground,a['completeOriginalProjectionCoverage'])
    else:
        # Preserve the original coverage-negative representation and complete
        # paired clearance context rather than introducing a new short circuit.
        b=legacy.verify(face,ground)
    return dict(coarse=a,paired=b,completeFiniteOrdinaryBoundProved=bool(a['existingOrdinaryClearanceBoundProved']or(b and b['existingOrdinaryClearanceBoundProved'])))
