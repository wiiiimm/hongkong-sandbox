"""Bounded exact shared-edge context for eleven local source contact exceptions."""
from pathlib import Path
from collections import defaultdict,deque
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-mall-i-contact-adjacency-v1-20261020';DOC=BASE/BATCH;CONTACT=BASE/'government-xl-yoho-mall-i-render-ground-contacts-v1-20261020';CAP=BASE/'government-xl-yoho-mall-i-render-foundations-v1-20261020'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};consumed={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [CONTACT,CAP]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(folder,p):
  key=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[folder][key];refs.append(p);consumed[key]=pins[folder][key];return read(p)
 capture=take(CAP,CAP/'attributes.json.gz')['rows'][0];summary=[]
 for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:
  tri=np.asarray(capture[field],dtype='float64').reshape(-1,3)[np.asarray(capture['completeOriginalIndex']).reshape(-1,3)];targets=take(CONTACT,CONTACT/(mode+'-targets.json.gz'))['rows'];unresolved=[r for r in targets if not r['positiveDimensionalContact']];assert len(unresolved)==11
  proven={c['sourceFaceA']:c for r in targets for c in r['contactRows']};edges=defaultdict(list)
  for i,t in enumerate(tri):
   for a,b in [(0,1),(1,2),(2,0)]:
    key=tuple(sorted((tuple(t[a]),tuple(t[b]))))
    if key[0]!=key[1]:edges[key].append(i)
  adjacent=defaultdict(dict)
  for edge,faces in edges.items():
   for a in faces:
    for b in faces:
     if a!=b:adjacent[a][b]=edge
  rows=[]
  for target in unresolved:
   queue=deque((s,[s])for s in target['incidentFaces']);seen=set(target['incidentFaces']);found=None
   while queue:
    face,route=queue.popleft()
    if face in proven:
     found=dict(faces=route,sharedEdges=[[list(v)for v in adjacent[a][b]]for a,b in zip(route,route[1:])],positiveContact=proven[face],vertices=[tri[i].tolist()for i in route]);break
    if len(route)>=4:continue
    for nxt in adjacent[face]:
     if nxt not in seen:seen.add(nxt);queue.append((nxt,route+[nxt]))
   rows.append(dict(witness=target['rawWitness'],incidentFaces=target['incidentFaces'],boundedExactEdgePath=found))
  save(DOC/(mode+'.json.gz'),dict(rows=rows,worldSHA256=digest(tri.tobytes()),diagnosticOnly=True));summary.append(dict(mode=mode,witnesses=len(rows),withBoundedPath=sum(r['boundedExactEdgePath']is not None for r in rows)))
 for p,h in consumed.items():assert digest((ROOT/p).read_bytes())==h
 result=dict(uids=['landsd/189427:0'],rows=summary,installationApproved=False,qualification='At most three exact shared nonzero edges to an already measured finite terrain contact. Local authored continuity only; no structural or placement approval.')
 save(DOC/'summary.json',result);module('yoho_adjacency_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-source-contact-edge-context',list(dict.fromkeys(refs)),result);print(summary,flush=True)
if __name__=='__main__':main()
