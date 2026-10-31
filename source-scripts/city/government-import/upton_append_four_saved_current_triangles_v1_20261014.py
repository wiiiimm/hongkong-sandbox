"""Append complete authenticated current tuples without any new packing."""
from copy import deepcopy
import numpy as np
from upton_append_current_plane_nomination_binding_v1_20261014 import digest

def append_saved_current(raw,provenance,mesh,records,protected):
 old=np.asarray(raw,dtype='<f8');assert old.ndim==3 and old.shape[1:]==(3,3) and len(provenance)==len(old)
 pos=np.asarray(mesh['position'],dtype='<f8').reshape(-1,3);idx=np.asarray(mesh['index'],dtype=np.int64).reshape(-1,3)
 assert pos[idx].tobytes()==old.tobytes() and old.tobytes()==old.astype('<f4').astype('<f8').tobytes()
 assert len({r['originalCurrentFace']for r in records})==len(records)
 for r in protected:assert digest(old[r['newCandidate']])==r['rawTripletSHA256']
 positions=list(mesh['position']);indices=list(mesh['index']);new_raw=old.tolist();new_pv=deepcopy(provenance);mapping=[]
 for r in records:
  face=np.asarray(r['wholeOriginalCurrentTriplet'],dtype='<f8');assert face.shape==(3,3) and np.isfinite(face).all()
  assert digest(face)==r['wholeOriginalCurrentTripletSHA256'] and face.tobytes()==face.astype('<f4').astype('<f8').tobytes(), 'entire current triplet must already be exact Float32; never silently pack'
  assert r['completeCurrentAttribution']['globalCurrentFace']==r['originalCurrentFace'] and r['completeCurrentAttribution']['globalOrderedSavedFaceSHA256']==digest(face)
  j=len(new_raw);k=len(positions)//3;positions.extend(face.reshape(-1).tolist());indices.extend(range(k,k+3));new_raw.append(face.tolist())
  new_pv.append(dict(candidateFace=j,kind='capturedCurrentRing',originalFace=r['originalCurrentFace'],completeCurrentSourceAttribution=deepcopy(r['completeCurrentAttribution']),region='wholeSavedCurrentCounterpartRestoration',computedFragment=False,savedInputByteExact=True,rawNominationFaceSHA256=digest(face),wholeCurrentCounterpartRestorationWithoutNewPacking=True))
  mapping.append(dict(originalCurrentFace=r['originalCurrentFace'],newCandidateFace=j,completeWholeCurrentCounterpartVerbatim=deepcopy(r)))
 assert np.asarray(new_raw[:len(old)],dtype='<f8').tobytes()==old.tobytes() and new_pv[:len(old)]==provenance and positions[:len(mesh['position'])]==mesh['position'] and indices[:len(mesh['index'])]==mesh['index']
 return dict(candidateRawPositionTriplets=new_raw,candidateFaceProvenance=new_pv,newNativeMesh=dict(position=positions,index=indices),completePreviousCandidateMapping=[dict(oldCandidateFace=i,newCandidateFaces=[i],allOldRawProvenanceBytesUnchanged=True)for i in range(len(old))],completeWholeCurrentRestorationMapping=mapping,protectedWholeCurrentTripletsUnchanged=deepcopy(protected),originalPositionIncludingUnusedAndIndexExactPrefixes=True,noNewPackingOrSourcePlaneInterpolation=True)
