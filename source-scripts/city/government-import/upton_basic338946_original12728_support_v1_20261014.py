"""ROOT-only missing genuine replacement support for current elevated BASIC tower.
Reuse exact complete116-face before/after finite and1911/52/6650 scope; no waiver.
"""
from pathlib import Path
import sys,json,subprocess,time,uuid
from run import ROOT,HERE,read,save,connect,reservations
import upton_podium_standalone_tower_fallback_guard_v1_20261014 as fallback
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
physical=fallback.physical;ref,check=physical.ref,physical.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-basic338946-original12728-support-v1-20261014';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LEASE=LOCAL/'reservation.json';RUNTIME=HERE/'upton_basic338946_original12728_support_v1_20261014.mjs'
PODIUM,TOWER=physical.OWNED;FALLBACK_JOB='8d471169e854cd487b673744ae46f4cec860ff39c9a0e8e3e89b7a90794f0a46'
def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 r=read(fallback.DOC/'result.json');v=read(fallback.DOC/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==FALLBACK_JOB and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased']
 state=read(fallback.DOC/'standalone-podium-prerequisites.json');assert state['reasons']==['neighbour-regression:'+TOWER]and not state['standaloneCurrentTowerFallbackGuardPassed']
 basic=read(fallback.DOC/'whole-current-tower-BASIC-finite-regression.json.gz');assert basic['uid']==TOWER and basic['completeFaces']==116 and not basic['currentClearCandidateUnproved']and basic['allOldNegativeRecordsRetained']
 neighbours=read(fallback.DOC/'neighbour-checks.json');row=next(r for r in neighbours['rows']if r['uid']==TOWER);assert row['reasons']==['increased-neighbour-ground-gap']and not row['existingNative']and not row['candidate']
 selection=read(physical.DOC/'selection.json.gz')['rows'];podium=next(r for r in selection if r['uid']==PODIUM);assert ref(ROOT/podium['candidate']['path'])['sha256']==podium['sourceSHA256']
 b=read(fallback.DOC/'current-tower-BASIC-constructor.json.gz')['row'];assert b['uid']==TOWER and b['currentForm'].get('parent')and b['currentForm']['parent']==podium['source']['building']['parent']
 support=read(physical.DOC/'support-checks.json.gz')['rows'][0];assert support['sourceSHA256']==next(r for r in selection if r['uid']==TOWER)['sourceSHA256']and support['supportSHA256']==podium['sourceSHA256']and len(support['unresolved'])==41
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==physical.CURRENT
 return pins,state,basic,row,podium
def schema_only():
 p,s,b,r,podium=load();return dict(passed=True,caller=ref(Path(__file__)),actualBASICFaces=116,actualOriginalPodiumFaces=1655,rawGroundGapReasonRetained=True,heldOriginalTower41Retained=True,noSupportHeightsOrContactsDBLeaseWorker=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,state,basic,raw,podium=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs']
 for folder in [fallback.DOC,physical.DOC]:
  result=read(folder/'result.json')
  with connect()as con:con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 def fence():
  for q in distinct_refs(refs):check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==physical.CURRENT;pulse(True)
 fence();DOC.mkdir(parents=True);save(DOC/'input.json',dict(actualBasicConstructor=ref(fallback.DOC/'current-tower-BASIC-constructor.json.gz'),actualBasicFinite=ref(fallback.DOC/'whole-current-tower-BASIC-finite-regression.json.gz'),actualOriginalRuntime=ref(physical.LOCAL/'runtime-geometry.json.gz'),actualPhysicalSupport=ref(physical.DOC/'support-checks.json.gz'),sourceSHA256=podium['sourceSHA256']))
 command=['node',str(RUNTIME),str(DOC.relative_to(ROOT))+'/'];p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);save(DOC/'actual-support-log.json',dict(command=command,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0;pulse(True)
 proof=read(DOC/'actual-BASIC338946-original12728-support.json.gz');assert proof['actualBasicWholeWorldSHA256']==basic['completeWorldSHA256']and proof['supportSourceSHA256']==podium['sourceSHA256']and proof['native50PercentRuleNotApplied']and proof['originalTower41NeverResolved']
 for path,digest in proof['inputHashes'].items():q=dict(path=path,sha256=digest);check(q);refs.append(q)
 passed=proof['strictCompleteBasicInterfacePassed'];remaining=[]if passed else raw['reasons']
 save(DOC/'standalone-ground-gap-source-support-attribution.json',dict(uid=TOWER,standaloneOwnedUID=PODIUM,rawCurrentNeighbourVerbatim=raw,completeCurrentBASICBeforeAfterProof=ref(fallback.DOC/'whole-current-tower-BASIC-finite-regression.json.gz'),exactReplacementOriginalPodiumSupport=ref(DOC/'actual-BASIC338946-original12728-support.json.gz'),strictCompleteBasicSupportProposedResolution=passed,remainingBasicGroundGapReasons=remaining,rawGroundDeltaNeverChanged=True,noAutomaticNative50PercentApproval=True,originalTowerSourceRemainsHeld41=True,all1911BASIC52Native6650AndFourModeProofsRetained=state['unchanged1911BASIC52FourModeNativeProof'],sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()];fence();physical.module(physical.FREEZER,'upton_basic_exact_support_freezer').freeze(BATCH,'actual-current-BASIC338946-exact-original12728-strict-support-existing-predicates',[check(q)for q in distinct_refs(refs)],dict(uids=[PODIUM,TOWER],currentManifestSHA256=physical.CURRENT,sourceOnly=True,sourceGeometryChanges=0,physicalAccepted=False,newlyInstalled=0))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--check-actual-basic-original-podium-support-only'in sys.argv and not DOC.exists()and not LOCAL.exists();load()
 uids=physical.finite.baseline.OWNED+[physical.SECONDARY,physical.RETAINED,physical.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton-basic-support-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
