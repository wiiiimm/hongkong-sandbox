"""Fresh provider facts and exact upward-negative-face diagrams; no modelling/approval."""
import sys,uuid,subprocess
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BATCH='government-xl-peak-original-grade-views-primary-sequence-v1-20261101';LOCAL=HERE/'local'/BATCH;BASE=ROOT/'docs/astra-city/government-import';RUNTIME='government-xl-peak-retained-unapproved-runtime-probe-v2-20261101';LOW='government-xl-peak-original-physical-context-low-faces-v1-20261101';UID='landsd/167911:0'
def owned():
 lease=LOCAL/'reservation.json';_,pins=authenticate(BASE/LOW);path=BASE/LOW/'original.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];data=read(path);ids=[]
 for row in data['rows']:
  t=np.asarray(row['vertices']);n=np.cross(t[1]-t[0],t[2]-t[0]);length=float(np.linalg.norm(n))
  if length and n[1]>.25*length:ids.append(row['sourceFace'])
 assert ids and len(ids)==len(set(ids));save(LOCAL/'nominated-upward-faces.json',dict(uid=UID,sourceFaceIds=ids,roleAccepted=False,qualification='Signed upward normal among exact negative source/ground contexts; not an outdoor-floor or basement label.'))
 commands=[('primary','selected_original_primary_records_v1_20261025.py',['--batch','government-xl-peak-fresh-primary-records-v1-20261101','--capture',RUNTIME]),('views','selected_original_face_region_views_v1_20261024.py',['--batch','government-xl-peak-upward-negative-grade-views-v1-20261101','--runtime',RUNTIME,'--uid',UID,'--faces',*[str(i)for i in ids]])]
 for label,tool,args in commands:
  assert reservations.owns(read(lease))
  with(LOCAL/(label+'.log')).open('w')as log:subprocess.run([sys.executable,str(HERE/tool),*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=10800)
  print(label+' complete',flush=True)
 save(LOCAL/'completed.json',dict(uids=[UID],upwardNegativeFaces=len(ids),sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,publication=False))
if __name__=='__main__':
 if '--owned'in sys.argv:owned()
 else:
  assert not LOCAL.exists();c=reservations.claim('peak-original-grade-primary-views-'+str(uuid.uuid4()),['building:'+UID,'building:landsd/248218:0','terrain:city/data/terrain.json','terrain:city/data/support-exact-tin-248218-0.json','immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],c
  execute_reserved(c['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
