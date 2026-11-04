"""Finite source-face paths bounded by their own contact endpoint heights."""
from pathlib import Path
from collections import defaultdict,deque
from fractions import Fraction
import heapq
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sol-city-original-facade-paths-v1-20261021';DOC=BASE/BATCH
CAP=BASE/'government-xl-sol-city-five-foundations-v1-20261021';CONTACT=BASE/'government-xl-sol-city-rendered-tower-contacts-v1-20261021';FULL=BASE/'government-xl-yoho-mall-i-tower8-render-context-v1-20261020'
JOIN=BASE/'government-xl-sol-city-rendered-joins-v1-20261021'
PRIOR=BASE/'government-xl-sol-city-rendered-tower-paths-v2-20261021'
ROLES={k:BASE/('government-xl-sol-city-tower'+n+'-facade-role-v1-20261021')for k,n in [('268424:0','5'),('273080:0','2')]}
DIRS={k:{'contact':BASE/('government-xl-sol-city-'+contact+'-20261021'),'prior':BASE/('government-xl-sol-city-'+prior+'-20261021'),'joins':[BASE/('government-xl-sol-city-'+join+'-v'+str(v)+'-20261021')for v in [1,2]]}for k,contact,prior,join in [('268424:0','additional-tower-contacts-v1','additional-tower-paths-v3','additional-tower-joins'),('273080:0','original-contacts-v1','original-paths-v3','component-joins')]}
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in list(dict.fromkeys([CAP,*ROLES.values()]+[d for r in DIRS.values()for d in [r['contact'],r['prior'],*r['joins']]])):
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(d,p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[d][k];used[k]=pins[d][k];refs.append(p);return read(p)
 summary=[]
 for mode in ['original']:
  for uid in ['landsd/268424:0','landsd/273080:0']:
   key=uid.split('/')[1];CONTACT=DIRS[key]['contact'];PRIOR=DIRS[key]['prior'];inp=take(CAP,CAP/mode/key/'input.json.gz');r=inp['rows'][0];t=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];prior=take(CONTACT,CONTACT/mode/(key+'.json.gz'));targets=[x for x in prior['targets']if not x['positiveContacts']]
   assert digest(t.tobytes())==prior['sourceWorldSHA256'];assert digest(np.asarray(inp['podium']).reshape(-1,3,3).tobytes())==prior['podiumWorldSHA256']
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
   for directory in DIRS[key]['joins']:
    joins=take(directory,directory/(key+'-joins.json.gz'));assert joins['sourceWorldSHA256']==digest(t.tobytes())
    for record in joins['components']:
     for contact in record['outsidePositiveContacts']:
      assert contact['dimension']>0 and contact['sourcePrimitiveDimensionA']==contact['sourcePrimitiveDimensionB']==2
      points=[tuple(float(Fraction(v))for v in q)for q in contact['exactPoints']];low=min(points,key=lambda q:q[1]);a,b=contact['sourceFaceA'],contact['sourceFaceB']
      adj[a][b]=adj[b][a]=(low,low)
   role=take(ROLES[key],ROLES[key]/'role-review.json');assert role['roleInterpretationAccepted'] and role['uid']==uid
   residual=take(PRIOR,PRIOR/mode/(key+'.json.gz'));assert residual['sourceWorldSHA256']==digest(t.tobytes())
   targets=[x for x in residual['rows']if not x['verifiedPath']];allowed=set(role['exactIncidentFaceIds']);out=[]
   for target in targets:
    start=np.asarray(target['witness']['position']);assert set(target['incidentFaces'])<=allowed
    assert any(np.linalg.norm(start-np.asarray(r['witness']['position']))<=.001 and set(target['incidentFaces'])&set(r['incidentFaces']) for r in role['witnesses'])
    cost={i:float(start[1]) for i in target['incidentFaces']};previous={i:None for i in cost};queue=[(v,i)for i,v in cost.items()];heapq.heapify(queue)
    while queue:
     value,a=heapq.heappop(queue)
     if value!=cost[a]:continue
     for b,edge in adj[a].items():
      needed=max(value,min(q[1]for q in edge))
      if needed<cost.get(b,float('inf')):cost[b]=needed;previous[b]=a;heapq.heappush(queue,(needed,b))
    candidates=[]
    for contact in contacts:
     terminal=contact['sourceFaceA']
     if terminal not in cost:continue
     endpoints=np.array([[float(Fraction(v))for v in q]for q in contact['exactPoints']]);end=max(endpoints,key=lambda p:p[1]);ids=[];at=terminal
     while at is not None:ids.append(at);at=previous[at]
     ids.reverse();points=[start]
     for a,b in zip(ids,ids[1:]):points.append(np.asarray(min(adj[a][b],key=lambda p:p[1])))
     points.append(end);errors=[float(np.linalg.norm(closest(q,t[f])-q))for i,f in enumerate(ids)for q in points[i:i+2]]
     if max(errors)>.001:continue
     endpointCeiling=max(float(start[1]),float(end[1]));maximumHeight=float(max(q[1]for q in points))
     candidates.append(dict(faces=ids,continuousPath=[q.tolist()for q in points],maximumResidualM=max(errors),endpointHeightCeilingM=endpointCeiling,maximumPathHeightM=maximumHeight,excessAboveOwnEndpointM=max(0,maximumHeight-endpointCeiling),contact=contact))
    found=min(candidates,key=lambda p:(p['excessAboveOwnEndpointM'],len(p['faces']))) if candidates else None
    out.append(dict(witness=target['witness'],incidentFaces=target['incidentFaces'],verifiedAttachmentPath=found,roleReview=str((ROLES[key]/'role-review.json').relative_to(ROOT)),rawBoundedPathFailureRetained=True))
   save(DOC/mode/(key+'.json.gz'),dict(uid=uid,sourceWorldSHA256=digest(t.tobytes()),supportWorldSHA256=digest(np.asarray(inp['podium']).reshape(-1,3,3).tobytes()),rows=out,installationApproved=False));item=dict(mode=mode,uid=uid,targets=len(out),finiteAttachedFacadePaths=sum(x['verifiedAttachmentPath']is not None for x in out));summary.append(item);print(item,flush=True)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 refs.append(HERE/'pool_incident_wall_contacts_v1_20261017.py');result=dict(uids=['landsd/268424:0','landsd/273080:0'],rows=summary,installationApproved=False,qualification='Exact continuous attachment paths for individually reviewed facade faces only. Raw strict and endpoint-bound failures retained. No generic threshold waiver, structural certification or publication approval.');save(DOC/'summary.json',result)
 module('yoho_remaining_paths_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'scoped-reviewed-facade-rendered-attachment-paths',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
