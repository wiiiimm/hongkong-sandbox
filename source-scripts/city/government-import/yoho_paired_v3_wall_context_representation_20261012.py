"""Yoho-only paired-v3 field adapter; no proof recomputation/changed bound."""
import copy,hashlib,json
import numpy as np

def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def sha(a):return hashlib.sha256(np.asarray(a,dtype=np.float64).tobytes()).hexdigest()
def for_context(row,face,ground):
 source=np.asarray(face,float);terrain=np.asarray(ground,float)
 assert source.shape==(3,3)and terrain.ndim==3 and terrain.shape[1:]==(3,3)and len(terrain)and np.isfinite(source).all()and np.isfinite(terrain).all()
 coarse=row['priorCoarseBoundProofVerbatim']['completeOriginal'];paired=row['pairedExactOriginalFiniteBound']
 assert coarse['sourceFaceSHA256']==sha(source)and coarse['completeCurrentGroundSHA256']==sha(terrain)
 out=copy.deepcopy(row)
 if paired is None:
  assert coarse['existingOrdinaryClearanceBoundProved']is True
  assert row['completeOriginalBoundProved']==coarse['existingOrdinaryClearanceBoundProved']and row['groundProjectionCovered']==coarse['groundProjectionCovered']
  return out
 assert paired['contract']=='exact-original-source-prism-complete-finite-column-clearance-pruned-v3'
 inner=paired['sameConstraintOptimizedOrdinaryPrismProof']
 assert row['completeOriginalBoundProved']==paired['existingOrdinaryClearanceBoundProved']and row['groundProjectionCovered']==paired['groundProjectionCovered']
 for proof in[paired,inner]:assert proof['sourceFaceSHA256']==sha(source)and proof['completeCurrentGroundSHA256']==sha(terrain)
 lo=source[:,[0,2]].min(0);hi=source[:,[0,2]].max(0);xz=terrain[:,:,[0,2]]
 ids=list(map(int,np.flatnonzero(np.all(xz.max(1)>=lo,axis=1)&np.all(xz.min(1)<=hi,axis=1))))
 assert ids and coarse['allProjectedBoundingCandidateOriginalGroundFacets']==ids
 assert inner['allProjectedBoundingCandidateOriginalGroundFacets']==ids,'Paired-v3 nested candidate census differs from complete closed AABB selection'
 if 'allProjectedBoundingCandidateOriginalGroundFacets'in paired:assert paired['allProjectedBoundingCandidateOriginalGroundFacets']==ids
 adapted=copy.deepcopy(paired);adapted['allProjectedBoundingCandidateOriginalGroundFacets']=ids
 adapted['completePairedV3ProofVerbatim']=copy.deepcopy(paired)
 adapted['candidateIDsRepresentationOnly']=dict(priorCoarseProofSHA256=canonical(coarse),completePairedV3ProofSHA256=canonical(paired),nestedOptimizedOrdinaryProofSHA256=canonical(inner),completeClosedAABBCandidateIDs=ids,numericalProofRecomputed=False,boundsOrCoverageChanged=False)
 for key in['sourceFaceSHA256','completeCurrentGroundSHA256','exactCertifiedLowerClearanceM','groundProjectionCovered','completeOriginalProjectionCoverage','existingOrdinaryClearanceBoundProved','allExactFiniteSourceGroundPieces']:
  assert adapted[key]==paired[key]
 out['pairedExactOriginalFiniteBound']=adapted
 assert row=={**out,'pairedExactOriginalFiniteBound':paired}
 return out
