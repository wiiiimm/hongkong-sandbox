"""Serial fenced full foundation diagnostics for all six affected originals."""
from pathlib import Path
import json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-fuying181489-six-foundation-sequence-v1-20261029';RUNTIME='government-xl-fuying181489-five-member-runtime-v2-20261029';ATTRS='government-xl-fuying181489-five-member-attributes-v1-20261029';PATCH='government-xl-fuying181489-five-member-boundary-contract-v2-20261029';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__),HERE/'fuying_four_world_foundation_context_v1_20261029.py'];receipts={}
 for n in [RUNTIME,ATTRS,PATCH]:receipts[n]=authenticate(BASE/n)[0];refs.append(BASE/n/'result.json')
 assert receipts[RUNTIME]['allSixOriginalsCaptured']and receipts[PATCH]['allTerrainValidatorsPassed'];uids=['landsd/181489:0']+sorted(set(receipts[RUNTIME]['uids'])-{'landsd/181489:0'});assert len(uids)==6;DOC.mkdir();results=[]
 for uid in uids:
  assert reservations.owns(lease);batch=BATCH+'-'+uid.split('/')[1].replace(':','-');folder=BASE/batch;assert not folder.exists();logpath=DOC/(uid.split('/')[1].replace(':','-')+'.log');command=[sys.executable,str(HERE/'fuying_four_world_foundation_context_v1_20261029.py'),'--batch',batch,'--runtime',RUNTIME,'--attributes',ATTRS,'--uid',uid]
  with logpath.open('w')as log:process=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
  assert process.returncode==0,(uid,process.returncode);receipt,pins=authenticate(folder);summarypath=folder/'summary.json';assert digest(summarypath.read_bytes())==pins[str(summarypath.relative_to(ROOT))];result=read(summarypath);assert result['uids']==[uid]and len(result['rows'])==4;refs.extend([folder/'result.json',summarypath]);results.append(dict(uid=uid,batch=batch,jobId=receipt['jobId'],establishedFoundationPolicyPassed=result['establishedFoundationPolicyPassed'],rows=result['rows']));save(DOC/'progress.json',dict(uids=uids,completed=results,remaining=uids[len(results):],running=True));print(dict(uid=uid,completed=len(results),passed=result['establishedFoundationPolicyPassed']),flush=True)
 summary=dict(uids=uids,rows=results,allSixFourWorldFoundationsComplete=True,allEstablishedFoundationPoliciesPassed=all(r['establishedFoundationPolicyPassed']for r in results),sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False);save(DOC/'summary.json',summary);save(DOC/'progress.json',dict(uids=uids,completed=results,remaining=[],running=False));assert reservations.owns(lease)
 module('fuying_six_foundations_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-six-originals-four-world-foundation-sequence-no-acceptance',refs,summary)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();uids=read(BASE/PATCH/'summary.json')['completeTargetObligations'];keys=['building:'+u for u in uids]+['terrain:city/data/terrain.json','terrain:city/data/government-native-fu-wong-original-v1-20261023.json'];claim=reservations.claim('fuying-six-foundations-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
