"""Exact shared-vertex connectivity of held original faces; diagnostic only."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-stonecutters-far-components-v1-20261021';DOC=BASE/BATCH;refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py']
assert not DOC.exists()
def take(n,file):
 _,pins=authenticate(BASE/n);p=BASE/n/file;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([BASE/n/'result.json',p]);return read(p)
r=take('government-xl-six-far-faces-v1-20261021','127037:0.json.gz');sel=take('government-xl-next-twenty-current-terrain-v6-20261021','selection.json.gz');row=next(x for x in sel['rows']if x['uid']==r['uid']);p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p);tri=decode_original_world_triangles(p.read_bytes());assert digest(tri.astype('<f8').tobytes())==r['worldTrianglesSHA256']
parent=list(range(len(tri)))
def find(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
vertex={}
for i,t in enumerate(tri):
 for v in t:
  key=tuple(float(x)for x in v)
  if key in vertex:parent[find(i)]=find(vertex[key])
  else:vertex[key]=i
roots={find(i)for i in r['farFaceIds']};out=[]
for root in sorted(roots):
 ids=[i for i in range(len(tri))if find(i)==root];v=tri[ids];far=sorted(set(ids)&set(r['farFaceIds']));out.append(dict(faceIds=ids,faces=len(ids),farFaceIds=far,bounds=[v.min((0,1)).tolist(),v.max((0,1)).tolist()],surfaceAreaM2=float(np.linalg.norm(np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]),axis=1).sum()/2)))
assert sum(len(x['farFaceIds'])for x in out)==18
result=dict(uids=[r['uid']],sourceSHA256=r['sourceSHA256'],worldTrianglesSHA256=r['worldTrianglesSHA256'],components=out,totalExactVertexComponents=len({find(i)for i in range(len(tri))}),sourceGeometryChanges=0,installationApproved=False,qualification='Exact shared-vertex connectivity only; separate authoring meshes can meet without shared vertices. No semantic identity approval, no simplification or source edits.')
save(DOC/'components.json',result);module('stone_components',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-far-face-connectivity',refs,result);print([(x['faces'],len(x['farFaceIds']),x['bounds'])for x in out],flush=True)
