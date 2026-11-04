"""Exact source-only roof corner contact evidence; no placement/publication approval."""
from pathlib import Path
import json,sys,subprocess,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-langham-current-finite-contacts-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SUP=BASE/'government-xl-langham-place-installed-support-v3-20261021'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();receipt=read(SUP/'result.json');refs=[Path(__file__),SUP/'result.json'];pins={e['path']:e['sha256']for e in receipt['evidenceRefs']}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 sources=take(SUP/'closure/support-inputs.json')['sources'];check=take(SUP/'summary.json')['interface'];assert len(check['unresolved'])==4;meshes={}
 census=ROOT/'docs/astra-city/government-import/government-xl-manhattan-original-installed-v1-20261021/full-xl-current-count.json';assert any(r.get('uid')=='landsd/79318:0' and not r['installedVerified'] for r in read(census)['rows']);refs.append(census)
 for r in sources:
  p=ROOT/r['candidate']['path'];raw=p.read_bytes();assert digest(raw)==r['sourceSHA256'];refs.append(p);tri=np.asarray(decode_original_world_triangles(raw),dtype='<f8');assert len(tri)==r.get('triangles',r['candidate']['entry']['triangles']);meshes[r['uid']]=tri
 tri=meshes['landsd/79318:0'];pod=meshes['landsd/224399:0'];accounts=[]
 for j,w in enumerate(check['unresolved']):
  point=np.asarray(w['position']);lo,hi=tri.min(1),tri.max(1);broad=np.flatnonzero(np.all(lo<=point+.001,axis=1)&np.all(hi>=point-.001,axis=1));incident=[int(i)for i in broad if np.linalg.norm(np.cross(tri[i,1]-tri[i,0],tri[i,2]-tri[i,0]))>0 and np.linalg.norm(closest(point,tri[i])-point)<=.001];assert incident
  proof=exact_finite_contacts(tri,incident,pod,list(range(len(pod))));positive=[c for c in proof['contacts']if c['sourcePrimitiveDimensionA']==2 and c['sourcePrimitiveDimensionB']==2 and c['dimension']>0]
  save(DOC/f'finite-contacts-{j}.json.gz',dict(sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in sources},towerWorldSHA256=digest(tri.tobytes()),podiumWorldSHA256=digest(pod.tobytes()),witness=w,incidentFaces=incident,positiveContacts=positive,proof=proof,installationApproved=False));accounts.append(dict(witness=w,incidentFaces=incident,positiveFiniteContactPairs=len(positive)))
 result=dict(uids=[r['uid']for r in sources],sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in sources},rows=accounts,rawStrictSupportFailures=4,installationApproved=False,sourceGeometryChanges=0,qualification='Source-only finite incident contacts. Raw strict failures retained; not placement acceptance.')
 save(DOC/'summary.json',result);assert reservations.owns(lease);refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_finite_triangle_contacts_20261010.py','pool_incident_wall_contacts_v1_20261017.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py'])
 module('grandiose_finite_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-roof-corner-finite-contact-evidence',list(dict.fromkeys(refs)),result);print(result,flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
