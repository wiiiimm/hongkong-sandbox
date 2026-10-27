"""Restore only missing exact original facets on an unchanged domain boundary."""
from collections import Counter
import numpy as np
import shapely

def preserve_boundary_facets(original,candidate,bounds,edit):
    original=np.asarray(original,float);candidate=np.asarray(candidate,float)
    assert original.ndim==candidate.ndim==3 and original.shape[1:]==candidate.shape[1:]==(3,3)
    assert np.isfinite(original).all() and np.isfinite(candidate).all()
    rendered=original.astype('float32').astype(float)
    available=Counter(tuple(sorted(map(tuple,f)))for f in candidate.astype('float32').astype(float))
    wanted=Counter();eligible=[]
    x0,z0,x1,z1=bounds
    for i,face in enumerate(rendered):
        edge=any(np.all(face[:,axis]==value)for axis,value in [(0,x0),(0,x1),(2,z0),(2,z1)])
        if not edge:continue
        assert np.cross(face[1]-face[0],face[2]-face[0])[1]==0
        key=tuple(sorted(map(tuple,face)));wanted[key]+=1;eligible.append((i,key))
    missing=wanted-available;restored=[];rows=[]
    for i,key in eligible:
        if not missing[key]:continue
        face=original[i]
        assert shapely.MultiPoint(rendered[i][:,[0,2]]).convex_hull.disjoint(edit),'Original boundary facet touches edit region'
        restored.append(face.copy());rows.append(dict(originalFace=i,originalVertices=face.tolist(),renderedVertices=rendered[i].tolist(),multiplicityRestored=1));missing[key]-=1
    assert not +missing
    output=np.concatenate([candidate,np.asarray(restored)])if restored else candidate.copy()
    assert np.array_equal(output[:len(candidate)],candidate)
    final=Counter(tuple(sorted(map(tuple,f)))for f in output.astype('float32').astype(float))
    assert all(final[key]>=count for key,count in wanted.items())
    return output,rows
