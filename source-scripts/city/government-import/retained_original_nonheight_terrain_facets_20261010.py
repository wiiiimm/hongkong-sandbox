"""Complete literal original terrain records omitted by a height sampler.

This helper only preserves coordinates/index records; it grants no terrain,
model, identity, support, collision, surface-equivalence or runtime acceptance.
"""
import copy,json
from fractions import Fraction as F
import numpy as np
from run import digest
from native_parent_child_flat_composition_20261010 import faces
def inventory(parent):
 assert parent.get('nativeMesh') and not parent.get('patches');a=faces(parent);assert np.isfinite(a).all();n=np.cross(a[:,1]-a[:,0],a[:,2]-a[:,0]);records=[]
 mesh=parent['nativeMesh'];raw=np.asarray(mesh['position'],float).reshape(-1,3);index=np.asarray(mesh['index'],int).reshape(-1,3)
 for i,t in enumerate(a):
  p,q,r=[tuple(F(float(v)) for v in p) for p in t];u=[q[k]-p[k] for k in range(3)];v=[r[k]-p[k] for k in range(3)];normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  records.append({'originalParentFace':i,'originalSourceIndices':index[i].tolist(),'originalRawPositionTriples':raw[index[i]].tolist(),'actualRenderedFloat32Triples':t.tolist(),'exactDyadicNormal':list(map(str,normal)),'exactZeroProjectedArea':normal[1]==0,'exactDegenerate3D':not any(normal),'excludedByCurrentHeightSampler':not bool(abs(n[i,1])>1e-10)})
 return {'completeOriginalParentFaces':len(a),'originalPositionSHA256':digest(json.dumps(mesh['position'],separators=(',',':')).encode()),'originalIndexSHA256':digest(json.dumps(mesh['index'],separators=(',',':')).encode()),'completeRenderedWorldSHA256':digest(a.astype('<f8').tobytes()),'allOriginalFaceRecords':records,'allHeightSamplerExcludedFaceIds':[r['originalParentFace'] for r in records if r['excludedByCurrentHeightSampler']],'physicalAccepted':False}
def append_omitted(candidate,parent,expected_world_sha,*,terrain_budget=100000):
 assert terrain_budget==100000,'Runtime terrain budget cannot be raised';proof=inventory(parent);assert proof['completeRenderedWorldSHA256']==expected_world_sha,'Original rendered parent changed';out=copy.deepcopy(candidate);mesh=out['nativeMesh'];assert not candidate.get('patches');oldp=copy.deepcopy(mesh['position']);oldi=copy.deepcopy(mesh['index']);existing={t.astype('<f8').tobytes() for t in faces(candidate)};raw=np.asarray(parent['nativeMesh']['position'],float).reshape(-1,3);idx=np.asarray(parent['nativeMesh']['index'],int).reshape(-1,3);records=[];mapping={}
 for faceid in proof['allHeightSamplerExcludedFaceIds']:
  t=faces(parent)[faceid];key=t.astype('<f8').tobytes();already=key in existing;newids=[]
  if not already:
   for originalindex in idx[faceid]:
    originalindex=int(originalindex)
    if originalindex not in mapping:mapping[originalindex]=len(mesh['position'])//3;mesh['position'].extend(raw[originalindex].tolist())
    newids.append(mapping[originalindex])
   mesh['index'].extend(newids);existing.add(key)
  records.append({'originalParentFace':faceid,'alreadyLiteralInCandidate':already,'newCandidateIndices':newids,'originalSourceIndices':idx[faceid].tolist(),'actualRenderedFloat32Triples':t.tolist()})
 assert mesh['position'][:len(oldp)]==oldp and mesh['index'][:len(oldi)]==oldi,'Existing terrain streams changed';assert len(mesh['index'])//3<=terrain_budget,'Final runtime terrain cap exceeded';final={t.astype('<f8').tobytes() for t in faces(out)};assert all(faces(parent)[i].astype('<f8').tobytes() in final for i in proof['allHeightSamplerExcludedFaceIds'])
 proof.update(literalRetainedFaceDispositions=records,finalCandidateFacets=len(mesh['index'])//3,existingCandidateStreamsUnchanged=True,allOmittedOriginalFacetsLiterallyRetained=True,sourceGeometryChanges=0,physicalAccepted=False,qualification='Complete exact dyadic classification and literal original raw/index retention for every facet excluded by the height-only sampler. Tiny nonzero and truly degenerate original records are retained, not relabelled or filtered. Independent full terrain/current/source/physical/runtime/browser gates remain mandatory.')
 return out,proof
