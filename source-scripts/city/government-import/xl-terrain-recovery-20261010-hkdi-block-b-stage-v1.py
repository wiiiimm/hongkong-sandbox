"""Stage only unchanged HKDI Block B with qualified existing native carrier.

No terrain replacement or legacy native reacceptance; root owns live publication.
"""
import importlib.util,json,os,subprocess,sys,shutil,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect
from dependency_preflight import from_catalogues
UID='landsd/89613:0';NATIVE='landsd/22089:0';UIDS={UID}
BASE=ROOT/'docs/astra-city/government-import'
PHYSICAL=BASE/'government-xl-terrain-recovery-hkdi-block-b-unchanged-current-terrain-physical-v2-20261010'
ROLE=BASE/'government-xl-terrain-recovery-hkdi-block-b-post-atomic-complete-current-role-v2-20261010'
BATCH='government-xl-terrain-recovery-hkdi-block-b-qualified-native-stage-v1-20261010';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH;LEASE=HERE/'local'/BATCH/'install-reservation.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def recheck(local=None):
 receipt=read(ROLE/'result.json')
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 role=module('hkdi_staging_complete_current_role',HERE/'xl-terrain-recovery-20261010-hkdi-block-b-post-atomic-complete-current-role-v2.py').recheck();assert role==read(ROLE/'typed-role.json.gz') and role['currentTypedPhysicalAccepted']is True and role['reasons']==[] and role['completeOriginalFaces']==11593 and role['completeOriginalComponents']==345 and role['completeCurrentNeighbourForms']==2
 assert role['currentNativeReacceptance']is False and role['nativeReacceptance']is False and role['terrainProposal']==[] and role['terrainProposalGeometryChanged']is False and role['mandatoryInstalledNativeSupport']['uid']==NATIVE
 rows=read(PHYSICAL/'selection.json.gz')['rows'];assert len(rows)==1 and rows[0]['uid']==UID
 return rows,[role['currentOwnedIdentity']],role

def owned():
 def owns():assert reservations.owns(read(LEASE))
 def call(cmd):subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();rows,identities,role=recheck();save(DOC/'identity-publication-recheck.json',identities);save(DOC/'typed-role-publication-recheck.json.gz',role)
 native=role['completeCurrentInstalledNativeEntryPreserved'];assert native['uid']==NATIVE and native['sha256']==role['mandatoryInstalledNativeSupport']['sourceSHA256'];save(DOC/'retained-native-exact-entry-before-stage.json',native)
 dep=dict(uid=NATIVE,csuid=native['buildingCSUID'],sha256=native['sha256'],state='installed');row=rows[0];entry=dict(row['candidate']['entry']);assert not entry.get('supportDependencies') and not entry.get('suppressesBuildingUids') and not entry.get('footprintScope')
 entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,sourceIdentityReviewUsedAI=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,supportDependencies=[dep],placementReview='Untouched complete original11593-face HKDI Block B. All345 source components resolved through independently qualified existing native131 exposed cap, independently rooted native144 and four genuine literal roots. Complete original and actual finite clearance/current wholefoundation/current twoforms and native fullmesh preserved. Existing native61 coarse/46 finite/27 unsupported diagnostics remain explicit; no native reacceptance, structural credit to unqualified parts, terrain change or source geometry edit.')
 asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['candidate']['path'],asset);assert ref(asset)['sha256']==entry['sha256']
 catalogue=read(HERE/'local'/PHYSICAL.name/'catalogue.json');catalogue.update(models=[entry],counts={'packedModels':1},area='HKDI original Block B, current qualified native cap support');save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',[row['source']['building']])
 destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=catalogue['area'],catalogue=ref(STAGE/'catalogue.json')['path'],destination=destination)],topLevelTerrainPatches=[]));deps=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json']);assert len(deps['rows'])==1 and not deps['rows'][0]['blockers'];save(DOC/'dependencies.json',deps)
 config=dict(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[],fitBox=True,captureDirectionByModel={UID:[.6,.9,.6]},captureBoundsByModel={UID:entry['worldBounds']},browserUids=[UID],failureTestUids=[UID],nativeSupportUidsByModel={UID:[NATIVE]});save(STAGE/'browser-config.json',config)
 paths=[Path(__file__),PHYSICAL/'result.json',ROLE/'result.json',ROLE/'typed-role.json.gz',DOC/'identity-publication-recheck.json',DOC/'typed-role-publication-recheck.json.gz',DOC/'retained-native-exact-entry-before-stage.json',DOC/'dependencies.json',STAGE/'catalogue.json',STAGE/'plan.json',STAGE/'browser-config.json',HERE/'xl-terrain-recovery-20261010-hkdi-block-b-post-atomic-complete-current-role-v2.py',HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs']
 evidence=[ref(p)for p in paths];decision=dict(batch=BATCH,uids=[UID],sourceSHA256s={UID:entry['sha256']},manifestSHA256=role['currentManifest']['sha256'],checksPassed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,terrainProposalGeometryChanged=False,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,nativeReacceptance=False,evidenceRefs=evidence);save(DOC/'stage.json',decision)
 call([sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH]);call(['node',str(HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs'),'staged',ref(STAGE/'browser-config.json')['path']])
 report=module('hkdi_browser_stage_validator',HERE/'integrate.py').browser_verified(DOC/'staged-browser.json',UIDS);assert len(report['retainedNativeOwnViews'])==4 and {v['uid']for v in report['retainedNativeOwnViews']}=={NATIVE}
 for view in report['views']:
  if 'time'in view:assert set(view['nativeSupports'])=={NATIVE};assert all(w['active']and w['visible']for w in view['nativeSupports'].values()if w.get('wanted'))
 for r in evidence:assert ref(ROOT/r['path'])==r
 _,_,final=recheck();assert final==role and final['completeCurrentInstalledNativeEntryPreserved']==native;decision.update(stagedBrowser=ref(DOC/'staged-browser.json'),passed=True,failures=[],livePublicationRequired=True);save(DOC/'acceptance.json',decision);print(dict(stagedBrowserPassed=True,publication=False,newlyInstalled=0),flush=True)
def main():
 if '--owned'in sys.argv:
  from publication_lock import locked_publication
  with locked_publication(ROOT):owned()
  return
 assert not DOC.exists()and not STAGE.exists();rows=read(PHYSICAL/'neighbour-inputs.json.gz')['rows'];keys={'building:'+r['building']['uid']for r in rows}|{'building:'+UID,'building:'+NATIVE};claim=reservations.claim('hkdi-qualified-native-stage-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
