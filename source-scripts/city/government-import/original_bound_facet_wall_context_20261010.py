"""Named diagnostic wall contexts from independently fenced finite facet proofs.

The minimum is a certified lower bound, not a claimed exact physical minimum.
The positive exposure witness is a conservative bound at an actual highest
original vertex. Old raw contexts are untouched. No role, root or install credit.
"""
import hashlib,json,math
from fractions import Fraction as F
import numpy as np

def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def sha(a):return hashlib.sha256(np.asarray(a,dtype=np.float64).tobytes()).hexdigest()
def down(v):
 r=float(v)
 assert math.isfinite(r)
 return math.nextafter(r,-math.inf) if F.from_float(r)>v else r

def contexts(triangles,ground,proof_rows,*,expected_binding,current_binding):
 tri=np.asarray(triangles,dtype=np.float64);g=np.asarray(ground,dtype=np.float64)
 assert tri.ndim==3 and tri.shape[1:]==(3,3) and len(tri) and np.isfinite(tri).all()
 assert g.ndim==3 and g.shape[1:]==(3,3) and len(g) and np.isfinite(g).all()
 assert expected_binding==current_binding
 assert current_binding['completeOriginalWorldTrianglesSHA256']==sha(tri)
 assert current_binding['completeDrawnGroundSHA256']==sha(g)
 assert current_binding['completeFiniteFacetProofRowsSHA256']==canonical(proof_rows)
 assert len(proof_rows)==len(tri)
 out=[]
 for i,(t,row) in enumerate(zip(tri,proof_rows)):
  assert row['sourceFace']==i and row['priorCoarseBoundProofVerbatim']['sourceFace']==i
  coarse=row['priorCoarseBoundProofVerbatim']['completeOriginal'];paired=row['pairedExactOriginalFiniteBound']
  assert coarse['sourceFaceSHA256']==sha(t) and coarse['completeCurrentGroundSHA256']==sha(g)
  p=coarse if coarse['existingOrdinaryClearanceBoundProved'] else paired
  assert p is not None and p['sourceFaceSHA256']==sha(t) and p['completeCurrentGroundSHA256']==sha(g)
  assert p['groundProjectionCovered'] is True and p['completeOriginalProjectionCoverage']['exactProjectionCovered'] is True
  bound=F(p['exactCertifiedLowerClearanceM'])
  assert p['existingOrdinaryClearanceBoundProved']==(bound>=F(-1,2))
  assert row['completeOriginalBoundProved']==(bound>=F(-1,2))
  lo=t[:,[0,2]].min(axis=0);hi=t[:,[0,2]].max(axis=0);xz=g[:,:,[0,2]]
  ids=np.flatnonzero(np.all(xz.max(axis=1)>=lo,axis=1)&np.all(xz.min(axis=1)<=hi,axis=1))
  assert len(ids) and list(map(int,ids))==p['allProjectedBoundingCandidateOriginalGroundFacets']
  # Every terrain facet that can cover the actual highest original vertex
  # belongs to this complete AABB list. Even overestimating terrain height
  # remains conservative. Collapsed projections also count in this maximum.
  vertex=int(np.argmax(t[:,1]));top=F.from_float(float(t[vertex,1]));highest=max(F.from_float(float(v)) for v in g[ids,:,1].flat)
  exposure=top-highest
  out.append(dict(sourceFace=i,groundProjectionCovered=True,minimum=dict(minimumGapM=down(bound),qualification='Certified finite-facet lower bound; not asserted exact minimum'),maximumObservedGapM=down(exposure),exposureQualification='Conservative actual highest-original-vertex gap lower bound; not asserted exact maximum',exactCertifiedLowerClearanceM=str(bound),actualHighestOriginalVertex=t[vertex].tolist(),allExposureBoundingGroundFacets=list(map(int,ids)),exactExposureLowerBoundM=str(exposure),sourceFaceSHA256=sha(t),finiteFacetProofSHA256=canonical(p),rawPriorDiagnosticChanged=False,fullAcceptance=False,rootOrContactCredit=False))
 return out
