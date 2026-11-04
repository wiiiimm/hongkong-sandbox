"""Stage only two unchanged Cullinan towers; existing VWalk is not reapproved."""
import importlib.util,json,os,subprocess,sys,shutil,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect
from dependency_preflight import from_catalogues
UIDS={'landsd/161931:0','landsd/120158:0'};NATIVE='landsd/262871:0'
BASE=ROOT/'docs/astra-city/government-import'
PHYS=[BASE/f'government-xl-terrain-recovery-cullinan-west-{t}-unchanged-current-terrain-physical-v2-20261010'for t in ['tower3','tower5']];PHYSICAL=PHYS[0]
ROLE=BASE/'xl-terrain-recovery-20261011-cullinan-west-complete-current-role-v5'
ROLE_SCRIPT=HERE/'xl-terrain-recovery-20261011-cullinan-west-complete-current-role-v5.py'
BATCH='government-xl-terrain-recovery-cullinan-west-two-qualified-native-stage-v1-20261011';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH;LEASE=HERE/'local'/BATCH/'install-reservation.json'
BROWSER=HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def normalized(value):return json.loads(json.dumps(value))
def recheck(local=None):
 receipt=read(ROLE/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 role=normalized(module('cullinan_staging_current_role',ROLE_SCRIPT).recheck());assert role==read(ROLE/'typed-role.json.gz') and role['currentTypedPhysicalAccepted'] and role['reasons']==[]
 assert role['completeOriginalFaces']==22312 and role['completeOriginalComponents']==32 and role['completeCurrentNeighbourForms']==3
 assert not role['currentNativeReacceptance']and not role['nativeReacceptance']and role['terrainProposal']==[]and not role['terrainProposalGeometryChanged']
 support=role['mandatoryInstalledNativeSupport'];assert support['uid']==NATIVE and support['installedVerified']is False and support['wholeNativeReaccepted']is False
 rows=[read(p/'selection.json.gz')['rows'][0]for p in PHYS];assert {r['uid']for r in rows}==UIDS
 return rows,role['currentOwnedIdentities'],role
def owned():
 def owns():assert reservations.owns(read(LEASE))
 def call(cmd):subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();rows,identities,role=recheck();save(DOC/'identity-publication-recheck.json',identities);save(DOC/'typed-role-publication-recheck.json.gz',role)
 native=role['completeCurrentInstalledNativeEntryPreserved'];assert native['uid']==NATIVE and native['publicationApproved']is False and native['buildingCSUID']=='3389220874P20180705'and native['sha256']==role['mandatoryInstalledNativeSupport']['sourceSHA256'];save(DOC/'retained-native-exact-entry-before-stage.json',native)
 dep=dict(uid=NATIVE,csuid=native['buildingCSUID'],sha256=native['sha256'],state='installed');entries=[]
 for row in rows:
  entry=dict(row['candidate']['entry']);assert not entry.get('supportDependencies')and not entry.get('suppressesBuildingUids')and not entry.get('footprintScope')
  entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,sourceIdentityReviewUsedAI=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,supportDependencies=[dep],placementReview='Complete unchanged original tower. All owned renderable structural parts use independently rooted current VWalk part51 through exact nonzero edge bodies and whole exposed original/literal positive interfaces. Three source-authored visual details receive no structural roots or bridges. Every original/literal owned facet, current identity, wholefoundation, basic/native and runtime guard passed. Dependency installed means current native availability only; VWalk publicationApproved:false and all legacy negatives remain unchanged. No source pose, geometry or terrain changes.')
  asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['candidate']['path'],asset);assert ref(asset)['sha256']==entry['sha256'];entries.append(entry)
 catalogue=read(HERE/'local'/PHYSICAL.name/'catalogue.json');catalogue.update(models=entries,counts={'packedModels':2},area='Cullinan West original towers 3 and 5, qualified current VWalk support');save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',[r['source']['building']for r in rows])
 destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=catalogue['area'],catalogue=ref(STAGE/'catalogue.json')['path'],destination=destination)],topLevelTerrainPatches=[]))
 deps=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json']);assert len(deps['rows'])==2 and all(not r['blockers']for r in deps['rows']);save(DOC/'dependencies.json',deps)
 capture={}
 for e in entries:
  b=next(b for b in role['completeWholeOriginalLiteralFloat32ProtectedActors']if b['uid']==e['uid']);bounds=[e['worldBounds'],b['providerCompletePOSITIONProof']['originalWholeSourceBounds'],b['literalCompletePositionBounds'],b['float32CompletePositionBounds']];capture[e['uid']]=[[min(bb[0][i]for bb in bounds)for i in range(3)],[max(bb[1][i]for bb in bounds)for i in range(3)]]
 config=dict(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[],fitBox=True,captureDirectionByModel={r['uid']:[.6,.9,.6]for r in rows},captureBoundsByModel=capture,browserUids=[r['uid']for r in rows],failureTestUids=[r['uid']for r in rows],nativeSupportUidsByModel={u:[NATIVE]for u in UIDS});save(STAGE/'browser-config.json',config)
 paths=[Path(__file__),ROLE_SCRIPT,ROLE/'result.json',ROLE/'typed-role.json.gz',DOC/'identity-publication-recheck.json',DOC/'typed-role-publication-recheck.json.gz',DOC/'retained-native-exact-entry-before-stage.json',DOC/'dependencies.json',STAGE/'catalogue.json',STAGE/'plan.json',STAGE/'browser-config.json',BROWSER,*[p/'result.json'for p in PHYS]]
 evidence=[ref(p)for p in paths];decision=dict(batch=BATCH,uids=sorted(UIDS),sourceSHA256s={e['uid']:e['sha256']for e in entries},manifestSHA256=role['currentManifest']['sha256'],checksPassed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,terrainProposalGeometryChanged=False,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,nativeReacceptance=False,legacyDependencyStateMeansCurrentNativeAvailabilityOnly=True,evidenceRefs=evidence);save(DOC/'stage.json',decision)
 call([sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH]);call(['node',str(BROWSER),'staged',ref(STAGE/'browser-config.json')['path']])
 report=module('cullinan_browser_stage_validator',HERE/'integrate.py').browser_verified(DOC/'staged-browser.json',UIDS);views=[v for v in report['views']if 'time'in v]
 assert len(views)==8 and {(v['uid'],v['width'],v['time'])for v in views}=={(u,w,t)for u in UIDS for w in [1280,390]for t in ['15:00','22:00']}
 own=report['retainedNativeOwnViews'];assert len(own)==4 and {(v['uid'],v['width'],v['time'])for v in own}=={(NATIVE,w,t)for w in [1280,390]for t in ['15:00','22:00']};assert all(v['active']and v['visible']and v['fullyFramed']for v in own)
 for view in views:assert set(view['nativeSupports'])=={NATIVE};assert all(w['active']and w['visible']for w in view['nativeSupports'].values())
 assert {v['uid']for v in report['views']if v.get('fallbackRetained')}==UIDS
 for r in evidence:assert ref(ROOT/r['path'])==r
 _,_,final=recheck();assert final==role and final['completeCurrentInstalledNativeEntryPreserved']==native
 decision.update(stagedBrowser=ref(DOC/'staged-browser.json'),passed=True,failures=[],livePublicationRequired=True);save(DOC/'acceptance.json',decision);print(dict(stagedBrowserPassed=True,publication=False,newlyInstalled=0),flush=True)
def main():
 if '--owned'in sys.argv:
  from publication_lock import locked_publication
  with locked_publication(ROOT):owned()
  return
 assert not DOC.exists()and not STAGE.exists();rows=read(PHYSICAL/'neighbour-inputs.json.gz')['rows'];keys={'building:'+r['building']['uid']for r in rows}|{'building:'+u for u in UIDS|{NATIVE}}
 claim=reservations.claim('cullinan-qualified-native-stage-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
