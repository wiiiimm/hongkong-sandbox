"""Finish exact-neighbour diagnostics after bounded original recovery.

No geometry edit, installation decision or reuse of source/placement approval.
"""
import json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from fixed_xl_cached_neighbour_contacts_v2_20261028 import required_resources
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-six-neighbour-two-case-contact-followthrough-v1-20261028';INVENTORY='government-xl-unfinished-territorial-neighbour-inventory-v1-20261028';RECOVERIES=['government-xl-six-neighbours-two-cases-recovery-v1-20261028','government-xl-revised-sheet-91790-exact-asset-recovery-v1-20261028'];TARGETS={'landsd/'+str(n)+':0'for n in[311761,264206]}
def main():
 out=BASE/BATCH;assert not out.exists();authenticate(BASE/INVENTORY);inventory=read(BASE/INVENTORY/'summary.json');refs=[Path(__file__),HERE/'fixed_xl_cached_neighbour_contacts_v2_20261028.py',BASE/INVENTORY/'result.json'];assets={}
 for batch in RECOVERIES:
  receipt,pins=authenticate(BASE/batch);assert receipt['recoveredCount']==(5 if batch==RECOVERIES[0]else 1);refs.append(BASE/batch/'result.json')
  for r in receipt['recovered']:
   path=ROOT/r['sourceAsset']['path'];assert __import__('hashlib').sha256(path.read_bytes()).hexdigest()==r['sourceSHA256'];assets[r['uid']]=r['sourceSHA256'];refs.append(path)
 assert len(assets)==6;rows=[r for r in inventory['rows']if r['uid']in TARGETS];assert len(rows)==2;out.mkdir();completed=[];unresolved=[]
 for row in rows:
  uid=row['uid'];child='government-xl-six-two-case-recovery-'+uid.split('/')[1].replace(':','-')+'-contacts-v1-20261028';doc=BASE/child;assert not doc.exists();claim=reservations.claim('six-two-case-recovery-source-contacts-'+str(uuid.uuid4()),sorted(required_resources(row)),batch=child,ttl=1800)
  if not claim['ok']:unresolved.append(dict(uid=uid,reason='canonical-resource-busy-no-takeover'));continue
  receipt=claim['reservation'];lease=HERE/'local'/child/'reservation.json';log=out/(uid.split('/')[1].replace(':','-')+'.log')
  try:
   with log.open('w')as stream:
    save(lease,json.loads(json.dumps(receipt,default=str)));proc=subprocess.run([sys.executable,str(HERE/'observed_reserved_runner_v1_20261027.py'),str(lease),sys.executable,str(HERE/'fixed_xl_cached_neighbour_contacts_v2_20261028.py'),'--batch',child,'--source-key',row['sourceKey'],'--lease',str(lease)],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
   if proc.returncode:unresolved.append(dict(uid=uid,reason='diagnostic-error-preserved',log=str(log.relative_to(ROOT))));continue
   result,_=authenticate(doc);completed.append(dict(uid=uid,sourceKey=row['sourceKey'],receipt=str((doc/'result.json').relative_to(ROOT)),allNominatedOriginalsTested=result['allNominatedOriginalsTested'],missingCachedSources=len(result['missingCachedSources']),contacts=[dict(uid=r['peer']['uid'],sourceKey=r['peer']['sourceKey'],count=r['finiteContacts'],positiveSurfaces=r['positiveSurfaceContacts'])for r in result['rows']]));refs.append(doc/'result.json')
  except Exception as error:unresolved.append(dict(uid=uid,reason='controller-error-preserved',errorType=type(error).__name__))
  finally:
   if reservations.owns(receipt):assert reservations.release(receipt)['ok']
   save(out/'progress.json',dict(scope=2,completed=completed,unresolved=unresolved,installationApproved=False));print(dict(uid=uid,completed=len(completed),unresolved=len(unresolved)),flush=True)
 result=dict(uids=sorted(TARGETS),recoveredOriginals=6,completed=completed,unresolved=unresolved,freshIdentityAndPlacementAcceptanceRequired=True,qualification='Original-source contact coverage only. Five assets recovered under pinned sheet metadata; one exact indexed byte-identical asset recovered from a separately identified changed archive. Old archive rejection and all old geometry/support/identity failures retained. Every checked original facet supplied; no new source/placement acceptance, geometry edit, source overwrite or installation credit.')
 save(out/'summary.json',result);module('nine_recovery_contact_followthrough_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-case-exact-original-contact-followthrough-after-six-recoveries',refs,result)
if __name__=='__main__':main()
