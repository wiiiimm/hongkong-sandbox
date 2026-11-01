"""Rebind prior failed construction domains to all current retained terrain obligations."""
import sys,uuid,subprocess
from run import ROOT,HERE,read,save,reservations
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BATCH='government-xl-silvercord-lippo-retention-preflight-sequence-v1-20261101';LOCAL=HERE/'local'/BATCH;UIDS=['landsd/233997:0','landsd/231645:0'];CAPTURE='government-xl-silvercord-lippo-current-checks-v1-20261101-runtime'
def owned():
 lease=LOCAL/'reservation.json';outcomes=[]
 for uid in UIDS:
  assert reservations.owns(read(lease));key=uid.split('/')[1].replace(':','-');batch='government-xl-silvercord-lippo-retention-'+key+'-v1-20261101';prior='government-xl-twelve-bounded-terrain-repairs-v1-20261022-'+key+'-terrain'
  with (LOCAL/(key+'.log')).open('w')as log:r=subprocess.run([sys.executable,str(HERE/'selected_original_retention_preflight_v2_20261023.py'),'--batch',batch,'--patch',prior,'--capture',CAPTURE],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=3600)
  outcomes.append(dict(uid=uid,batch=batch,exitCode=r.returncode));save(LOCAL/'progress.json',dict(rows=outcomes,installationApproved=False,publication=False));print(outcomes[-1],flush=True)
 save(LOCAL/'completed.json',dict(rows=outcomes,installationApproved=False,publication=False))
if __name__=='__main__':
 if '--owned'in sys.argv:owned()
 else:
  assert not LOCAL.exists();c=reservations.claim('silvercord-lippo-retention-preflight-'+str(uuid.uuid4()),['building:'+u for u in UIDS]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],c
  execute_reserved(c['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
