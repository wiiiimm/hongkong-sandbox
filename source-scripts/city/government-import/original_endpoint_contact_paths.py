"""Find exact-edge source-face paths to finite contacts within endpoint heights.
No model edits, architectural role inference or publication approval.
"""
import argparse
from pathlib import Path
from collections import defaultdict,deque
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import'
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ['batch','contacts','capture']:p.add_argument('--'+key,required=True)
 a=p.parse_args();out=BASE/a.batch;assert not out.exists();refs=[Path(__file__)];cache={}
 def take(n,path):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(path.read_bytes())==cache[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 report=take(a.contacts,BASE/a.contacts/'contacts.json.gz');runtime=take(a.capture,HERE/'local'/a.capture/'runtime-geometry.json.gz');uid=report['uid'];supportuid=report['supportUid']
 def tri(g):return np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 source=next(r for r in runtime['rows']if r['uid']==uid);support=next(r for r in runtime['rows']if r['uid']==supportuid);t=tri(source)
 assert digest(t.tobytes())==report['sourceWorldSHA256'] and digest(tri(support).tobytes())==report['supportWorldSHA256']
 targets=[r for r in report['targets']if not r['positiveContacts']];assert 0<len(targets)<=1000
 contacts=[c for c in report['proof']['contacts']if c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 and c['dimension']>0]
 edges=defaultdict(list);adj=defaultdict(dict)
 for i,face in enumerate(t):
  for x,y in [(0,1),(1,2),(2,0)]:
   edge=tuple(sorted((tuple(face[x]),tuple(face[y]))))
   if edge[0]!=edge[1]:edges[edge].append(i)
 for edge,ids in edges.items():
  for x in ids:
   for y in ids:
    if x!=y:adj[x][y]=edge
 endpoints=[(c,np.array([[float(Fraction(v))for v in q]for q in c['exactPoints']]).mean(0))for c in sorted(contacts,key=lambda c:-c['maximumSpanM'])]
 rows=[]
 for target in targets:
  start=np.asarray(target['witness']['position']);found=None
  for contact,end in endpoints:
   ceiling=max(start[1],end[1]);terminal=contact['sourceFaceA'];queue=deque(target['incidentFaces']);previous={i:None for i in queue}
   while queue and terminal not in previous:
    x=queue.popleft()
    for y,edge in adj[x].items():
     if y not in previous and min(q[1]for q in edge)<=ceiling:previous[y]=x;queue.append(y)
   if terminal not in previous:continue
   ids=[];at=terminal
   while at is not None:ids.append(at);at=previous[at]
   ids.reverse();points=[start]
   for x,y in zip(ids,ids[1:]):
    low,high=map(np.asarray,adj[x][y]);assert min(low[1],high[1])<=ceiling
    if max(low[1],high[1])>ceiling:
     cut=low+(high-low)*((ceiling-low[1])/(high[1]-low[1]))
     if low[1]>ceiling:low=cut
     else:high=cut
    points.append((low+high)/2)
   points.append(end);errors=[float(np.linalg.norm(closest(q,t[f])-q))for i,f in enumerate(ids)for q in points[i:i+2]]
   if max(errors)>.001:continue
   maximum=float(max(q[1]for q in points));assert maximum<=ceiling+1e-9
   found=dict(faces=ids,continuousPath=[q.tolist()for q in points],maximumResidualM=max(errors),endpointHeightCeilingM=float(ceiling),maximumPathHeightM=maximum,withinEndpointHeight=True,contact=contact);break
  rows.append(dict(witness=target['witness'],incidentFaces=target['incidentFaces'],verifiedPath=found))
 result=dict(uids=[uid,supportuid],uid=uid,supportUid=supportuid,sourceWorldSHA256=report['sourceWorldSHA256'],supportWorldSHA256=report['supportWorldSHA256'],targets=len(rows),finiteEndpointBoundedPaths=sum(r['verifiedPath']is not None for r in rows),remaining=sum(r['verifiedPath']is None for r in rows),sourceGeometryChanges=0,installationApproved=False)
 save(out/'paths.json.gz',dict(**result,rows=rows));save(out/'summary.json',result);refs.append(HERE/'pool_incident_wall_contacts_v1_20261017.py');module('endpoint_path_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'finite-own-endpoint-height-original-support-paths',refs,result);print(result,flush=True)
if __name__=='__main__':main()
