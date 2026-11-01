"""Complete original-source physical diagnostics on the unadmitted private scene.

All outputs remain diagnostic: constructor admission, identity, neighbours and
publication are neither bypassed nor inferred from a completed computation.
"""
import sys,uuid,subprocess
from run import ROOT,HERE,read,save,reservations
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
P='government-xl-peak-original-physical-context-';BATCH=P+'sequence-v1-20261101';LOCAL=HERE/'local'/BATCH
RUNTIME='government-xl-peak-retained-unapproved-runtime-probe-v2-20261101';ATTR=P+'attributes-v1-20261101';UID='landsd/167911:0'
def owned():
 lease=LOCAL/'reservation.json'
 steps=[('attributes','selected_original_render_attributes_v1.py',['--batch',ATTR,'--capture',RUNTIME]),('foundations','original_four_world_foundation_context_v1_20261025.py',['--batch',P+'foundations-v1-20261101','--runtime',RUNTIME,'--attributes',ATTR,'--uid',UID]),('low-faces','selected_original_four_world_low_face_context_v3_20261031.py',['--batch',P+'low-faces-v1-20261101','--runtime',RUNTIME,'--attributes',ATTR,'--uid',UID])]
 for name,tool,args in steps:
  assert reservations.owns(read(lease))
  with (LOCAL/(name+'.log')).open('w')as log:subprocess.run([sys.executable,str(HERE/tool),*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=10800)
  print(name+' complete',flush=True)
 save(LOCAL/'completed.json',dict(uids=[UID],constructorAdmitted=False,physicalAcceptance=False,identityAccepted=False,installationApproved=False,publication=False,sourceGeometryChanges=0))
if __name__=='__main__':
 if '--owned'in sys.argv:owned()
 else:
  assert not LOCAL.exists()
  c=reservations.claim('peak-complete-source-physical-context-'+str(uuid.uuid4()),['building:'+UID,'building:landsd/248218:0','terrain:city/data/terrain.json','terrain:city/data/support-exact-tin-248218-0.json','immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],c
  execute_reserved(c['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
