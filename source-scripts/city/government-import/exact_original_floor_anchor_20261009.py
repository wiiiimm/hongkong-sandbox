"""Conservative exact contact band over complete horizontal floor facet.

Every intersecting original ground plane is bounded, including overlaps. This
does not mistake a sampled maximum for a certified continuous upper bound.
"""
import numpy as np
from fractions import Fraction
from exact_original_projection_coverage_20261009 import point,signed_area,clip,exact_coverage
def verify_contact(face,ground,band=.1):
    source=np.asarray(face,float);terrain=np.asarray(ground,float)
    assert source.shape==(3,3) and terrain.ndim==3 and terrain.shape[1:]==(3,3)
    assert np.isfinite(source).all() and np.isfinite(terrain).all() and np.isfinite(band) and band>=0
    assert np.all(source[:,1]==source[0,1]) and signed_area([point(p) for p in source[:,[0,2]]])!=0
    coverage=exact_coverage(source,terrain);poly=[point(p) for p in source[:,[0,2]]]
    source_y=Fraction.from_float(float(source[0,1]));gaps=[];pieces=[]
    lo=source[:,[0,2]].min(axis=0);hi=source[:,[0,2]].max(axis=0);xz=terrain[:,:,[0,2]]
    candidates=np.flatnonzero(np.all(xz.max(axis=1)>=lo,axis=1)&np.all(xz.min(axis=1)<=hi,axis=1))
    for j in candidates:
        original=terrain[j];p=[point(v) for v in original[:,[0,2]]]
        if signed_area(p)==0:continue
        if signed_area(p)<0:p.reverse()
        clipped=poly
        for a,b in zip(p,p[1:]+p[:1]):clipped=clip(clipped,a,b,True)
        if not clipped:continue
        a,b,c=[tuple(Fraction.from_float(float(v)) for v in xyz) for xyz in original]
        u=tuple(b[k]-a[k] for k in range(3));v=tuple(c[k]-a[k] for k in range(3))
        n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);assert n[1]!=0
        values=[]
        for x,z in clipped:
            y=a[1]-(n[0]*(x-a[0])+n[2]*(z-a[2]))/n[1];values.append(source_y-y)
        gaps.extend(values);pieces.append({'originalGroundFace':int(j),'exactMinimumGapM':str(min(values)),'exactMaximumGapM':str(max(values))})
    limit=Fraction.from_float(float(band))
    verified=bool(coverage['exactProjectionCovered'] and gaps and min(gaps)>=-limit and max(gaps)<=limit)
    return {'verifiedCompleteFacetContactBand':verified,'bandM':band,'exactProjectionCoverage':coverage,
        'exactMinimumOverAllOriginalPlanesM':str(min(gaps)) if gaps else None,
        'exactMaximumOverAllOriginalPlanesM':str(max(gaps)) if gaps else None,
        'allOriginalIntersectingPlanePieces':pieces,'continuousBoundsCertified':bool(gaps),
        'sampledMaximumUsedForAcceptance':False,'installationApproved':False}
