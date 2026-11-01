"""Complete original-source scope/diagrams for bounded identity review; no approval."""
import sys,uuid,subprocess
from run import ROOT,HERE,read,save,reservations
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BATCH='government-xl-silvercord-lippo-complete-scope-views-sequence-v1-20261101';LOCAL=HERE/'local'/BATCH
RUNTIME='government-xl-silvercord-lippo-current-checks-v1-20261101-runtime';ATTR='government-xl-silvercord-lippo-original-attributes-v1-20261101';SCOPE='government-xl-silvercord-lippo-complete-source-scope-v1-20261101';VIEWS='government-xl-silvercord-lippo-complete-source-views-v1-20261101';UIDS=['landsd/233997:0','landsd/231645:0']
def owned():
 lease=LOCAL/'reservation.json'
 steps=[('scope','selected_original_model_only_scope_v1_20261023.py',['--batch',SCOPE,'--runtime',RUNTIME,'--attributes',ATTR,'--inventory','government-xl-after-hkust-carpark-renderer-bound-inventory-v1-20261101']),('views','selected_original_scope_views_v2_20261031.py',['--batch',VIEWS,'--runtime',RUNTIME,'--scope',SCOPE])]
 for name,tool,args in steps:
  assert reservations.owns(read(lease))
  with (LOCAL/(name+'.log')).open('w')as log:subprocess.run([sys.executable,str(HERE/tool),*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=10800)
  print(name+' complete',flush=True)
 save(LOCAL/'completed.json',dict(uids=UIDS,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False))
if __name__=='__main__':
 if '--owned'in sys.argv:owned()
 else:
  assert not LOCAL.exists()
  c=reservations.claim('silvercord-lippo-complete-source-views-'+str(uuid.uuid4()),['building:'+u for u in UIDS]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],c
  execute_reserved(c['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
