"""Resume two unfinished fixed XL originals with current-scene scripted checks.

Cached original bytes and poses stay immutable. No publication or approval transfer.
"""
import sys, uuid, subprocess
from pathlib import Path
from run import ROOT,HERE,read,digest,reservations,save
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BATCH='government-xl-peak-harbourfront-current-sequence-v1-20261101'
UIDS=['landsd/167911:0','landsd/233227:0']
CAPTURE='government-xl-remaining-178-v3-current-scene-v1-20261023-chunk-01-selection'
BASE=ROOT/'docs/astra-city/government-import'
LOCAL=HERE/'local'/BATCH
COUNT=BASE/'government-xl-academic309823-after-kai-tak-carpark-original-installed-v1-20261101/full-xl-current-count.json'
def owned():
 lease=LOCAL/'reservation.json';count=read(COUNT)
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==count['manifestSHA256']
 assert len(count['rows'])==len({r['sourceKey'] for r in count['rows']})==521
 for uid in UIDS:
  rows=[r for r in count['rows']if r['uid']==uid]
  assert len(rows)==1 and not rows[0]['installedVerified'] and rows[0]['runtimeSourceSHA256']is None
 commands=[('selection','selected_original_refresh_selection_v1.py',['--capture',CAPTURE,*[v for u in UIDS for v in ['--uid',u]]]),('runtime','selected_original_current_capture_v3.py',['--capture',BATCH+'-selection',*[v for u in UIDS for v in ['--uid',u]]]),('identity','selected_original_identity_v3.py',['--capture',BATCH+'-runtime'])]
 jobs=[]
 for step,tool,args in commands:
  assert reservations.owns(read(lease))
  with (LOCAL/(step+'.log')).open('w')as log:
   subprocess.run([sys.executable,str(HERE/tool),'--batch',BATCH+'-'+step,*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=10800)
  result=read(BASE/(BATCH+'-'+step)/'result.json');jobs.append({'phase':step,'jobId':result['jobId'],'batch':BATCH+'-'+step});print(step+' complete',flush=True)
 save(LOCAL/'completed.json',dict(uids=UIDS,jobs=jobs,installationApproved=False,publication=False,sourceGeometryChanges=0))
if __name__=='__main__':
 if '--owned'in sys.argv:owned()
 else:
  assert not LOCAL.exists()
  c=reservations.claim('peak-harbourfront-original-'+str(uuid.uuid4()),['building:'+u for u in UIDS]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],c
  execute_reserved(c['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
