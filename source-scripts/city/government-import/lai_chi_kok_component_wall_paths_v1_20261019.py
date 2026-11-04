"""Exact shared-edge original wall connectivity, never tolerance welding or approval."""
from pathlib import Path
from collections import defaultdict,deque
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-component-wall-paths-v1-20261019';DOC=BASE/BATCH;ATTR=BASE/'government-xl-lai-chi-kok-eight-render-attributes-v1-20261019';FOUND=BASE/'government-xl-lai-chi-kok-eight-foundations-v1-20261019'
def paths(tri,affected):
 normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1);valid=length>0;ratio=np.divide(normal[:,1],length,out=np.zeros(len(tri)),where=valid);walls=set(np.flatnonzero(valid&(np.abs(ratio)<=.25)).tolist());roofs=set(np.flatnonzero(valid&(ratio>.25)).tolist());nodes=walls|roofs;edges=defaultdict(list);adj={i:set()for i in nodes}
 for i in nodes:
  for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
   if np.array_equal(a,b):continue
   edges[tuple(sorted((tuple(a),tuple(b))))].append(i)
 for fs in edges.values():
  for i in fs:adj[i].update(j for j in fs if j!=i)
 previous={i:None for i in roofs};todo=deque(sorted(roofs))
 while todo:
  i=todo.popleft()
  for j in sorted(adj[i]):
   if j not in previous:previous[j]=i;todo.append(j)
 rows=[]
 for i in affected:
  path=[i]
  while path[-1]in previous and previous[path[-1]]is not None:path.append(previous[path[-1]])
  rows.append(dict(faceId=i,normalYRatio=float(ratio[i]),isSteepSideFace=i in walls,sourceSharedEdgePath=path,endsOnOriginalUpwardFace=path[-1]in roofs))
 return dict(rows=rows,allSteepSideFaces=all(r['isSteepSideFace']for r in rows),allConnectedToOriginalUpwardFaces=all(r['endsOnOriginalUpwardFace']for r in rows),collapsedFaceIds=np.flatnonzero(~valid).tolist(),wholeSourceFaces=len(tri),coordinateSHA256=digest(np.asarray(tri,dtype='<f8').tobytes()))
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [ATTR,FOUND]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 sources=read(ATTR/'selection.json.gz')['rows'][1:];captures={r['uid']:r for r in read(ATTR/'attributes.json.gz')['rows']};summary=[]
 for source in sources:
  uid=source['uid'];a=captures[uid];worlds={'original':decode_original_world_triangles((ROOT/source['candidate']['path']).read_bytes())}
  for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(a[field],dtype='<f8').reshape(-1,3)[np.asarray(a['completeOriginalIndex']).reshape(-1,3)]
  for mode,t in worlds.items():
   f=read(FOUND/(uid.split('/')[1]+'-'+mode+'.json'));affected=[v['faceId']for v in f.get('buriedFaces',[])];proof=paths(t,affected);assert proof['coordinateSHA256']==f['wholeWorldSHA256'];save(DOC/(uid.split('/')[1]+'-'+mode+'.json'),dict(uid=uid,sourceSHA256=source['sourceSHA256'],mode=mode,proof=proof,installationApproved=False));summary.append(dict(uid=uid,mode=mode,affectedFaces=len(affected),allSteepSideFaces=proof['allSteepSideFaces'],allConnectedToOriginalUpwardFaces=proof['allConnectedToOriginalUpwardFaces']));print(summary[-1],flush=True)
 save(DOC/'summary.json',dict(rows=summary,qualification='Exact shared-full-edge source connectivity only. Upward destinations are not independently certified contact supports. No source welding, boundary snapping or acceptance credit.',installationApproved=False))
 module('wall_path_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-component-buried-side-face-connectivity',list(dict.fromkeys(refs)),dict(uids=[s['uid']for s in sources],rows=summary,installationApproved=False))
if __name__=='__main__':main()
