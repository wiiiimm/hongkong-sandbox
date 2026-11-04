"""Stage one untouched Block11 source and reviewed current-parent replacement.

No live writes. Only native254491 is a declared structural dependency; all four
current native actors receive separate clean own-camera presence witnesses.
Their exact legacy entries/flags remain untouched and none is reapproved.
"""
import importlib.util,json,os,subprocess,sys,shutil,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from dependency_preflight import from_catalogues
BASE=ROOT/'docs/astra-city/government-import';UIDS={'landsd/255647:0'};NATIVE='landsd/254491:0';RETAINED=['landsd/254491:0','landsd/255439:0','landsd/256112:0','landsd/256114:0']
PHYSICAL=BASE/'government-xl-terrain-recovery-parkview-block11-authentic-retained-current-physical-v2-20261011';ROLE=BASE/'xl-terrain-recovery-20261011-parkview-block11-current-role-v2';ROLE_SCRIPT=HERE/'xl-terrain-recovery-20261011-parkview-block11-complete-current-role-v2.py'
BATCH='government-xl-parkview-block11-authentic-current-stage-v1-20261011';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH;LEASE=HERE/'local'/BATCH/'install-reservation.json';BROWSER=HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs'
TERRAIN_DESTINATION='city/data/terrain-government-xl-parkview-block11-authentic-installed-v1-20261011.json'
def ref(p):return dict(path=str(Path(p).relative_to(ROOT)),sha256=digest(Path(p).read_bytes()))
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def recheck(local=None):
 receipt=read(ROLE/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for p in receipt['evidenceRefs']:assert ref(ROOT/p['path'])==p
 role=json.loads(json.dumps(module('parkview_stage_current_role',ROLE_SCRIPT).recheck()));assert role==read(ROLE/'typed-role.json.gz')and role['currentTypedPhysicalAccepted']and role['scriptChecksPassed']and role['reasons']==[]
 assert role['completeOriginalFaces']==10679 and role['completeOriginalComponents']==81 and role['completeCurrentNeighbourForms']==26 and role['independentlySupportedStructuralOwnedComponents']==80 and role['visualOnlyOwnedComponents']==[324]
 assert role['nativeReacceptance']is False and role['namedRoofUnitRootOrBridgeCredit']is False and role['terrainProposalGeometryChanged']is True
 assert role['mandatoryInstalledNativeSupport']['uid']==NATIVE and role['mandatoryInstalledNativeSupport']['installedVerified']is False and role['mandatoryInstalledNativeSupport']['wholeNativeReaccepted']is False
 rows=read(PHYSICAL/'selection.json.gz')['rows'];assert {r['uid']for r in rows}==UIDS
 return rows,role['currentOwnedIdentities'],role

def owned():
 def owns():assert reservations.owns(read(LEASE))
 def call(cmd):subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();rows,identities,role=recheck();save(DOC/'identity-publication-recheck.json',identities);save(DOC/'typed-role-publication-recheck.json.gz',role)
 nativeentries=role['completeCurrentInstalledNativeEntriesPreserved'];assert set(nativeentries)==set(RETAINED);save(DOC/'retained-native-exact-entries-before-stage.json',nativeentries)
 native=nativeentries[NATIVE];assert native['uid']==NATIVE and native['sha256']==role['mandatoryInstalledNativeSupport']['sourceSHA256'];dependency=dict(uid=NATIVE,csuid=native['buildingCSUID'],sha256=native['sha256'],state='installed');row=rows[0];entry=dict(row['candidate']['entry']);assert not entry.get('supportDependencies')and not entry.get('suppressesBuildingUids')and not entry.get('footprintScope')
 entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,sourceIdentityReviewUsedAI=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,supportDependencies=[dependency],placementReview='Complete unchanged original government Block11 source. Every10679 owned face clears actual drawn terrain in original/literal and two explicitly computed Float32 model-matrix arithmetic orders. Eighty structural components have complete nonzero-edge bodies and exact positive-dimensional original contact paths to main285. Support uses only existing native254491 wall60989 genuine finite grade→exposed original edge→strict clear cap57951→ownedface0; no whole-native root or reapproval. Original72-face rooftop appendage324 mounts by its complete six-edge lower loop within the existing finite band; its two upper openings, triple incidences and raw negatives remain, with no structural/root/bridge credit. All26 current forms/four actual native checks, whole foundation, current identity/runtime/sampler and complete current source bounds pass. Explicit authenticated two-sheet terrain proposal replaces the old255439 terrain while preserving Block9 and eighteen disjoint ordinary footprints. Every building source vertex/index/normal/color/root/elevation remains unchanged; zero AI geometry modelling.')
 asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['candidate']['path'],asset);assert ref(asset)['sha256']==entry['sha256'];catalogue=read(HERE/'local'/PHYSICAL.name/'catalogue.json');catalogue.update(models=[entry],counts={'packedModels':1},area='Parkview Block11 complete unchanged original, authenticated current terrain');save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',[row['source']['building']])
 candidate=role['terrainProposal'];assert len(candidate)==1;c=candidate[0];replacement=c['replaces'];assert replacement['url']=='city/data/government-native-255439-0.json'and replacement['retainedUids']==['landsd/255439:0']and ref(ROOT/'3d-viewer'/replacement['url'])['sha256']==replacement['sha256'];assert ref(ROOT/c['path'])['sha256']==c['sha256'];sourcepatch=read(ROOT/c['path']);assert sourcepatch.get('nativeMesh')and not sourcepatch.get('patches')and sourcepatch['meta']['targetUids']==['landsd/255439:0',row['uid']]
 validator=module('parkview_stage_final_native_validator',HERE.parent/'island-detail-integration/native_terrain_validation.py');validator.validate_native_mesh(sourcepatch,read(ROOT/'3d-viewer/city/data/terrain.json'))
 stagedpatch=STAGE/'authenticated-terrain.json';shutil.copyfile(ROOT/c['path'],stagedpatch);assert ref(stagedpatch)['sha256']==c['sha256'];terrain=dict(source=ref(stagedpatch)['path'],sha256=c['sha256'],destination=TERRAIN_DESTINATION,resolution=sourcepatch['cell'],area=catalogue['area'])
 review=dict(status='approved-for-integration',supersededURL=replacement['url'],supersededSHA256=replacement['sha256'],replacementSHA256=c['sha256'],sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,terrainProposalGeometryChanged=True,retainedUids=replacement['retainedUids'],replacementTargetUids=sourcepatch['meta']['targetUids'],fullMeshCheck=ref(PHYSICAL/'native-neighbour-checks.json'),completeCurrentRole=ref(ROLE/'typed-role.json.gz'),allFourCurrentNativeEntriesUntouched=True,wholeNativeReacceptance=False);save(DOC/'native-replacement-review.json',review);terrain.update(replaces=replacement,nativeReview=ref(DOC/'native-replacement-review.json'))
 destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=catalogue['area'],catalogue=ref(STAGE/'catalogue.json')['path'],destination=destination)],topLevelTerrainPatches=[terrain]));deps=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json']);assert len(deps['rows'])==1 and all(not r['blockers']for r in deps['rows']);save(DOC/'dependencies.json',deps)
 bounds=role['completeOwnedWholePOSITIONLiteralExplicitF32ProtectedBounds']['union'];capture=[[min(bounds[0][i],entry['worldBounds'][0][i])for i in range(3)],[max(bounds[1][i],entry['worldBounds'][1][i])for i in range(3)]]
 # v5 uses this browser-only census both for eligibility and own-camera visits;
 # it does not create catalogue support relationships to the other3 actors.
 config=dict(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[terrain],fitBox=True,captureDirectionByModel={row['uid']:[.6,.8,.6]},captureBoundsByModel={row['uid']:capture},browserUids=[row['uid']],failureTestUids=[row['uid']],nativeSupportUidsByModel={row['uid']:RETAINED},mandatoryActualStructuralSupportUidsByModel={row['uid']:[NATIVE]},retainedOwnCameraOnlyUIDs=[u for u in RETAINED if u!=NATIVE]);save(STAGE/'browser-config.json',config)
 paths=[Path(__file__),ROLE_SCRIPT,ROLE/'result.json',ROLE/'typed-role.json.gz',PHYSICAL/'result.json',DOC/'identity-publication-recheck.json',DOC/'typed-role-publication-recheck.json.gz',DOC/'retained-native-exact-entries-before-stage.json',DOC/'dependencies.json',DOC/'native-replacement-review.json',STAGE/'catalogue.json',STAGE/'plan.json',STAGE/'browser-config.json',stagedpatch,BROWSER,HERE.parent/'island-detail-integration/native_terrain_validation.py'];evidence=[ref(p)for p in paths];decision=dict(batch=BATCH,uids=sorted(UIDS),sourceSHA256s={entry['uid']:entry['sha256']},manifestSHA256=role['currentManifest']['sha256'],checksPassed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,terrainProposalGeometryChanged=True,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,nativeReacceptance=False,legacyDependencyStateMeansCurrentNativeAvailabilityOnly=True,evidenceRefs=evidence);save(DOC/'stage.json',decision)
 call([sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH]);call(['node',str(BROWSER),'staged',ref(STAGE/'browser-config.json')['path']]);report=module('parkview_browser_validator',HERE/'integrate.py').browser_verified(DOC/'staged-browser.json',UIDS);views=[v for v in report['views']if 'time'in v];assert len(views)==4 and {(v['uid'],v['width'],v['time'])for v in views}=={(u,w,t)for u in UIDS for w in [1280,390]for t in ['15:00','22:00']}
 own=report['retainedNativeOwnViews'];assert len(own)==16 and {(v['uid'],v['width'],v['time'])for v in own}=={(u,w,t)for u in RETAINED for w in [1280,390]for t in ['15:00','22:00']};assert all(v['active']and v['visible']and v['fullyFramed']for v in own)
 for v in views:
  assert set(v['nativeSupports'])==set(RETAINED);assert v['nativeSupports'][NATIVE]['active']and v['nativeSupports'][NATIVE]['visible']
  assert all(not s['wanted']or(s['active']and s['visible'])for s in v['nativeSupports'].values())
 assert {v['uid']for v in report['views']if v.get('fallbackRetained')}==UIDS
 for p in evidence:assert ref(ROOT/p['path'])==p
 _,_,final=recheck();assert final==role and final['completeCurrentInstalledNativeEntriesPreserved']==nativeentries;decision.update(stagedBrowser=ref(DOC/'staged-browser.json'),passed=True,failures=[],livePublicationRequired=True);save(DOC/'acceptance.json',decision);print(dict(stagedBrowserPassed=True,uids=sorted(UIDS),publication=False,newlyInstalled=0),flush=True)
def main():
 if '--owned'in sys.argv:
  from publication_lock import locked_publication
  with locked_publication(ROOT):owned()
  return
 assert not DOC.exists()and not STAGE.exists();forms=read(PHYSICAL/'neighbour-inputs.json.gz')['rows'];keys={'building:'+r['building']['uid']for r in forms}|{'building:'+u for u in UIDS|set(RETAINED)}|{'terrain-patch:'+u for u in UIDS}|{'terrain-surface:city/data/government-native-255439-0.json','terrain-surface:'+TERRAIN_DESTINATION}
 claim=reservations.claim('parkview-block11-authentic-stage-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
