"""Draft supervised terrain-only acquisition. No model/contact arithmetic."""
import argparse,json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,reservations
import citywalk134332_current_ground_only_preflight_draft_v2_20261013 as Q
BATCH='government-xl-citywalk134332-complete-current-drawn-ground-v1-20261013';D=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';P=ROOT/'docs/astra-city/government-import/government-xl-citywalk134332-current-ground-supervisor-freezer-proposal-v1-20261013';JS=HERE/'citywalk134332_current_ground_only_capture_draft_v2_20261013.mjs';FREEZER=HERE/'citywalk134332_freeze_complete_current_ground_draft_v1_20261013.py'
def inputs(a):
 pins=read(P/'executable-pins.json')['refs']
 for e in pins:assert Q.ref(ROOT/e['path'])==e
 v=read(Q.P/'actual13-tests-readonly-preflight-closure-validation-v1.json');assert v['testsPassed']==v['expectedTests']==13 and v['testExitCode']==v['preflightExitCode']==v['closurePreparationExitCode']==0 and v['noRendererImport']
 for e in v['refs']:assert Q.ref(ROOT/e['path'])==e
 q=Q.inputs(a);old=Q.W.inputs(a);assert q['readOnlyPreflightPassed'];resources=sorted(['building:'+u for u in old['uids']]+['native-model:'+old['sourceKey'],'source-context:'+BATCH+'-capture']);assert len(resources)==21
 closure=read(Q.P/'prepared-complete-ground-exporter-module-closure-v1.json');assert closure['entryPath']==str(JS.relative_to(ROOT))
 for p,h in closure['inputHashes'].items():assert Q.ref(ROOT/p)['sha256']==h
 return dict(currentState=old,groundPreparation=q,resources=resources,plan=Q.ref(Q.P/'ground-capture-plan.json'),validation=Q.ref(Q.P/'actual13-tests-readonly-preflight-closure-validation-v1.json'),closure=Q.ref(Q.P/'prepared-complete-ground-exporter-module-closure-v1.json'))
def fence(a,before):assert inputs(a)==before and reservations.owns(read(LEASE))
def main():
 p=argparse.ArgumentParser();p.add_argument('--expected-manifest',required=True);p.add_argument('--preflight-only',action='store_true');p.add_argument('--owned',action='store_true');a=p.parse_args();before=inputs(a)
 if a.preflight_only:print(json.dumps(dict(readOnlyPreflightPassed=True,noWorker=True,canonicalResources=len(before['resources']),uids=len(before['currentState']['uids']),protectedRows=before['currentState']['observedProtectedReviewRecords'])));return
 if not a.owned:
  assert not LOCAL.exists()and not D.exists();claim=reservations.claim('citywalk-ground-only-'+str(uuid.uuid4()),before['resources'],batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True);return
 assert reservations.owns(read(LEASE));save(LOCAL/'protected-state-before.json',before);save(LOCAL/'immutable-lease-at-start.json',read(LEASE));fence(a,before);assert reservations.heartbeat(read(LEASE))['ok'];D.mkdir();subprocess.run(['node',str(JS),str((Q.P/'ground-capture-plan.json').relative_to(ROOT)),str((D/'complete-current-drawn-ground.json.gz').relative_to(ROOT))],cwd=ROOT,check=True);fence(a,before);subprocess.run([sys.executable,str(FREEZER),'--expected-manifest',a.expected_manifest],cwd=ROOT,check=True);fence(a,before);print(json.dumps(dict(groundOnlyFrozen=True,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
