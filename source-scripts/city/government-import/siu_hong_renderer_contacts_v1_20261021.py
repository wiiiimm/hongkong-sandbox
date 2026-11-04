"""Exact finite original tower/podium contacts at all current flagged witnesses."""
from pathlib import Path
import json,sys,uuid,subprocess
import numpy as np
from collections import defaultdict,deque
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-siu-hong-renderer-contacts-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;ASSEMBLY=BASE/'government-xl-siu-hong-four-mode-foundations-v1-20261021';REC=BASE/'government-xl-grandiose-companion-recovery-v2-20261021';CAP=BASE/'government-xl-siu-hong-companion-sources-v1-20261021'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in [ASSEMBLY,CAP]:
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(d,p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[d][k];refs.append(p);used[k]=pins[d][k];return read(p)
 summary=[]; selection=take(CAP,CAP/'nominations.json')['rows']; rows=[dict(uid=n['uid'],sourceSHA256=n['model']['asset']['sha256']) for n in selection]
 for mode in ['literal','leftF32','balancedF32']:
  for r in rows:
   folder=ASSEMBLY/mode/r['uid'].split('/')[1]
   support=take(ASSEMBLY,folder/'support.json.gz'); failures=support['rows'][0]['proof']['unresolved']
   if not failures:continue
   inputs=take(ASSEMBLY,folder/'input.json.gz'); mesh=inputs['rows'][0]
   tri=np.asarray(mesh['position']).reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)]; podium=np.asarray(inputs['podium']).reshape(-1,3,3)
   lo,hi=tri.min(1),tri.max(1); targets=[]
   for witness in failures:
    point=np.asarray(witness['position']); broad=np.flatnonzero(np.all(lo<=point+.001,axis=1)&np.all(hi>=point-.001,axis=1))
    ids=[int(i)for i in broad if np.linalg.norm(np.cross(tri[i,1]-tri[i,0],tri[i,2]-tri[i,0]))>0 and np.linalg.norm(closest(point,tri[i])-point)<=.001]; assert ids
    targets.append(dict(witness=witness,incidentFaces=ids))
   incidentIds=sorted({i for t in targets for i in t['incidentFaces']});edges=defaultdict(list);adj=defaultdict(set)
   for i,face in enumerate(tri):
    for a,b in [(0,1),(1,2),(2,0)]:
     edge=tuple(sorted((tuple(face[a]),tuple(face[b]))))
     if edge[0]!=edge[1]:edges[edge].append(i)
   for ids in edges.values():
    for i in ids:adj[i].update(ids)
   reached=set(incidentIds);queue=deque(incidentIds)
   while queue:
    i=queue.popleft()
    for j in adj[i]-reached:reached.add(j);queue.append(j)
   ids=sorted(reached);print(dict(mode=mode,uid=r['uid'],wholeIncidentComponents=len(ids)),flush=True)
   proof=exact_finite_contacts(tri,ids,podium,list(range(len(podium))))
   for target in targets:
    target['positiveContacts']=[c for c in proof['contacts'] if c['sourceFaceA']in target['incidentFaces'] and c['sourcePrimitiveDimensionA']==2 and c['sourcePrimitiveDimensionB']==2 and c['dimension']>0]
   save(DOC/mode/(r['uid'].split('/')[1]+'.json.gz'),dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],sourceWorldSHA256=digest(tri.tobytes()),podiumWorldSHA256=digest(podium.tobytes()),targets=targets,proof=proof,installationApproved=False))
   item=dict(mode=mode,uid=r['uid'],witnesses=len(targets),finiteIncidentContacts=sum(bool(t['positiveContacts']) for t in targets)); summary.append(item); print(item,flush=True); assert reservations.owns(lease)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_finite_triangle_contacts_20261010.py','pool_incident_wall_contacts_v1_20261017.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py'])
 result=dict(uids=[r['uid']for r in rows],rows=summary,installationApproved=False,sourceGeometryChanges=0);save(DOC/'summary.json',result);module('yoho_tower_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-tower-podium-finite-contacts',list(dict.fromkeys(refs)),result)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
