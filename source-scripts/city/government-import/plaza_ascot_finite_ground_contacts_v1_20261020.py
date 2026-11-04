"""Exact original tower/podium intersections at flagged incident faces, no approval."""
from pathlib import Path
import json,subprocess,sys,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-finite-ground-contacts-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-plaza-ascot-candidate-ground-v2-20261020';SUP=BASE/'government-xl-plaza-ascot-ground-contacts-v1-20261020';OLD=BASE/'government-xl-victoria-mall-complete-source-lower-joins-context-v1-20261012';POD='landsd/289787:0'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,SUP]:
   receipt=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);refs.append(folder/'result.json');pins[folder.name]={e['path']:e['sha256']for e in receipt['evidenceRefs']}
 def consume(folder,name):
  p=folder/name;assert digest(p.read_bytes())==pins[folder.name][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 capture_path=HERE/'local'/CAP.name/'runtime-geometry.json.gz';assert digest(capture_path.read_bytes())==pins[CAP.name][str(capture_path.relative_to(ROOT))];refs.append(capture_path);capture=read(capture_path);summary=[]
 modes=[('literal','position')]
 for mode,field in modes:
  assert reservations.owns(lease)
  if field:
   world={r['uid']:np.asarray(r[field],dtype='<f8').reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]for r in capture['rows']}
   failures=[dict(uid=r['uid'],witness=f)for r in consume(SUP,'support.json.gz')['rows']for f in r['proof']['unresolved']]
  out=[];support=np.asarray(capture['rows'][0]['drawnGroundGeometry']).reshape(-1,3,3)
  for uid in sorted({r['uid']for r in failures}):
   t=world[uid];lo,hi=t.min(1),t.max(1);targets=[]
   for r in failures:
    if r['uid']!=uid:continue
    point=np.asarray(r['witness']['position']);broad=np.flatnonzero(np.all(lo<=point+.001,axis=1)&np.all(hi>=point-.001,axis=1))
    ids=[int(i)for i in broad if np.linalg.norm(np.cross(t[i,1]-t[i,0],t[i,2]-t[i,0]))>0 and np.linalg.norm(closest(point,t[i])-point)<=.001]
    assert ids;targets.append(dict(rawWitness=r['witness'],incidentFaces=ids))
   ids=sorted({f for target in targets for f in target['incidentFaces']});proof=exact_finite_contacts(t,ids,support,list(range(len(support))))
   for target in targets:
    contacts=[c for c in proof['contacts']if c['sourceFaceA']in target['incidentFaces'] and c['sourcePrimitiveDimensionA']==2 and c['sourcePrimitiveDimensionB']==2 and c['dimension']>0]
    out.append(dict(uid=uid,**target,positiveDimensionalContact=bool(contacts),contactRows=contacts))
   save(DOC/(mode+'-'+uid.split('/')[1]+'.json.gz'),dict(sourceWorldSHA256=digest(t.tobytes()),supportWorldSHA256=digest(support.tobytes()),sourceFaceIds=ids,proof=proof,installationApproved=False))
  save(DOC/(mode+'-targets.json.gz'),dict(rows=out,installationApproved=False));row=dict(mode=mode,targets=len(out),targetsWithFiniteIncidentContact=sum(r['positiveDimensionalContact']for r in out));summary.append(row);print(row,flush=True)
 for p in refs:
  for mapping in pins.values():
   key=str(p.relative_to(ROOT))
   if key in mapping:assert digest(p.read_bytes())==mapping[key]
 refs.extend(HERE/n for n in ['pool_incident_wall_contacts_v1_20261017.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py'])
 save(DOC/'summary.json',dict(rows=summary,installationApproved=False,qualification='Exact finite intersections of unchanged original incident faces. This is contact evidence, not a change to strict support policy or an installation decision.',geometryChanges=0))
 module('mount_sterling_render_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-literal-render-ground-finite-contacts',list(dict.fromkeys(refs)),dict(uids=[r['uid'] for r in capture['rows']],rows=summary,installationApproved=False))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists() and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
