"""Exact terrain-only consolidation preserving flat normals and vertex colour fields."""
import numpy as np
from exact_runtime_coplanar_consolidation_20261010 import consolidate

def colours(vertices,patch):
 v=np.asarray(vertices,dtype=np.float32).astype(float);g=patch['meta']['georef']
 c=np.floor((v[...,0]+834500-g['bE'])/g['aE']+.5).astype(int)
 r=np.floor((816500-v[...,2]-g['bN'])/g['aN']+.5).astype(int)
 c=np.clip(c,0,patch['w']-1);r=np.clip(r,0,patch['h']-1)
 return np.asarray(patch['vegetation'])[r*patch['w']+c]!=0

def consolidate_patch(patch):
 mesh=patch['nativeMesh'];v=np.asarray(mesh['position'],dtype=np.float32).astype(float).reshape(-1,3);idx=np.asarray(mesh['index']).reshape(-1,3)
 assert np.array_equal(idx.reshape(-1),np.arange(len(v))),'Flat nonshared terrain vertex contract required'
 faces=v[idx];colour=colours(faces,patch);same=(colour==colour[:,:1]).all(1);output=[];groups=[];covered=[]
 for green in [False,True]:
  ids=np.flatnonzero(same&(colour[:,0]==green));covered.extend(ids.tolist())
  if not len(ids):continue
  result,proof=consolidate(faces[ids]);assert (colours(result,patch)==green).all();start=len(output);output.extend(result)
  groups.append(dict(colour='green'if green else'urban',originalFaceIds=ids.tolist(),outputFaceRange=[start,len(output)],integerSurfaceCertificate=proof))
 mixed=np.flatnonzero(~same);covered.extend(mixed.tolist());start=len(output);output.extend(faces[mixed])
 assert sorted(covered)==list(range(len(faces)))
 result=np.asarray(output,float);assert np.array_equal(result,result.astype(np.float32).astype(float))
 return result,dict(originalFaces=len(faces),outputFaces=len(result),savedFaces=len(faces)-len(result),groups=groups,mixedColourOriginalFaceIds=mixed.tolist(),mixedColourOutputFaceRange=[start,len(result)],allOriginalFacesAccounted=True,sourceVerticesOnly=True,constantColourGroupsOnly=True,mixedColourFacesRetainedUnchanged=True,flatNormalsAndFinitePlaneSurfacesPreserved=True,sourceBuildingMeshesUsed=False,physicalAccepted=False,qualification='Only proved coplanar constant-colour groups are retriangulated using existing rendered Float32 vertices. Mixed-colour faces remain literal originals; production flat per-face normals and colour interpolation are preserved. Physical/runtime/browser checks remain mandatory.')
