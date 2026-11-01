"""Validate source-ground and full affected scope after exact private terrain recovery."""
import sys,uuid,subprocess
from run import ROOT,HERE,read,save,reservations
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
P='government-xl-peak-harbourfront-';BATCH=P+'post-budget-sequence-v1-20261101'
BASE=ROOT/'docs/astra-city/government-import';LOCAL=HERE/'local'/BATCH
UIDS=['landsd/167911:0','landsd/233227:0'];CAPTURE=P+'current-sequence-v1-20261101-runtime'
INVENTORY='government-xl-after-hkust-carpark-renderer-bound-inventory-v1-20261101'
def owned():
 lease=LOCAL/'reservation.json';outcomes=[]
 def run(label,tool,args):
  assert reservations.owns(read(lease))
  with (LOCAL/(label+'.log')).open('w')as log:
   r=subprocess.run([sys.executable,str(HERE/tool),*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=10800)
  print(label+' exit '+str(r.returncode),flush=True);return r.returncode==0
 harbour='government-xl-harbourfront-exact-colour-terrain-candidate-v1-20261101'
 good=run('harbour-budget','selected_exact_colour_terrain_budget_recovery_v1_20261101.py',['--batch',harbour,'--prior',P+'authentic-terrain-233227-0-v1-20261101','--lease-file',str(lease)])
 for uid,patch in [(UIDS[0],'government-xl-peak-exact-colour-terrain-candidate-v1-20261101'),(UIDS[1],harbour if good else None)]:
  key=uid.split('/')[1].replace(':','-');row=dict(uid=uid,patch=patch,installationApproved=False)
  if patch is None:row['status']='exact-budget-investigation';outcomes.append(row);continue
  scope=P+'post-budget-scope-'+key+'-v1-20261101';runtime=P+'post-budget-runtime-'+key+'-v1-20261101'
  if not run(key+'-scope','selected_original_retained_patch_scope_v3_20261026.py',['--batch',scope,'--inventory',INVENTORY,'--patch',patch]):row['status']='scope-script-investigation';outcomes.append(row);continue
  row['scope']=scope;s=read(BASE/scope/'scope.json');r=read(BASE/patch/'result.json');args=['--batch',runtime,'--patch',patch,'--capture',CAPTURE]
  if not r.get('replacedNativeTerrain'):
   if s['terrainContacts']or s['positiveAreaTerrainOverlaps']:
    row['status']='explicit-retained-terrain-obligations-required';outcomes.append(row);continue
   args+=['--new-root-scope',scope]
  row['runtime']=runtime;row['status']='source-ground-captured'if run(key+'-runtime','selected_original_patch_runtime_full_basic_ground_v2_20261101.py',args)else'runtime-script-investigation'
  outcomes.append(row);save(LOCAL/'progress.json',dict(rows=outcomes,publication=False,installationApproved=False))
 save(LOCAL/'completed.json',dict(rows=outcomes,sourceGeometryChanges=0,publication=False,installationApproved=False))
if __name__=='__main__':
 if '--owned'in sys.argv:owned()
 else:
  assert not LOCAL.exists()
  c=reservations.claim('peak-harbourfront-post-budget-'+str(uuid.uuid4()),['building:'+u for u in UIDS]+['terrain:city/data/terrain.json','immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],c
  execute_reserved(c['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
