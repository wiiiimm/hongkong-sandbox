"""Replay only an exact complete immutable coarse clearance input row.

The caller must independently verify the fenced receipt and original producing
kernel bytes. This cache includes failures verbatim and grants no acceptance.
Every original/rendered face SHA, full drawn-ground SHA, row order and all
whole-source bindings must equal freshly decoded current inputs exactly.
"""
import hashlib,json
import numpy as np
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def reuse(cached,source_sha,triangles,world,ground,*,expected_cached_sha):
 tri=np.asarray(triangles,float);world=np.asarray(world,float);ground=np.asarray(ground,float);assert tri.ndim==3 and tri.shape[1:]==(3,3) and world.shape==tri.shape and ground.ndim==3 and ground.shape[1:]==(3,3) and len(ground) and np.isfinite(tri).all() and np.isfinite(world).all() and np.isfinite(ground).all()
 assert canonical(cached)==expected_cached_sha,'Immutable complete cache row changed'
 sha=lambda a:hashlib.sha256(a.tobytes()).hexdigest();assert cached['sourceSHA256']==source_sha and cached['completeOriginalFaces']==len(tri) and cached['completeOriginalWorldSHA256']==sha(tri) and cached['completeActualRenderedWorldSHA256']==sha(world) and cached['completeGroundSHA256']==sha(ground)
 ground_sha=sha(ground);rows=cached['allFaces'];assert len(rows)==len(tri)
 for i,r in enumerate(rows):
  assert r['sourceFace']==i
  for key,face in [('completeOriginal',tri[i]),('actualRendered',world[i])]:
   p=r[key];assert p['sourceFaceSHA256']==sha(face) and p['completeCurrentGroundSHA256']==ground_sha and p['contract']=='exact-original-facet-conservative-vertex-clearance-v2-exact-disjoint-pruning';assert type(p['existingOrdinaryClearanceBoundProved']) is bool
 assert cached['unprovedOriginalFaceBounds']==[r['sourceFace'] for r in rows if not r['completeOriginal']['existingOrdinaryClearanceBoundProved']]
 assert cached['unprovedActualRenderedFaceBounds']==[r['sourceFace'] for r in rows if not r['actualRendered']['existingOrdinaryClearanceBoundProved']]
 return json.loads(json.dumps(cached))
