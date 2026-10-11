"""Immutable alternate-bearing solid assembly witness using unchanged staged originals."""
import argparse,importlib.util,json,os,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
spec=importlib.util.spec_from_file_location('hsbc_initial_stage',HERE/'xl-terrain-recovery-20261009-hsbc-three-stage-install-v1.py');BASE=importlib.util.module_from_spec(spec);spec.loader.exec_module(BASE)
UIDS=BASE.UIDS;PHYSICAL=BASE.PHYSICAL;ROLE=BASE.ROLE;STAGE=BASE.STAGE;ref=BASE.ref;module=BASE.module;recheck=BASE.recheck
BATCH='government-xl-terrain-recovery-hsbc-three-typed-stage-v2-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;BROWSER_CONFIG=DOC/'browser-config.json';LEASE=HERE/'local'/BATCH/'install-reservation.json'
def owned():
 def owns():assert reservations.owns(read(LEASE))
 def call(cmd):subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();rows,identities,role=recheck(HERE/'local'/BATCH/'identity-recheck');prior=read(BASE.DOC/'acceptance.json');assert prior['passed'] and prior['checksPassed'] and not prior['publication']
 for r in prior['evidenceRefs']:assert ref(ROOT/r['path'])==r
 assert prior['stagedBrowser']==ref(BASE.DOC/'staged-browser.json');save(DOC/'identity-publication-recheck.json',identities);save(DOC/'typed-role-publication-recheck.json.gz',role)
 config=read(STAGE/'browser-config.json');config['doc']=str(DOC.relative_to(ROOT))+'/';config['captureDirectionByModel']={u:[-.65,.75,-.5] for u in UIDS};save(BROWSER_CONFIG,config)
 refs=prior['evidenceRefs']+[ref(p) for p in [Path(__file__),BROWSER_CONFIG,BASE.DOC/'acceptance.json',BASE.DOC/'staged-browser.json',DOC/'identity-publication-recheck.json',DOC/'typed-role-publication-recheck.json.gz']]
 decision=dict(batch=BATCH,uids=sorted(UIDS),sourceSHA256s={r['uid']:r['sourceSHA256'] for r in rows},manifestSHA256=role['manifestSHA256'],checksPassed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,evidenceRefs=refs,qualification='Unchanged original stage, full physical/role/dependencies and current manifest. Distinct clean northwest elevated bearing for visual review, full assembly desktop and original individual mobile; all solid/source/visible/framing/picking/collision/failed-load retry/retained-native own-camera and eligibility gates unchanged. No model or runtime edits.');save(DOC/'stage.json',decision)
 call([sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH]);call(['node',str(HERE/'xl-terrain-recovery-20261009-multi-native-solid-browser-v4.mjs'),'staged',ref(BROWSER_CONFIG)['path']])
 report=module('hsbc_solid_browser_validator',HERE/'integrate.py').browser_verified(DOC/'staged-browser.json',UIDS);expected={(u,w,t) for u in ['landsd/227099:0','landsd/229310:0'] for w in [1280,390] for t in ['15:00','22:00']};assert {(v['uid'],v['width'],v['time']) for v in report['retainedNativeOwnViews']}==expected and all(v['active'] and v['visible'] and v['fullyFramed'] for v in report['retainedNativeOwnViews'])
 for r in refs:assert ref(ROOT/r['path'])==r
 recheck(HERE/'local'/BATCH/'identity-final');decision.update(stagedBrowser=ref(DOC/'staged-browser.json'),passed=True,failures=[],livePublicationRequired=True);save(DOC/'acceptance.json',decision);print(json.dumps(dict(stagedBrowserPassed=True,uids=sorted(UIDS),publication=False,newlyInstalled=0)),flush=True)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--owned',action='store_true');args=parser.parse_args()
 if args.owned:
  from publication_lock import locked_publication
  with locked_publication(ROOT):owned()
  return
 assert not DOC.exists();forms=read(PHYSICAL/'neighbour-inputs.json.gz')['rows'];resources={'building:'+r['building']['uid'] for r in forms}|{'terrain-patch:'+u for u in UIDS}|{'terrain-surface:city/data/government-native-227099-0.json'};claim=reservations.claim('codex-hsbc-three-solid-stage-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
