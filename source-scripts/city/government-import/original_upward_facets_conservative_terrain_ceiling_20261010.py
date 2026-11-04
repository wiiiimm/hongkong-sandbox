"""Candidate-only terrain ceiling from complete unchanged upward source facets.

Exact closed projected intersections include edge/point contacts. Every vertex
of an intersecting height-bearing terrain facet is capped conservatively below
the minimum original AND literal source altitude. All shared records move
together; original non-height terrain records are protected. This deliberately
changes terrain, never building geometry. It grants no installation acceptance.
"""
import hashlib
import numpy as np
from exact_original_projection_coverage_20261009 import point, signed_area, clip

def hash_array(a):return hashlib.sha256(np.asarray(a).tobytes()).hexdigest()

def intersection(a,b):
    a=[point(p) for p in a];b=[point(p) for p in b]
    assert signed_area(a)!=0 and signed_area(b)!=0
    if signed_area(b)<0:b=list(reversed(b))
    for p,q in zip(b,b[1:]+b[:1]):
        a=clip(a,p,q,True)
        if not a:break
    return a

def ceiling(original,literal,position,index):
    source=np.asarray(original,np.float64);actual=np.asarray(literal,np.float64)
    p=np.asarray(position,np.float64);idx=np.asarray(index,np.uint32)
    assert source.shape==actual.shape and source.ndim==3 and source.shape[1:]==(3,3)
    assert p.ndim==2 and p.shape[1]==3 and idx.ndim==2 and idx.shape[1]==3
    assert len(source) and len(p) and len(idx) and idx.max()<len(p)
    assert all(np.isfinite(x).all() for x in [source,actual,p])
    assert np.max(np.abs(source-actual))<=1e-9,'Literal source correspondence only; no contact welding'
    ground=p[idx];gxz=ground[:,:,[0,2]]
    norms=np.cross(source[:,1]-source[:,0],source[:,2]-source[:,0])
    upward=np.flatnonzero(norms[:,1]>0)
    assert len(upward)
    height=np.array([signed_area([point(v) for v in t])!=0 for t in gxz])
    protected=set(map(int,idx[~height].reshape(-1)))
    low=gxz.min(axis=1);high=gxz.max(axis=1)
    limits=np.full(len(p),np.inf);witnesses=[]
    for face in upward:
        pair=np.stack([source[face],actual[face]])
        xz=pair[:,:,[0,2]];lo=xz.min((0,1));hi=xz.max((0,1))
        candidates=np.flatnonzero(height&np.all(high>=lo,axis=1)&np.all(low<=hi,axis=1))
        bound=float(pair[:,:,1].min());rounded=np.float32(bound)
        if float(rounded)>bound:rounded=np.nextafter(rounded,np.float32(-np.inf))
        cap=float(rounded);assert cap<=bound
        selected=[]
        for j in candidates:
            intersections=[intersection(t,gxz[j]) for t in xz]
            if not any(intersections):continue
            selected.append(int(j));limits[idx[j]]=np.minimum(limits[idx[j]],cap)
        witnesses.append(dict(originalFace=int(face),minimumOriginalAndLiteralAltitude=bound,float32TerrainCeiling=cap,completeClosedProjectedTerrainFaceIndices=selected))
    groups={}
    for i,v in enumerate(p):groups.setdefault(tuple(v),[]).append(i)
    for ids in groups.values():limits[ids]=limits[ids].min()
    changed=np.flatnonzero(p[:,1]>limits)
    assert not (set(map(int,changed))&protected),'Ceiling would alter an original non-height terrain record'
    result=p.copy();result[changed,1]=limits[changed]
    assert np.array_equal(result[:,[0,2]],p[:,[0,2]]) and np.all(result[:,1]<=p[:,1])
    assert np.array_equal(result[idx[~height]],ground[~height])
    for row in witnesses:
        ids=idx[row['completeClosedProjectedTerrainFaceIndices']]
        assert not len(ids) or np.all(result[ids,1]<=row['minimumOriginalAndLiteralAltitude'])
    return result,dict(contract='candidate-only-original-and-literal-whole-upward-roof-terrain-ceiling-v1',completeOriginalFaces=len(source),completeUpwardSourceFaces=len(upward),completeTerrainFaces=len(idx),originalWorldSHA256=hash_array(source),literalWorldSHA256=hash_array(actual),terrainPositionBeforeSHA256=hash_array(p),terrainPositionAfterSHA256=hash_array(result),terrainIndexSHA256=hash_array(idx),protectedOriginalNonheightTerrainFaces=np.flatnonzero(~height).tolist(),changedRawVertexRecords=changed.tolist(),maximumTerrainLoweringM=float((p[:,1]-result[:,1]).max()),completeRoofCeilingWitnesses=witnesses,buildingGeometryChanges=0,terrainGeometryChanges=len(changed),noToleranceOrBufferCredit=True,sourceSupportAccepted=False,currentAcceptancePassed=False,publication=False)
