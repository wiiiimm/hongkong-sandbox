"""Run bounded source-only cross-sheet contact diagnostics; never publish/approve.

Each child owns canonical building leases and freezes its own exact evidence.
Unavailable leases, unmatched identities and missing local files stay unresolved.
"""
import json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-cross-sheet-cached-contacts-controller-v1-20261028';INVENTORY='government-xl-unfinished-territorial-neighbour-inventory-v1-20261028'
def main():
 out=BASE/BATCH;assert not out.exists();authenticate(BASE/INVENTORY);inventory=read(BASE/INVENTORY/'summary.json');out.mkdir();completed=[];unresolved=[];refs=[Path(__file__),HERE/'fixed_xl_cached_neighbour_contacts_v1_20261028.py',BASE/INVENTORY/'result.json'];scope=[r for r in inventory['rows']if any(c['sheet']!=r['sheet']for c in r['nearbyOriginalCandidates'])]
 for row in scope:
  uid=row['uid'];peers=row['nearbyOriginalCandidates']
  if not uid or any(not p['uid']for p in peers):unresolved.append(dict(sourceKey=row['sourceKey'],uid=uid,reason='unmatched-source-identity-requires-canonical-resource-resolution'));continue
  if uid in ['landsd/182397:0','landsd/30031:0','landsd/59289:0']:unresolved.append(dict(sourceKey=row['sourceKey'],uid=uid,reason='active-installation-or-completed-separate-contact-evidence'));continue
  child='government-xl-cross-sheet-'+uid.split('/')[1].replace(':','-')+'-original-contacts-v1-20261028';doc=BASE/child
  if doc.exists():unresolved.append(dict(sourceKey=row['sourceKey'],uid=uid,reason='existing-attempt-preserved-no-overwrite'));continue
  keys=sorted({'building:'+u for u in[uid,*[p['uid']for p in peers]]});claim=reservations.claim('cross-sheet-original-contacts-'+str(uuid.uuid4()),keys,batch=child,ttl=1800)
  if not claim['ok']:unresolved.append(dict(sourceKey=row['sourceKey'],uid=uid,reason='canonical-resource-busy-no-takeover'));continue
  lease=HERE/'local'/child/'reservation.json';log=out/(uid.split('/')[1].replace(':','-')+'.log')
  try:
   # execute_reserved handles renewal and releases only this child's lease.
   with log.open('w') as stream:
    receipt=claim['reservation'];save(lease,json.loads(json.dumps(receipt,default=str)))
    try:
     proc=subprocess.run([sys.executable,str(HERE/'observed_reserved_runner_v1_20261027.py'),str(lease),sys.executable,str(HERE/'fixed_xl_cached_neighbour_contacts_v1_20261028.py'),'--batch',child,'--uid',uid,'--lease',str(lease)],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
    finally:
     if reservations.owns(receipt):assert reservations.release(receipt)['ok']
   if proc.returncode:unresolved.append(dict(sourceKey=row['sourceKey'],uid=uid,reason='diagnostic-error-preserved',log=str(log.relative_to(ROOT))));continue
   result,_=authenticate(doc);completed.append(dict(uid=uid,sourceKey=row['sourceKey'],receipt=str((doc/'result.json').relative_to(ROOT)),allNominatedOriginalsTested=result['allNominatedOriginalsTested'],missingCachedSources=len(result['missingCachedSources']),contacts=[dict(uid=r['peer']['uid'],count=r['finiteContacts'])for r in result['rows']]));refs.append(doc/'result.json')
  except Exception as error:
   unresolved.append(dict(sourceKey=row['sourceKey'],uid=uid,reason='controller-error-preserved',errorType=type(error).__name__))
  finally:
   save(out/'progress.json',dict(scope=len(scope),completed=completed,unresolved=unresolved,installationApproved=False));print(dict(uid=uid,completed=len(completed),unresolved=len(unresolved)),flush=True)
 result=dict(uids=sorted(r['uid']for r in scope if r['uid']),fixedXLTotal=521,unfinishedInventoryScope=126,crossSheetTargets=len(scope),completed=completed,unresolved=unresolved,qualification='Diagnostic coverage only, no installed/skip/permanent-rejection credit. Busy leases are not taken over. Missing files, unknown bounds, unmatched source identities and all current-scene/physical gates remain unresolved. No production jobs queued; every completed child has separate fenced immutable Neon evidence.')
 save(out/'summary.json',result);module('cross_sheet_controller_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'cross-sheet-cached-original-contact-diagnostic-coverage',refs,result)
if __name__=='__main__':main()
