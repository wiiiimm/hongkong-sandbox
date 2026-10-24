"""Exact full regional ground versus complete owned-bounds runtime ground census.

Closed X/Z facet AABBs nominate every facet meeting any complete owned stream
bound. No height/slope/area/epsilon selection; oriented dyadic byte records and
their multiplicities must equal the runtime inventory exactly.
"""
from collections import Counter
import hashlib,json,struct
import numpy as np
MODES={'providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix'}
def sha_array(a):return hashlib.sha256(np.asarray(a,dtype='<f8').tobytes()).hexdigest()
def bounds_sha(boxes):return hashlib.sha256(json.dumps(boxes,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def verify(regional,runtime,boxes,*,regional_sha,runtime_sha,owned_bounds_sha):
 a=np.asarray(regional,dtype='<f8');b=np.asarray(runtime,dtype='<f8')
 assert a.ndim==b.ndim==3 and a.shape[1:]==b.shape[1:]==(3,3) and len(a)>0 and len(b)>0
 assert np.isfinite(a).all() and np.isfinite(b).all() and set(boxes)==MODES
 assert sha_array(a)==regional_sha and sha_array(b)==runtime_sha and bounds_sha(boxes)==owned_bounds_sha
 valid=[]
 for mode in sorted(MODES):
  box=np.asarray(boxes[mode],dtype='<f8');assert box.shape==(2,3) and np.isfinite(box).all() and np.all(box[0]<=box[1]);valid.append(box)
 def record(t):return struct.pack('<9d',*(float(v)for v in t.flat))
 relevant=[]
 for i,t in enumerate(a):
  lo=t.min(0);hi=t.max(0)
  if any(lo[0]<=box[1,0] and hi[0]>=box[0,0] and lo[2]<=box[1,2] and hi[2]>=box[0,2] for box in valid):relevant.append(i)
 full=Counter(record(t)for t in a);actual=Counter(record(t)for t in b);needed=Counter(record(a[i])for i in relevant)
 assert not actual-full,'Runtime facet is not an exact regional oriented record with available multiplicity'
 assert actual==needed,'Every relevant whole facet, including vertical/degenerate/boundary-only records, must be included exactly once per source occurrence'
 return dict(completeRegionalGroundFacets=len(a),completeRuntimeGroundFacets=len(b),completeRelevantRegionalFacetIds=relevant,allRelevantFacetsExactlyIncluded=True,exactOrientedMultiplicityPreserved=True,regionalGroundSHA256=regional_sha,runtimeGroundSHA256=runtime_sha,completeOwnedBoundsSHA256=owned_bounds_sha,closedXZAABBSelection=True,heightSlopeAreaToleranceFiltersUsed=False,physicalRootCredit=False)
