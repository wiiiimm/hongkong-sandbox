"""Append-only saved terrain binding. No terrain acceptance or source decoding."""
from copy import deepcopy
import hashlib
import numpy as np

def digest(v):
 return hashlib.sha256(np.asarray(v,dtype='<f8').tobytes()).hexdigest()

def append_bound_pieces(raw,provenance,mesh,additions,protected,cumulative):
 raw=np.asarray(raw,dtype='<f8');assert raw.ndim==3 and raw.shape[1:]==(3,3)
 assert len(provenance)==len(raw) and np.isfinite(raw).all()
 pos=np.asarray(mesh['position'],dtype='<f8');idx=np.asarray(mesh['index'],dtype=np.int64)
 assert pos.ndim==1 and len(pos)%3==0 and idx.ndim==1 and len(idx)==len(raw)*3
 assert all(type(i)is int for i in mesh['index']) and idx.min()>=0 and idx.max()<len(pos)//3
 assert pos.reshape(-1,3)[idx.reshape(-1,3)].tobytes()==raw.astype('<f4').astype('<f8').tobytes()
 protected_ids=[r['newCandidate']for r in protected];assert len(set(protected_ids))==len(protected_ids)
 for r in protected:assert 0<=r['newCandidate']<len(raw) and digest(raw[r['newCandidate']])==r['rawTripletSHA256']
 assert [r['oldCandidateFace']for r in cumulative]==list(range(len(cumulative)))
 flat=[j for r in cumulative for j in r['newCandidateFaces']]
 assert sorted(flat)==list(range(len(raw))), 'cumulative old mapping must cover every old candidate exactly once'
 new_raw=raw.tolist();new_prov=deepcopy(provenance);new_mesh=deepcopy(mesh)
 new_pos=list(mesh['position']);new_idx=list(mesh['index']);added=[]
 for item in additions:
  trip=np.asarray(item['packedPieceTriplet'],dtype='<f8');assert trip.shape==(3,3) and np.isfinite(trip).all()
  assert trip.tobytes()==trip.astype('<f4').astype('<f8').tobytes(), 'append only actual Float32 packed tuples'
  j=len(new_raw);record=deepcopy(item['provenance']);assert record['candidateFace']==j and record['rawNominationFaceSHA256']==digest(trip)
  start=len(new_pos)//3;new_pos.extend(trip.reshape(-1).tolist());new_idx.extend(range(start,start+3))
  new_raw.append(trip.tolist());new_prov.append(record);added.append(j)
 new_mesh['position']=new_pos;new_mesh['index']=new_idx
 assert np.asarray(new_pos[:len(pos)],dtype='<f8').tobytes()==pos.tobytes()
 assert new_idx[:len(idx)]==mesh['index'] and new_prov[:len(raw)]==provenance
 assert np.asarray(new_raw[:len(raw)],dtype='<f8').tobytes()==raw.tobytes()
 return dict(candidateRawPositionTriplets=new_raw,candidateFaceProvenance=new_prov,newNativeMesh=new_mesh,
             completePreviousCandidateMapping=[dict(oldCandidateFace=i,newCandidateFaces=[i],allOldRawProvenanceBytesUnchanged=True)for i in range(len(raw))],
             completeOriginalCandidateMappingHistoricalOldPrefixVerbatim=deepcopy(cumulative),
             protectedWholeCurrentTripletsUnchanged=deepcopy(protected),addedCandidateFaceIDs=added,
             originalPositionIncludingUnusedAndIndexExactPrefixes=True,allPreviousRawAndProvenanceBytesRetained=True)
