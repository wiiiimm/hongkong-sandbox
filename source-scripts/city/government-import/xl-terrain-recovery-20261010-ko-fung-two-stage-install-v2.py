"""Stage two unchanged Ko Fung originals and single retained original terrain.
No live publication. Root separately reviews/replays and publishes atomically.
"""
import argparse,importlib.util,json,os,shutil,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect,NATIVE_RUN
from exact_original_georef_cell_identity_20261009 import verify_files
from dependency_preflight import from_catalogues
UIDS={'landsd/'+u+':0' for u in ['79097','110480']}
PHYSICAL=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-ko-fung-original-pair-current-physical-v3-20261010'
BASE=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-ko-fung-pair-current-inputs-v1'
ROLE=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261010-ko-fung-current-mounted-role-v1'
BATCH='government-xl-terrain-recovery-ko-fung-two-typed-stage-v2-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH;STAGE=HERE/'accepted'/BATCH;LEASE=HERE/'local'/BATCH/'install-reservation.json'
def ref(p):return dict(path=str(Path(p).relative_to(ROOT)),sha256=digest(Path(p).read_bytes()))
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def recheck(local):
 physical=read(PHYSICAL/'result.json');rr=read(ROLE/'result.json');rows=read(PHYSICAL/'selection.json.gz')['rows'];assert {r['uid'] for r in rows}==UIDS
 kernel=module('ko_fung_current_original_roles',HERE/'xl-terrain-recovery-20261010-ko-fung-current-mounted-role-v1.py')
 for doc,r in [(PHYSICAL,physical),(ROLE,rr)]:
  assert read(doc/'neon-sync.json')==dict(jobId=r['jobId'],resultVerified=True)
  with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:kernel.archived_or_current(e)
 identities=[];contexts={c['uid']:c for c in read(BASE/'context.json.gz')['rows']}
 for row in rows:
  identity=verify_files(row,contexts[row['uid']],local/row['uid'].split('/')[1].replace(':','-'));assert identity['passed'];identities.append(identity)
 role=kernel.recheck();assert role==read(ROLE/'typed-role.json.gz') and role['independentPhysicalChecksPassed'] and not role['unresolvedIndependentPhysicalReasons'] and role['completeVerifiedMountedVisualRoles']['allComponentsAccounted']
 assert role['completeOriginalFaces']==15561 and role['completeOriginalComponents']==666 and role['currentNeighbourFormsAccounted']==26
 return rows,identities,role
def owned():
 def owns():assert reservations.owns(read(LEASE))
 def call(cmd):subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();rows,identities,role=recheck(HERE/'local'/BATCH/'identity-recheck');save(DOC/'identity-publication-recheck.json',identities);save(DOC/'typed-role-publication-recheck.json.gz',role)
 podium=next(r for r in rows if r['uid']=='landsd/110480:0');dependency=dict(uid=podium['uid'],csuid=podium['source']['building']['buildingCSUID'],sha256=podium['sourceSHA256'],state='candidate');entries=[]
 for row in rows:
  entry=dict(row['candidate']['entry']);assert not entry.get('suppressesBuildingUids') and not entry.get('supportDependencies')
  entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,sourceIdentityReviewUsedAI=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,supportDependencies=[] if row['uid']==podium['uid'] else [dependency],placementReview='Unchanged complete original government Ko Fung tower and original podium. Two independent exact provider/current geographic-cell identities; all15561 original/rendered faces satisfy complete finite unchanged ordinary clearance. Original podium grade root plus603 positive-dimensional original interfaces anchor547 structural components;118 complete authored open-back facade details have entire original opening mounts within the existing finite contact band, and one slanted original triangle has two exact top-edge point mounts. Visuals supply no root/load-bearing/actor bridge. Every whole foundation,26current forms and retained274320 native, sampler/runtime checks pass. Raw earlier failures retained; source POSITION/NORMAL/COLOR/root/elevation unchanged; zero AI geometry modelling.')
  asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['candidate']['path'],asset);assert ref(asset)['sha256']==entry['sha256'];entries.append(entry)
 catalogue=read(HERE/'local'/PHYSICAL.name/'catalogue.json');catalogue.update(models=entries,counts={'packedModels':2},area='Ko Fung complete original tower and original podium');save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']))
 forms=read(PHYSICAL/'neighbour-inputs.json.gz')['rows'];sourceforms=[r['building'] for r in forms if r['building']['uid'] in UIDS];assert {r['uid'] for r in sourceforms}==UIDS;save(STAGE/'source-forms.json',sourceforms)
 candidates=read(PHYSICAL/'terrain-candidates.json');assert len(candidates)==1;c=candidates[0];assert set(c['uids'])==UIDS and c.get('replaces') and not c.get('replacesMany') and ref(ROOT/c['path'])['sha256']==c['sha256'];patch=STAGE/Path(c['path']).name;shutil.copyfile(ROOT/c['path'],patch);p=read(patch);assert p.get('nativeMesh') and not p.get('patches')
 assert p['meta']['parentTerrain']=='city/data/terrain.json' and p['meta']['parentSha256']==ref(ROOT/'3d-viewer/city/data/terrain.json')['sha256'];terrain=dict(source=ref(patch)['path'],sha256=ref(patch)['sha256'],destination='city/data/'+patch.name,resolution=p['cell'],area=catalogue['area']+' indexed original terrain')
 replacement=c['replaces'];assert ref(ROOT/'3d-viewer'/replacement['url'])['sha256']==replacement['sha256'];assert replacement['url'] in {r['url'] for r in read(ROOT/'3d-viewer/city/data/manifest.json')['terrainPatches']};assert set(replacement['retainedUids'])=={'landsd/274320:0'} and set(replacement['retainedUids'])<=set(p['meta']['targetUids'])
 review=dict(status='approved-for-integration',supersededURL=replacement['url'],supersededSHA256=replacement['sha256'],replacementSHA256=terrain['sha256'],sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,retainedUids=replacement['retainedUids'],replacementTargetUids=p['meta']['targetUids'],fullMeshCheck=ref(PHYSICAL/'native-neighbour-checks.json'));save(DOC/'native-replacement-review.json',review);terrain.update(replaces=replacement,nativeReview=ref(DOC/'native-replacement-review.json'))
 destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=catalogue['area'],catalogue=ref(STAGE/'catalogue.json')['path'],destination=destination)],topLevelTerrainPatches=[terrain]))
 dependencies=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json']);assert not any(r['blockers'] for r in dependencies['rows']);save(DOC/'dependencies.json',dependencies)
 assembly=[[min(e['worldBounds'][0][i] for e in entries) for i in range(3)],[max(e['worldBounds'][1][i] for e in entries) for i in range(3)]]
 config=dict(captureDirectionByModel={u:[-.65,.75,-.5] for u in UIDS},stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[terrain],fitBox=True,captureBoundsByModel={e['uid']:e['worldBounds'] for e in entries},captureBoundsByViewport={'1280':{e['uid']:assembly for e in entries}},browserUids=sorted(UIDS),failureTestUids=sorted(UIDS),nativeSupportUidsByModel={u:replacement['retainedUids'] for u in UIDS});save(STAGE/'browser-config.json',config)
 evidence=[ref(q) for q in [Path(__file__),PHYSICAL/'result.json',ROLE/'result.json',ROLE/'typed-role.json.gz',DOC/'identity-publication-recheck.json',DOC/'typed-role-publication-recheck.json.gz',DOC/'dependencies.json',DOC/'native-replacement-review.json',STAGE/'catalogue.json',STAGE/'plan.json',STAGE/'browser-config.json',HERE/'xl-terrain-recovery-20261010-ko-fung-current-mounted-role-v1.py',HERE/'xl-terrain-recovery-20261009-multi-native-solid-browser-v4.mjs',HERE/'exact_original_georef_cell_identity_20261009.py']]
 decision=dict(batch=BATCH,uids=sorted(UIDS),sourceSHA256s={r['uid']:r['sourceSHA256'] for r in rows},manifestSHA256=role['manifestSHA256'],checksPassed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,evidenceRefs=evidence);save(DOC/'stage.json',decision)
 call([sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH]);call(['node',str(HERE/'xl-terrain-recovery-20261009-multi-native-solid-browser-v4.mjs'),'staged',ref(STAGE/'browser-config.json')['path']])
 report=module('ko_fung_browser_validator',HERE/'integrate.py').browser_verified(DOC/'staged-browser.json',UIDS);expected={(u,w,t) for u in replacement['retainedUids'] for w in [1280,390] for t in ['15:00','22:00']};assert {(v['uid'],v['width'],v['time']) for v in report['retainedNativeOwnViews']}==expected and all(v['active'] and v['visible'] and v['fullyFramed'] for v in report['retainedNativeOwnViews'])
 for r in evidence:assert ref(ROOT/r['path'])==r
 recheck(HERE/'local'/BATCH/'identity-recheck-final');decision.update(stagedBrowser=ref(DOC/'staged-browser.json'),passed=True,failures=[],livePublicationRequired=True);save(DOC/'acceptance.json',decision);print(json.dumps(dict(stagedBrowserPassed=True,uids=sorted(UIDS),publication=False,newlyInstalled=0)),flush=True)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--owned',action='store_true');a=parser.parse_args()
 if a.owned:
  from publication_lock import locked_publication
  with locked_publication(ROOT):owned()
  return
 assert not DOC.exists() and not STAGE.exists();forms=read(PHYSICAL/'neighbour-inputs.json.gz')['rows'];resources={(('building:' if r['building']['uid'].startswith('landsd/') else 'foreign-form:')+r['building']['uid']) for r in forms}|{'terrain-patch:'+u for u in UIDS}|{'terrain-surface:city/data/government-native-274320-0.json'}
 claim=reservations.claim('codex-ko-fung-two-stage-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
