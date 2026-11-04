"""Bounded exact original-pair evidence for reciprocal source identity overlap.

No identity/physical acceptance, source edits, terrain changes or publication.
"""
import sys,uuid,subprocess
from run import ROOT,HERE,read,save,reservations
from require_remaining_xl import require_remaining
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BATCH='government-xl-silvercord-lippo-original-pair-sequence-v1-20261101';BASE=ROOT/'docs/astra-city/government-import';LOCAL=HERE/'local'/BATCH
RUNTIME='government-xl-silvercord-lippo-current-checks-v1-20261101-runtime';ATTR='government-xl-silvercord-lippo-original-attributes-v1-20261101';CONTACT='government-xl-silvercord-lippo-original-contacts-v1-20261101';UIDS=['landsd/233997:0','landsd/231645:0']
def owned():
 lease=LOCAL/'reservation.json';rows={r['uid']:r for r in read(BASE/RUNTIME/'selection.json.gz')['rows']}
 for uid in UIDS:require_remaining(BASE/'government-xl-academic309823-after-kai-tak-carpark-original-installed-v1-20261101/full-xl-current-count.json',uid,rows[uid]['sourceSHA256'])
 steps=[('attributes','selected_original_render_attributes_v1.py',['--batch',ATTR,'--capture',RUNTIME]),('contacts','selected_original_pair_finite_contacts_v1_20261025.py',['--batch',CONTACT,'--runtime',RUNTIME,'--attributes',ATTR,'--left',UIDS[0],'--right',UIDS[1]]),('views','selected_original_pair_contact_views_v2_20261031.py',['--batch','government-xl-silvercord-lippo-original-contact-views-v1-20261101','--selection',RUNTIME,'--contacts',CONTACT,'--lease',str(lease)])]
 for name,tool,args in steps:
  assert reservations.owns(read(lease))
  with (LOCAL/(name+'.log')).open('w')as log:subprocess.run([sys.executable,str(HERE/tool),*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=10800)
  print(name+' complete',flush=True)
 save(LOCAL/'completed.json',dict(uids=UIDS,identityAccepted=False,physicalAcceptance=False,sourceGeometryChanges=0,installationApproved=False,publication=False))
if __name__=='__main__':
 if '--owned'in sys.argv:owned()
 else:
  assert not LOCAL.exists()
  c=reservations.claim('silvercord-lippo-exact-original-pair-'+str(uuid.uuid4()),['building:'+u for u in UIDS]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],c
  execute_reserved(c['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
