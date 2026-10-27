"""Complete source-key diagnostics previously deferred by missing viewer IDs.

Anonymous government units retain exact keys/hashes; no IDs or approvals invented.
"""
import json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from fixed_xl_cached_neighbour_contacts_v2_20261028 import required_resources
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-unmatched-neighbour-contacts-controller-v1-20261028';PRIOR='government-xl-cross-sheet-cached-contacts-controller-v1-20261028';INVENTORY='government-xl-unfinished-territorial-neighbour-inventory-v1-20261028'
def main():
 out=BASE/BATCH;assert not out.exists();authenticate(BASE/PRIOR);authenticate(BASE/INVENTORY);prior=read(BASE/PRIOR/'summary.json');inventory=read(BASE/INVENTORY/'summary.json');keys=[r['sourceKey']for r in prior['unresolved']if r['reason']=='unmatched-source-identity-requires-canonical-resource-resolution'];assert len(keys)==len(set(keys))==20;rows={r['sourceKey']:r for r in inventory['rows']};out.mkdir();done=[];unresolved=[];refs=[Path(__file__),HERE/'fixed_xl_cached_neighbour_contacts_v2_20261028.py',BASE/PRIOR/'result.json',BASE/INVENTORY/'result.json']
 for key in keys:
  row=rows[key];model_id=key.split('/')[1];child='government-xl-anonymous-neighbour-'+model_id.lower()+'-contacts-v1-20261028';doc=BASE/child
  if doc.exists():unresolved.append(dict(sourceKey=key,reason='existing-attempt-preserved'));continue
  claim=reservations.claim('exact-source-key-contact-'+str(uuid.uuid4()),sorted(required_resources(row)),batch=child,ttl=1800)
  if not claim['ok']:unresolved.append(dict(sourceKey=key,reason='canonical-resource-busy-no-takeover'));continue
  lease=HERE/'local'/child/'reservation.json';log=out/(model_id+'.log');receipt=claim['reservation']
  try:
   with log.open('w')as stream:
    save(lease,json.loads(json.dumps(receipt,default=str)));proc=subprocess.run([sys.executable,str(HERE/'observed_reserved_runner_v1_20261027.py'),str(lease),sys.executable,str(HERE/'fixed_xl_cached_neighbour_contacts_v2_20261028.py'),'--batch',child,'--source-key',key,'--lease',str(lease)],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
   if proc.returncode:unresolved.append(dict(sourceKey=key,reason='diagnostic-error-preserved',log=str(log.relative_to(ROOT))));continue
   result,_=authenticate(doc);done.append(dict(sourceKey=key,uid=row['uid'],receipt=str((doc/'result.json').relative_to(ROOT)),allNominatedOriginalsTested=result['allNominatedOriginalsTested'],missingCachedSources=len(result['missingCachedSources']),testedPairs=len(result['rows']),positivePairs=sum(r['finiteContacts']>0 for r in result['rows'])));refs.append(doc/'result.json')
  except Exception as error:unresolved.append(dict(sourceKey=key,reason='controller-error-preserved',errorType=type(error).__name__))
  finally:
   if reservations.owns(receipt):assert reservations.release(receipt)['ok']
   save(out/'progress.json',dict(scope=len(keys),completed=done,unresolved=unresolved,installationApproved=False));print(dict(sourceKey=key,completed=len(done),unresolved=len(unresolved)),flush=True)
 result=dict(uids=sorted(rows[k]['uid']for k in keys if rows[k]['uid']),sourceKeys=keys,completed=done,unresolved=unresolved,qualification='Exact diagnostic source-key coverage of20previously deferred cases. A null viewer UID is never assigned/inferred. Named sources use canonical building leases; anonymous originals use canonical native-source keys. No installation, identity/support approval, model edit or permanent rejection. Missing local assets and busy resources stay unresolved.')
 save(out/'summary.json',result);module('anonymous_neighbour_controller_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-key-diagnostics-for-unmatched-original-neighbours',refs,result)
if __name__=='__main__':main()
