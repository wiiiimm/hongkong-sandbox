"""Private authentic-terrain recovery for two unfinished XL originals.

No live terrain writes, source edits, automatic approval or terminal decisions.
"""
import sys,uuid,subprocess
from run import ROOT,HERE,read,save,reservations
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
P='government-xl-peak-harbourfront-'
BATCH=P+'authentic-terrain-sequence-v1-20261101'
CAPTURE=P+'current-sequence-v1-20261101-runtime'
BASE=ROOT/'docs/astra-city/government-import';LOCAL=HERE/'local'/BATCH
UIDS=['landsd/167911:0','landsd/233227:0']
def owned():
 lease=LOCAL/'reservation.json';outcomes=[]
 for uid in UIDS:
  key=uid.split('/')[1].replace(':','-');batch=P+'authentic-terrain-'+key+'-v1-20261101'
  assert reservations.owns(read(lease))
  cmd=[sys.executable,str(HERE/'selected_original_local_full_tin_v22_20261101.py'),'--batch',batch,'--capture',CAPTURE,'--terrain-check','government-xl-all-200-original-terrain-batch-v2-20261022','--uid',uid]
  with (LOCAL/(key+'-terrain.log')).open('w')as log:
   result=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=10800)
  row=dict(uid=uid,batch=batch,exitCode=result.returncode,installationApproved=False)
  if result.returncode==0:
   receipt=read(BASE/batch/'result.json');row['jobId']=receipt['jobId'];summary=read(BASE/batch/'summary.json');row['terrainResult']=summary
  outcomes.append(row);save(LOCAL/'progress.json',dict(rows=outcomes,installationApproved=False,publication=False));print(dict(uid=uid,exitCode=result.returncode,jobId=row.get('jobId')),flush=True)
 save(LOCAL/'completed.json',dict(rows=outcomes,sourceGeometryChanges=0,publication=False,installationApproved=False))
if __name__=='__main__':
 if '--owned'in sys.argv:owned()
 else:
  assert not LOCAL.exists()and (BASE/CAPTURE/'result.json').exists()
  c=reservations.claim('peak-harbourfront-authentic-terrain-'+str(uuid.uuid4()),['building:'+u for u in UIDS]+['terrain:city/data/terrain.json','immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],c
  execute_reserved(c['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
