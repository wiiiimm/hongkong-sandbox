"""Bounded connected original wall paths for unresolved Opus rim points."""
from pathlib import Path
from collections import deque
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from opus_triangle_intersections_v1_20261017 import contact
from pool_local_wall_paths_v1_20261017 import clip_segment
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-opus-triangle-intersections-v1-20261017';BATCH='government-xl-opus-local-paths-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for ref in r['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
 original=BASE/'government-xl-opus-exact-wall-interfaces-v1-20261017';inp=read(original/'input.json');g=next(g for g in read(ROOT/inp['geometryPath'])['rows'] if g['uid']=='landsd/248432:0');support=np.array(g['position']).reshape(-1,3)[np.array(g['index']).reshape(-1,3)]
 path=BASE/'government-xl-opus-companion-original-v1-20261016/original-geometry.json.gz';g=read(path);tri=np.array(g['position']).reshape(-1,3)[np.array(g['index']).reshape(-1,3)]
 normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);lengths=np.linalg.norm(normals,axis=1);normals=np.divide(normals,lengths[:,None],out=np.zeros_like(normals),where=lengths[:,None]>0)
 failures=[x for x in read(PRIOR/'contacts.json.gz')['rows'] if x['witness'] is None];assert len(failures)==2 and all(x['uid']=='landsd/319559:0' for x in failures)
 output=[]
 for row in failures:
  p=np.array(row['position']);radius=.5/np.sqrt(3);lo=p+[-radius,0,-radius];hi=p+radius
  eligible=[i for i,t in enumerate(tri) if lengths[i]>0 and abs(normals[i,1])<=.1 and np.all(t.max(axis=0)>=lo) and np.all(t.min(axis=0)<=hi)]
  edges={}
  for i in eligible:
   for j in range(3):edges.setdefault(tuple(sorted((tuple(tri[i,j]),tuple(tri[i,(j+1)%3])))),[]).append(i)
  adj={i:[] for i in eligible}
  for edge,faces in edges.items():
   clipped=clip_segment(*map(np.array,edge),lo,hi)
   if clipped is None:continue
   for a in faces:
    for b in faces:
     if a!=b:adj[a].append((b,clipped.tolist()))
  starts=[i for i in eligible if np.linalg.norm(closest(p,tri[i])-p)<=.001];parents={i:None for i in starts};crossings={};queue=deque(starts)
  while queue:
   i=queue.popleft()
   for j,edge in adj[i]:
    if j not in parents:parents[j]=i;crossings[j]=edge;queue.append(j)
  candidates=[];ids=np.flatnonzero(np.all(support.max(axis=1)>=lo,axis=1)&np.all(support.min(axis=1)<=hi,axis=1))
  for i in parents:
   for j in ids:
    q=contact(p,tri[i],support[j])
    if q is None or not (np.all(q>=lo-1e-9) and np.all(q<=hi+1e-9)):continue
    chain=[i]
    while parents[chain[-1]] is not None:chain.append(parents[chain[-1]])
    chain.reverse();candidates.append(dict(sourceFaces=chain,sourceTriangles=tri[chain].tolist(),clippedSharedEdges=[crossings[k] for k in chain[1:]],supportFace=int(j),supportTriangle=support[j].tolist(),contact=q.tolist(),distanceM=float(np.linalg.norm(q-p))))
  candidates.sort(key=lambda x:x['distanceM']);output.append(dict(position=p.tolist(),localPrism=[lo.tolist(),hi.tolist()],reachableWallFaces=len(parents),witness=candidates[0] if candidates else None))
 DOC.mkdir();save(DOC/'paths.json',dict(rows=output,fullAcceptance=False,qualification='Connected unmodified original wall triangles in a convex prism entirely within 0.5m of rim, with exact original podium intersection. Role and four-coordinate-mode review still required.'))
 refs=[Path(__file__),HERE/'opus_triangle_intersections_v1_20261017.py',HERE/'pool_local_wall_paths_v1_20261017.py',HERE/'pool_incident_wall_contacts_v1_20261017.py',PRIOR/'result.json',path,*[ROOT/x['path'] for x in r['evidenceRefs']]]
 out=module('opus_local_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-local-wall-paths-v1',refs,dict(uids=['landsd/248432:0','landsd/319559:0','landsd/322573:0'],witnesses=sum(x['witness'] is not None for x in output),total=len(output),fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],rows=output),flush=True)
if __name__=='__main__':main()
