"""Exact finite original tower/podium contacts at the eighteen flagged witnesses."""
from pathlib import Path
import json,sys,uuid,subprocess
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-mall-i-tower-contacts-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;ASSEMBLY=BASE/'government-xl-yoho-mall-i-original-assembly-v1-20261020';REC=BASE/'government-xl-yoho-mall-i-tower-recovery-v1-20261020';CAP=BASE/'government-xl-yoho-mall-i-private-runtime-v3-20261020'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in [ASSEMBLY,REC,CAP]:
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(d,p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[d][k];refs.append(p);used[k]=pins[d][k];return read(p)
 rows=take(REC,REC/'recovery.json')['rows'];mall=take(CAP,CAP/'selection.json.gz')['rows'][0];ap=ROOT/mall['candidate']['path'];assert digest(ap.read_bytes())==mall['sourceSHA256'];refs.append(ap);podium=decode_original_world_triangles(ap.read_bytes())
 support=take(ASSEMBLY,ASSEMBLY/'189427:0/support.json.gz');summary=[]
 for r in rows:
  failures=next(x['proof']['unresolved']for x in support['rows']if x['uid']==r['uid'])
  if not failures:continue
  ap=ROOT/r['assetPath'];assert digest(ap.read_bytes())==r['sourceSHA256'];refs.append(ap);tri=decode_original_world_triangles(ap.read_bytes());lo,hi=tri.min(1),tri.max(1);targets=[]
  for witness in failures:
   point=np.asarray(witness['position']);broad=np.flatnonzero(np.all(lo<=point+.001,axis=1)&np.all(hi>=point-.001,axis=1));ids=[int(i)for i in broad if np.linalg.norm(np.cross(tri[i,1]-tri[i,0],tri[i,2]-tri[i,0]))>0 and np.linalg.norm(closest(point,tri[i])-point)<=.001];assert ids;targets.append(dict(witness=witness,incidentFaces=ids))
  ids=sorted({i for t in targets for i in t['incidentFaces']});proof=exact_finite_contacts(tri,ids,podium,list(range(len(podium))))
  for target in targets:
   contacts=[c for c in proof['contacts']if c['sourceFaceA']in target['incidentFaces']and c['sourcePrimitiveDimensionA']==2 and c['sourcePrimitiveDimensionB']==2 and c['dimension']>0];target['positiveContacts']=contacts
  save(DOC/(r['uid'].split('/')[1]+'.json.gz'),dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],sourceWorldSHA256=digest(tri.tobytes()),podiumWorldSHA256=digest(podium.tobytes()),targets=targets,proof=proof,installationApproved=False));item=dict(uid=r['uid'],witnesses=len(targets),finiteIncidentContacts=sum(bool(t['positiveContacts'])for t in targets));summary.append(item);print(item,flush=True);assert reservations.owns(lease)
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
