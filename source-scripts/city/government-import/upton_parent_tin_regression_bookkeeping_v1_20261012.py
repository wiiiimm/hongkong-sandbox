"""Diagnostic bookkeeping only; unchanged exact finite v5/paired v3 kernels.
No root/grade/role/terrain construction or acceptance predicates added.
"""
from fractions import Fraction as F
import hashlib
import numpy as np
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse
from exact_original_paired_finite_clearance_v3_20261011 import verify as paired

MODES=('original','literal','explicitLeftF32','explicitBalancedF32')
def sha(a):return hashlib.sha256(np.asarray(a,dtype='<f8').tobytes()).hexdigest()
def triangles(a):
 a=np.asarray(a,dtype='<f8');assert a.ndim==3 and a.shape[1:]==(3,3) and np.isfinite(a).all();return a
def closed_face_scope(world,domain):
 a=triangles(world);d=np.asarray(domain,dtype='<f8');assert d.shape==(4,)and np.isfinite(d).all()and d[0]<=d[2]and d[1]<=d[3]
 xz=a[:,:,[0,2]];lo=xz.min(1);hi=xz.max(1);mask=(hi[:,0]>=d[0])&(lo[:,0]<=d[2])&(hi[:,1]>=d[1])&(lo[:,1]<=d[3])
 ids=np.flatnonzero(mask);omitted=np.flatnonzero(~mask)
 assert len(ids)+len(omitted)==len(a)and not set(ids)&set(omitted)
 inside=np.all((lo>=d[:2])&(hi<=d[2:]),1)
 return dict(selectedFaceIDs=ids.tolist(),strictClosedBoundsDisjointFaceIDs=omitted.tolist(),wholeFaceWithinCapturedDomain=inside.tolist(),completeFaces=len(a),wholeWorldSHA256=sha(a),noTriangleClipping=True)
def ground_roi(full,bounds):
 g=triangles(full);b=np.asarray(bounds,dtype='<f8');assert b.shape==(2,3)and np.isfinite(b).all()and np.all(b[0]<=b[1])
 xz=g[:,:,[0,2]];ids=np.flatnonzero(np.all(xz.max(1)>=b[0,[0,2]],1)&np.all(xz.min(1)<=b[1,[0,2]],1))
 return ids,g[ids]
def finite_record(face,ground,reused=None):
 face=np.asarray(face,dtype='<f8');assert face.shape==(3,3)and np.isfinite(face).all();ground=triangles(ground)
 source_sha=sha(face);ground_sha=sha(ground)
 if reused is not None:
  assert reused['coarse']['sourceFaceSHA256']==source_sha and reused['coarse']['completeCurrentGroundSHA256']==ground_sha
  final=reused['paired']or reused['coarse']
  assert final['sourceFaceSHA256']==source_sha and final['completeCurrentGroundSHA256']==ground_sha
  assert bool(final['groundProjectionCovered'])==reused['projectionCovered']and bool(final['existingOrdinaryClearanceBoundProved'])==reused['ordinaryBoundProved']
  return dict(sourceFaceSHA256=source_sha,completeGroundSHA256=ground_sha,coarse=reused['coarse'],paired=reused['paired'],projectionCovered=reused['projectionCovered'],ordinaryBoundProved=reused['ordinaryBoundProved'],exactLowerM=final['exactCertifiedLowerClearanceM'],reusedImmutableFullProofVerbatim=True)
 if len(ground):
  ids,_=ground_roi(ground,np.array([face.min(0),face.max(0)]))
 else:ids=[]
 if not len(ids):
  return dict(sourceFaceSHA256=source_sha,completeGroundSHA256=ground_sha,coarse=None,paired=None,projectionCovered=False,ordinaryBoundProved=False,exactLowerM=None,allClosedProjectedBoundingCandidates=[],missingFiniteCandidate=True,reusedImmutableFullProofVerbatim=False)
 first=coarse(face,ground)
 # Coverage-v2 already completely decides coverage. Refinement is only needed
 # when a covered whole face has an insufficient conservative height bound.
 second=paired(face,ground)if first['groundProjectionCovered']and not first['existingOrdinaryClearanceBoundProved']else None
 final=second or first
 assert final['sourceFaceSHA256']==source_sha and final['completeCurrentGroundSHA256']==ground_sha
 return dict(sourceFaceSHA256=source_sha,completeGroundSHA256=ground_sha,coarse=first,paired=second,projectionCovered=bool(final['groundProjectionCovered']),ordinaryBoundProved=bool(final['existingOrdinaryClearanceBoundProved']),exactLowerM=final['exactCertifiedLowerClearanceM'],reusedImmutableFullProofVerbatim=False)
def comparison(current,original,within_domain):
 assert current['sourceFaceSHA256']==original['sourceFaceSHA256']
 for q in [current,original]:
  if q['ordinaryBoundProved']:assert q['projectionCovered']and F(q['exactLowerM'])>=-F(1,2)
 a=current['ordinaryBoundProved'];b=original['ordinaryBoundProved']
 return dict(currentCovered=current['projectionCovered'],originalTINCovered=original['projectionCovered'],currentOrdinaryBoundProved=a,originalTINOrdinaryBoundProved=b,currentClearOriginalTINUnproved=bool(a and not b),currentUnprovedOriginalTINClear=bool(not a and b),bothOrdinaryUnproved=bool(not a and not b),currentUncoveredOutsideCapturedDomainIsNotRuntimeGap=bool(not current['projectionCovered']and not within_domain),wholeFacetProofNotGradeRootOrAcceptance=True)
