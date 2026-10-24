"""Authenticate append-only saved full22 nomination bytes; no new geometry."""
import numpy as np
from upton_append_current_plane_nomination_binding_v1_20261014 import digest

def validate_binding(nom,previous,patch,parents):
 old=np.asarray(previous['candidateRawPositionTriplets'],dtype='<f8');raw=np.asarray(nom['candidateRawPositionTriplets'],dtype='<f8');n=len(old)
 assert raw.ndim==3 and raw.shape[1:]==(3,3) and len(raw)>n and np.isfinite(raw).all()
 assert raw[:n].tobytes()==old.tobytes() and nom['candidateFaceProvenance'][:n]==previous['candidateFaceProvenance']
 assert len(nom['candidateFaceProvenance'])==len(raw)
 mapping=nom['completePreviousCandidateMapping'];assert len(mapping)==n
 for i,r in enumerate(mapping):assert r['oldCandidateFace']==i and r['newCandidateFaces']==[i] and r['allOldRawProvenanceBytesUnchanged']
 assert nom['completeOriginalCandidateMappingHistoricalOldPrefixVerbatim']==previous['completeOldNewIndexMapping']
 assert nom['protectedWholeCurrentTripletsUnchanged']==previous['protectedWholeCurrentTripletsUnchanged']
 for r in nom['protectedWholeCurrentTripletsUnchanged']:assert digest(raw[r['newCandidate']])==r['rawTripletSHA256']
 mesh=nom['newNativeMesh'];oldmesh=patch['nativeMesh'];pos=np.asarray(mesh['position'],dtype='<f8');idx=np.asarray(mesh['index'],dtype=np.int64)
 assert pos.ndim==1 and len(pos)%3==0 and np.isfinite(pos).all() and idx.ndim==1 and len(idx)==len(raw)*3
 assert all(type(i)is int for i in mesh['index']) and idx.min()>=0 and idx.max()<len(pos)//3
 assert np.asarray(mesh['position'][:len(oldmesh['position'])],dtype='<f8').tobytes()==np.asarray(oldmesh['position'],dtype='<f8').tobytes()
 assert mesh['index'][:len(oldmesh['index'])]==oldmesh['index'] and pos.reshape(-1,3)[idx.reshape(-1,3)].tobytes()==raw.astype('<f4').astype('<f8').tobytes()
 assert raw[n:].tobytes()==raw[n:].astype('<f4').astype('<f8').tobytes()
 assert nom['addedCandidateFaceIDs']==list(range(n,len(raw)))
 parentmap=nom['completeRestoredCurrentCounterpartMapping'];assert len(parentmap)==len(parents)
 assigned=[]
 for row,parent in zip(parentmap,parents):
  assert row['originalCurrentFace']==parent['originalCurrentFace'] and row['completeCurrentCounterpartVerbatim']==parent
  for j in row['addedCandidateFaces']:
   assert type(j)is int and n<=j<len(raw);assigned.append(j);p=nom['candidateFaceProvenance'][j]
   assert p['candidateFace']==j and p['kind']=='capturedCurrentRing' and p['originalFace']==parent['originalCurrentFace']
   assert p['completeCurrentSourceAttribution']==parent['completeCurrentAttribution'] and p['rawNominationFaceSHA256']==digest(raw[j])
   assert p['computedFragment'] and not p['savedInputByteExact'] and p['currentRestoration']['noOtherLayerYUsed']
   q=p['currentRestoration'];assert q['originalCurrentTripletSHA256']==parent['wholeOriginalCurrentTripletSHA256']
   inside=parent['completeOwnCurrentPlaneMaskPartition']['inside'];assert 0<=q['ownPlaneInsidePolygonOrdinal']<len(inside)
   assert q['exactSavedInsidePolygonVerbatim']==inside[q['ownPlaneInsidePolygonOrdinal']] and q['savedCompiledMaskOrdinal']==q['exactSavedInsidePolygonVerbatim']['mask']
 assert sorted(assigned)==list(range(n,len(raw))), 'each appended facet must have exactly one authenticated own-current-plane ancestor'
 assert nom['completeNewCandidateFacets']==len(raw) and nom['completeNewRawCandidateSHA256']==digest(raw)
 return raw
