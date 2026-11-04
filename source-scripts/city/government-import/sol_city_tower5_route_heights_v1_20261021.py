"""Finite source-face paths bounded by their own contact endpoint heights."""
from pathlib import Path
from collections import defaultdict,deque
from fractions import Fraction
import numpy as np
import heapq
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sol-city-tower5-route-heights-v1-20261021';DOC=BASE/BATCH
CAP=BASE/'government-xl-sol-city-complete-capture-v1-20261021';CONTACT=BASE/'government-xl-sol-city-additional-tower-contacts-v1-20261021';FULL=BASE/'government-xl-yoho-mall-i-tower8-render-context-v1-20261020'
JOIN=BASE/'government-xl-sol-city-additional-tower-joins-v1-20261021'
JOIN2=BASE/'government-xl-sol-city-additional-tower-joins-v2-20261021'
PRIOR=BASE/'government-xl-sol-city-additional-tower-paths-v3-20261021'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in [CAP,CONTACT,JOIN,JOIN2,PRIOR]:
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(d,p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[d][k];used[k]=pins[d][k];refs.append(p);return read(p)
 summary=[]; sources={r['uid']:r for r in take(CAP,CAP/'selection.json.gz')['rows']}
 for mode in ['original']:
  for uid in ['landsd/268424:0']:
   key=uid.split('/')[1];arrays=[]
   for u in [uid,'landsd/273271:0']:
    row=sources[u];p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==row['candidate']['entry']['sha256'];refs.append(p);arrays.append(decode_original_world_triangles(p.read_bytes()))
   t,podium=arrays;inp={'podium':podium};prior=take(CONTACT,CONTACT/mode/(key+'.json.gz'));assert digest(t.tobytes())==prior['sourceWorldSHA256']and digest(podium.tobytes())==prior['podiumWorldSHA256'];targets=[x for x in prior['targets']if not x['positiveContacts']]
   contactproof=prior['proof']
   contacts=[c for c in contactproof['contacts']if c['sourcePrimitiveDimensionA']==2 and c['sourcePrimitiveDimensionB']==2 and c['dimension']>0];edges=defaultdict(list);adj=defaultdict(dict)
   for i,face in enumerate(t):
    for a,b in [(0,1),(1,2),(2,0)]:
     edge=tuple(sorted((tuple(face[a]),tuple(face[b]))))
     if edge[0]!=edge[1]:edges[edge].append(i)
   for edge,ids in edges.items():
    for a in ids:
     for b in ids:
      if a!=b:adj[a][b]=edge
   joins=take(JOIN,JOIN/(key+'-joins.json.gz'));assert joins['sourceWorldSHA256']==digest(t.tobytes())
   extra=take(JOIN2,JOIN2/(key+'-joins.json.gz'));assert extra['sourceWorldSHA256']==joins['sourceWorldSHA256']
   for component in joins['components']+extra['components']:
    for contact in component['outsidePositiveContacts']:
     assert contact['dimension']>0 and contact['sourcePrimitiveDimensionA']==contact['sourcePrimitiveDimensionB']==2
     points=[tuple(float(Fraction(v))for v in q)for q in contact['exactPoints']];low=min(points,key=lambda q:q[1]);a,b=contact['sourceFaceA'],contact['sourceFaceB']
     # Crossing at a verified point of a positive-dimensional finite face join;
     # each subsequent segment stays inside its original convex triangle.
     adj[a][b]=adj[b][a]=(low,low)
   residual=take(PRIOR,PRIOR/mode/(key+'.json.gz'));targets=[x for x in residual['rows']if not x['verifiedPath']];out=[]
   for target in targets:
    start=np.asarray(target['witness']['position']);cost={i:float(start[1])for i in target['incidentFaces']};previous={i:None for i in cost};queue=[(v,i)for i,v in cost.items()];heapq.heapify(queue)
    while queue:
     value,a=heapq.heappop(queue)
     if value!=cost[a]:continue
     for b,edge in adj[a].items():
      needed=max(value,min(q[1]for q in edge))
      if needed<cost.get(b,float('inf')):cost[b]=needed;previous[b]=a;heapq.heappush(queue,(needed,b))
    options=[]
    for contact in contacts:
     terminal=contact['sourceFaceA']
     if terminal not in cost:continue
     endpoints=np.array([[float(Fraction(v))for v in q]for q in contact['exactPoints']]);endpointY=float(max(endpoints[:,1]));ceiling=max(float(start[1]),endpointY);ids=[];at=terminal
     while at is not None:ids.append(at);at=previous[at]
     ids.reverse();options.append(dict(minimumGatewayHeightM=cost[terminal],highestContactEndpointM=endpointY,ownEndpointCeilingM=ceiling,excessAboveOwnEndpointM=max(0,cost[terminal]-ceiling),faces=ids,contact=contact))
    best=min(options,key=lambda x:x['excessAboveOwnEndpointM'])if options else None
    out.append(dict(witness=target['witness'],incidentFaces=target['incidentFaces'],reachableContactCount=len(options),bestRoute=best))
   save(DOC/(key+'.json.gz'),dict(uid=uid,sourceWorldSHA256=digest(t.tobytes()),rows=out,installationApproved=False));item=dict(uid=uid,residual=len(out),connected=sum(x['bestRoute']is not None for x in out),excessHeightsM=sorted({x['bestRoute']['excessAboveOwnEndpointM']for x in out if x['bestRoute']}));summary.append(item);print(item,flush=True)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 refs.append(HERE/'pool_incident_wall_contacts_v1_20261017.py');result=dict(uids=['landsd/268424:0'],rows=summary,installationApproved=False,qualification='Continuous finite source-face paths to positive finite contacts, bounded by their own endpoint heights. Preserves strict raw warnings; does not infer structural roles or approve publication.');save(DOC/'summary.json',result)
 module('yoho_remaining_paths_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'minimum-required-source-route-height-diagnostic',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
