"""Finite source-face paths bounded by their own contact endpoint heights."""
from pathlib import Path
from collections import defaultdict,deque
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-siu-hong-remaining-paths-v1-20261021';DOC=BASE/BATCH
CAP=BASE/'government-xl-siu-hong-original-assembly-v1-20261021';CONTACT=BASE/'government-xl-siu-hong-assembly-contacts-v1-20261021';FULL=BASE/'government-xl-yoho-mall-i-tower8-render-context-v1-20261020'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in [CAP,CONTACT]:
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(d,p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[d][k];used[k]=pins[d][k];refs.append(p);return read(p)
 summary=[]
 for mode in ['original']:
  for uid in ['landsd/190963:0']:
   key=uid.split('/')[1];inp=take(CAP,CAP/key/'input.json.gz');r=inp['rows'][0];t=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];prior=take(CONTACT,CONTACT/mode/(key+'.json.gz'));targets=[x for x in prior['targets']if not x['positiveContacts']]
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
   out=[]
   for target in targets:
    start=np.asarray(target['witness']['position']);found=None
    for contact in sorted(contacts,key=lambda c:-c['maximumSpanM']):
     endpoints=np.array([[float(Fraction(v))for v in q]for q in contact['exactPoints']]);end=endpoints.mean(0);ceiling=max(start[1],end[1]);terminal=contact['sourceFaceA'];queue=deque(target['incidentFaces']);previous={i:None for i in queue}
     while queue and terminal not in previous:
      a=queue.popleft()
      for b,edge in adj[a].items():
       if b not in previous and min(q[1]for q in edge)<=ceiling:previous[b]=a;queue.append(b)
     if terminal not in previous:continue
     ids=[];at=terminal
     while at is not None:ids.append(at);at=previous[at]
     ids.reverse();points=[start]
     for a,b in zip(ids,ids[1:]):
      x,y=map(np.asarray,adj[a][b]);assert min(x[1],y[1])<=ceiling
      if max(x[1],y[1])>ceiling:
       cut=x+(y-x)*((ceiling-x[1])/(y[1]-x[1]))
       if x[1]>ceiling:x=cut
       else:y=cut
      points.append((x+y)/2)
     points.append(end);errors=[float(np.linalg.norm(closest(q,t[f])-q))for i,f in enumerate(ids)for q in points[i:i+2]]
     if max(errors)>.001:continue
     found=dict(faces=ids,continuousPath=[q.tolist()for q in points],maximumResidualM=max(errors),endpointHeightCeilingM=float(ceiling),maximumPathHeightM=float(max(q[1]for q in points)),withinEndpointHeight=bool(max(q[1]for q in points)<=ceiling+1e-9),contact=contact)
     break
    out.append(dict(witness=target['witness'],incidentFaces=target['incidentFaces'],verifiedPath=found))
   save(DOC/mode/(key+'.json.gz'),dict(uid=uid,sourceWorldSHA256=digest(t.tobytes()),supportWorldSHA256=digest(np.asarray(inp['podium']).reshape(-1,3,3).tobytes()),rows=out,installationApproved=False));item=dict(mode=mode,uid=uid,targets=len(out),finiteBoundedPaths=sum(x['verifiedPath']is not None for x in out));summary.append(item);print(item,flush=True)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 refs.append(HERE/'pool_incident_wall_contacts_v1_20261017.py');result=dict(uids=['landsd/190963:0'],rows=summary,installationApproved=False,qualification='Continuous finite source-face paths to positive finite contacts, bounded by their own endpoint heights. Preserves strict raw warnings; does not infer structural roles or approve publication.');save(DOC/'summary.json',result)
 module('yoho_remaining_paths_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'finite-own-endpoint-height-original-path-context',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
