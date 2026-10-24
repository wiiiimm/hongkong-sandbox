"""Paired v3: same exact clearance constraints, reviewed exact coverage pruning.

The ordinary prism stage uses coverage-v2 instead of the unpruned coverage-v1
subtraction. Only strictly rational-bound-disjoint pieces skip clipping; no
threshold/face/height/root changes. Old v1/v2 outputs stay immutable. This is
new diagnostic provenance, not a claim that old v1 was executed successfully.
"""
import hashlib
from fractions import Fraction as F
import numpy as np
from exact_original_projection_coverage_v2_20261010 import exact_coverage, point, signed_area
from exact_original_closed_projection_intersection_20261010 import intersection

def rational(p):
    return tuple(F.from_float(float(x)) for x in p)

def clip_source(poly, a, b):
    def side(p):
        return (b[0]-a[0])*(p[2]-a[1])-(b[1]-a[1])*(p[0]-a[0])
    out=[]
    for p,q in zip(poly,poly[1:]+poly[:1]):
        sp,sq=side(p),side(q)
        if sp>=0: out.append(p)
        if (sp<0 and sq>0) or (sp>0 and sq<0):
            t=sp/(sp-sq)
            out.append(tuple(p[k]+t*(q[k]-p[k]) for k in range(3)))
    return list(dict.fromkeys(out))

def optimized_ordinary_prism(face, ground):
    source=np.asarray(face,float); terrain=np.asarray(ground,float)
    assert source.shape==(3,3) and terrain.ndim==3 and terrain.shape[1:]==(3,3) and len(terrain)
    assert np.isfinite(source).all() and np.isfinite(terrain).all()
    lo=source[:,[0,2]].min(axis=0); hi=source[:,[0,2]].max(axis=0); xz=terrain[:,:,[0,2]]
    ids=np.flatnonzero(np.all(xz.max(axis=1)>=lo,axis=1)&np.all(xz.min(axis=1)<=hi,axis=1))
    assert len(ids)
    coverage=exact_coverage(source,terrain[ids]); original=[rational(p) for p in source]
    low=min(p[1] for p in original); gaps=[]; pieces=[]
    for j in ids:
        raw=terrain[j]; projected=[point(p) for p in raw[:,[0,2]]]; area=signed_area(projected)
        if area==0:
            touching=intersection(source[:,[0,2]],raw[:,[0,2]])
            if not touching:
                pieces.append(dict(originalGroundFace=int(j),closedProjectionDisjoint=True,groundHeightOrCoverageCredit=False)); continue
            gap=low-max(p[1] for p in map(rational,raw)); gaps.append(gap)
            pieces.append(dict(originalGroundFace=int(j),collapsedProjectionConservative=True,exactMinimumGapM=str(gap),groundPlaneCredit=False)); continue
        if area<0: projected.reverse()
        poly=original
        for a,b in zip(projected,projected[1:]+projected[:1]):
            if not poly: break
            poly=clip_source(poly,a,b)
        if not poly: continue
        a,b,c=map(rational,raw); u=tuple(b[k]-a[k] for k in range(3)); v=tuple(c[k]-a[k] for k in range(3))
        n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]); assert n[1]!=0
        paired=[]
        for x,y,z in poly:
            gy=a[1]-(n[0]*(x-a[0])+n[2]*(z-a[2]))/n[1]
            paired.append(dict(exactOriginalSourcePoint=[str(x),str(y),str(z)],exactFiniteGroundHeightM=str(gy),exactGapM=str(y-gy)))
            gaps.append(y-gy)
        pieces.append(dict(originalGroundFace=int(j),allExactSourcePrismIntersectionVertices=paired,exactMinimumGapM=str(min(F(p['exactGapM']) for p in paired))))
    assert gaps
    bound=min(gaps)
    return dict(contract='exact-original-source-prism-paired-finite-clearance-coverage-pruned-v3',completeOriginalProjectionCoverage=coverage,groundProjectionCovered=coverage['exactProjectionCovered'],allProjectedBoundingCandidateOriginalGroundFacets=list(map(int,ids)),allExactFiniteSourceGroundPieces=pieces,exactCertifiedLowerClearanceM=str(bound),existingOrdinaryClearanceBoundProved=coverage['exactProjectionCovered'] and bound>=F(-1,2),sourceFaceSHA256=hashlib.sha256(source.tobytes()).hexdigest(),completeCurrentGroundSHA256=hashlib.sha256(terrain.tobytes()).hexdigest(),sourcePlaneInversionUsed=False,rawPriorDiagnosticChanged=False,sourceGeometryChanges=0,rootOrContactCredit=False,fullAcceptance=False,installationApproved=False)


def verify(face, ground):
    from exact_original_paired_finite_clearance_v2_20261010 import refine
    initial=optimized_ordinary_prism(face, ground)
    result=refine(face, ground, initial)
    assert result['rawPriorPairedProofVerbatim']==initial
    result['sameConstraintOptimizedOrdinaryPrismProof']=result.pop('rawPriorPairedProofVerbatim')
    result['contract']='exact-original-source-prism-complete-finite-column-clearance-pruned-v3'
    result['initialCoverageUsesExactReviewedStrictDisjointPruning']=True
    result['oldPairedV1OrV2NotRewritten']=True
    return result
