"""Private unchanged-terrain Elements two-tower stage; no live publication."""
import importlib.util,json,os,subprocess,sys,shutil,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect
from dependency_preflight import from_catalogues
BASE=ROOT/'docs/astra-city/government-import'
UIDS={'landsd/204145:0','landsd/204143:0'};NATIVE='landsd/273061:0';RETAINED={'landsd/273061:0','landsd/204144:0'}
PHYSICAL=BASE/'government-xl-terrain-recovery-elements-sun-star-unchanged-current-physical-v1-20261011';PHYS=[PHYSICAL]
ROLE=BASE/'xl-terrain-recovery-20261011-elements-pair-complete-current-role-v2';ROLE_SCRIPT=HERE/'xl-terrain-recovery-20261011-elements-pair-complete-current-role-v2.py'
BATCH='government-xl-terrain-recovery-elements-sun-star-two-qualified-native-stage-v2-20261011';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH;LEASE=HERE/'local'/BATCH/'install-reservation.json'
BROWSER=HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def normalized(v):return json.loads(json.dumps(v))
def recheck(local=None):
 receipt=read(ROLE/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for pin in receipt['evidenceRefs']:assert ref(ROOT/pin['path'])==pin
 role=normalized(module('elements_stage_current_role',ROLE_SCRIPT).recheck(local));assert role==read(ROLE/'typed-role.json.gz')and role['currentTypedPhysicalAccepted']is True and role['reasons']==[]
 assert role['completeOriginalFaces']==23809 and role['completeOriginalNonzeroBodies']==998 and not role['nativeReacceptance']and role['terrainProposal']==[]and not role['terrainProposalGeometryChanged']
 assert {r['uid']for r in role['retainedNativeExactEntries']}==RETAINED
 rows=read(PHYSICAL/'selection.json.gz')['rows'];assert {r['uid']for r in rows}==UIDS
 return rows,role['currentOwnedIdentities'],role

def owned():
 def owns():assert reservations.owns(read(LEASE))
 def call(cmd):subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();rows,identities,role=recheck();save(DOC/'identity-publication-recheck.json',identities);save(DOC/'typed-role-publication-recheck.json.gz',role)
 retained=role['retainedNativeExactEntries'];save(DOC/'retained-native-exact-entries-before-stage.json',retained);native=next(r['entry']for r in retained if r['uid']==NATIVE)
 dep=dict(uid=NATIVE,csuid=native['buildingCSUID'],sha256=native['sha256'],state='installed');entries=[]
 for row in rows:
  entry=dict(row['candidate']['entry']);assert not entry.get('supportDependencies')and not entry.get('suppressesBuildingUids')and not entry.get('footprintScope')
  entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,sourceIdentityReviewUsedAI=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,supportDependencies=[dep],placementReview='Complete unchanged government original Elements tower. The entire 23809-face pair is accounted in four captured arithmetic streams: 866 nonvisual bodies use only twelve qualified native grade/exposed-cap interfaces and exact exposed owned paths; 132 complete source visual bodies have separately reviewed nonstructural frame, mounted, perimeter or visual-placement roles. Every source zero remains uncredited. All current identity, wholefoundation, finite-ground, foreign/basic/native and runtime guards pass. Retained Elements and Moon source entries remain unchanged; no whole native reapproval, source geometry, terrain or pose change.')
  target=STAGE/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['candidate']['path'],target);assert ref(target)['sha256']==entry['sha256'];entries.append(entry)
 catalogue=read(HERE/'local'/PHYSICAL.name/'catalogue.json');catalogue.update(models=entries,counts={'packedModels':2},area='Elements complete unchanged Suntower and Startower');save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',[r['source']['building']for r in rows])
 destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=catalogue['area'],catalogue=ref(STAGE/'catalogue.json')['path'],destination=destination)],topLevelTerrainPatches=[]))
 deps=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json']);assert len(deps['rows'])==2 and all(not r['blockers']for r in deps['rows']);save(DOC/'dependencies.json',deps)
 regional=read(ROOT/role['completeRegionalCurrentProof']['path']);capture={}
 for uid in UIDS:
  r=next(r for r in regional['completeProtectedModelBounds']if r['uid']==uid);bb=[r['completeOriginalPOSITIONProof']['originalWholeSourceBounds'],*r['completeLiteralBothF32Bounds']];capture[uid]=[[min(b[0][k]for b in bb)for k in range(3)],[max(b[1][k]for b in bb)for k in range(3)]]
 config=dict(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[],fitBox=True,captureDirectionByModel={u:[.6,.9,.6]for u in UIDS},captureBoundsByModel=capture,browserUids=[r['uid']for r in rows],failureTestUids=[r['uid']for r in rows],nativeSupportUidsByModel={u:sorted(RETAINED)for u in UIDS});save(STAGE/'browser-config.json',config)
 paths=[Path(__file__),ROLE_SCRIPT,ROLE/'result.json',ROLE/'typed-role.json.gz',DOC/'identity-publication-recheck.json',DOC/'typed-role-publication-recheck.json.gz',DOC/'retained-native-exact-entries-before-stage.json',DOC/'dependencies.json',STAGE/'catalogue.json',STAGE/'plan.json',STAGE/'browser-config.json',BROWSER,PHYSICAL/'result.json']
 evidence=[ref(p)for p in paths];decision=dict(batch=BATCH,uids=sorted(UIDS),sourceSHA256s={e['uid']:e['sha256']for e in entries},manifestSHA256=role['currentManifest']['sha256'],checksPassed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,terrainGeometryChanges=0,terrainProposalGeometryChanged=False,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,nativeReacceptance=False,mandatoryCurrentNativeSupport=NATIVE,retainedNativeOwnCameraUids=sorted(RETAINED),evidenceRefs=evidence);save(DOC/'stage.json',decision)
 call([sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH]);call(['node',str(BROWSER),'staged',ref(STAGE/'browser-config.json')['path']])
 report=module('elements_stage_browser_validator',HERE/'integrate.py').browser_verified(DOC/'staged-browser.json',UIDS);views=[v for v in report['views']if 'time'in v]
 assert len(views)==8 and {(v['uid'],v['width'],v['time'])for v in views}=={(u,w,t)for u in UIDS for w in [1280,390]for t in ['15:00','22:00']}
 own=report['retainedNativeOwnViews'];assert len(own)==8 and {(v['uid'],v['width'],v['time'])for v in own}=={(u,w,t)for u in RETAINED for w in [1280,390]for t in ['15:00','22:00']};assert all(v['active']and v['visible']and v['fullyFramed']for v in own)
 for v in views:
  assert set(v['nativeSupports'])==RETAINED and v['nativeSupports'][NATIVE]['active']and v['nativeSupports'][NATIVE]['visible']
  for uid,w in v['nativeSupports'].items():
   expected=next(r['entry']for r in retained if r['uid']==uid);assert w['sourceSHA256']==expected['sha256']
   if w['wanted']:assert w['active']and w['visible']
 assert {v['uid']for v in report['views']if v.get('fallbackRetained')}==UIDS
 for pin in evidence:assert ref(ROOT/pin['path'])==pin
 _,_,final=recheck();assert final==role and final['retainedNativeExactEntries']==retained
 decision.update(stagedBrowser=ref(DOC/'staged-browser.json'),passed=True,failures=[],livePublicationRequired=True);save(DOC/'acceptance.json',decision);print(dict(stagedBrowserPassed=True,publication=False,newlyInstalled=0),flush=True)
def main():
 if '--owned'in sys.argv:
  from publication_lock import locked_publication
  with locked_publication(ROOT):owned()
  return
 assert not DOC.exists()and not STAGE.exists();inputs=read(PHYSICAL/'neighbour-inputs.json.gz')['rows'];keys={'building:'+r['building']['uid']for r in inputs}|{'building:'+u for u in UIDS|RETAINED}
 claim=reservations.claim('elements-qualified-native-stage-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
