"""Stage six unchanged independent Market originals and reviewed dual native ground.

This only prepares assets, dry-runs publication and runs staged browser acceptance.
Root performs separately guarded live publication after reviewing every receipt.
"""
import argparse,importlib.util,json,os,shutil,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect,NATIVE_RUN
from dependency_preflight import from_catalogues
UIDS={'landsd/'+u+':0' for u in ['313033','313034','313116','313118','313119','313121']}
PHYSICAL=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-market-six-original-physical-v5-20261009'
ROLE=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-market-six-current-role-v10'
BATCH='government-xl-terrain-recovery-market-six-typed-stage-v1-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
STAGE=HERE/'accepted'/BATCH
LEASE=HERE/'local'/BATCH/'install-reservation.json'
def ref(p):return dict(path=str(Path(p).relative_to(ROOT)),sha256=digest(Path(p).read_bytes()))
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def recheck(local):
 physical=read(PHYSICAL/'result.json');role_result=read(ROLE/'result.json')
 for doc,result in [(PHYSICAL,physical),(ROLE,role_result)]:
  assert read(doc/'neon-sync.json')==dict(jobId=result['jobId'],resultVerified=True)
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 assert physical['publication'] is False and physical['newlyInstalled']==physical['modelGeometryChanges']==physical['scriptExternalAICalls']==0
 rows=read(PHYSICAL/'selection.json.gz')['rows'];assert {r['uid'] for r in rows}==UIDS
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for row in rows:assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 kernel=module('market_fresh_original_roles',HERE/'xl-terrain-recovery-20261009-market-six-current-role-v10.py');role=kernel.recheck();assert json.loads(json.dumps(role))==read(ROLE/'typed-role.json.gz')
 assert role['independentPhysicalChecksPassed'] and not role['unresolvedIndependentPhysicalReasons'] and role['verifiedPodiumWallRole']['verifiedWallRole']
 assert role['completeOriginalFaces']==40100 and role['completeOriginalComponents']==84 and role['currentNeighbourFormsAccounted']==42
 assert {r['uid'] for r in role['completeFreshCurrentIdentities']}==UIDS and all(r['passed'] for r in role['completeFreshCurrentIdentities'])
 for r in role_result['evidenceRefs']:assert ref(ROOT/r['path'])==r
 return rows,role['completeFreshCurrentIdentities'],role
def owned():
 def owns():assert reservations.owns(read(LEASE))
 def call(cmd):subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();rows,identities,role=recheck(HERE/'local'/BATCH/'identity-recheck')
 save(DOC/'identity-publication-recheck.json',identities);save(DOC/'typed-role-publication-recheck.json.gz',role)
 entries=[]
 for row in rows:
  entry=dict(row['candidate']['entry']);assert not entry.get('suppressesBuildingUids') and not entry.get('supportDependencies')
  entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,sourceIdentityReviewUsedAI=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,
   placementReview='Unchanged original government source and root. Six independent provider identities/current geographic cells pass. Complete40100 source faces/84 components support-accounted using actual strict ground roots and exact original positive-dimensional contacts; exact zero-area source face retained without renderable support credit and three whole under-deck facets retain the strict±.1m contact band. Sole17 original podium crossing walls independently bound to exposed original roofs and full current foreign separation; all ordinary/upward faces, whole foundations,42currentforms and two retained original native neighbours pass. Source/world/current-ground inputs exactly rebound after unrelated Miami publication; no geometry/elevation edits or AI modelling.')
  asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['candidate']['path'],asset);assert ref(asset)['sha256']==entry['sha256'];entries.append(entry)
 catalogue=read(HERE/'local'/PHYSICAL.name/'catalogue.json');catalogue.update(models=entries,counts={'packedModels':6},area='Market In six unchanged independent government originals')
 save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',dict(models=6,catalogues=['catalogue.json']))
 forms=read(PHYSICAL/'neighbour-inputs.json.gz')['rows'];source_forms=[r['building'] for r in forms if r['building']['uid'] in UIDS];assert {r['uid'] for r in source_forms}==UIDS;save(STAGE/'source-forms.json',source_forms)
 candidates=read(PHYSICAL/'terrain-candidates.json');assert len(candidates)==1;c=candidates[0];assert set(c['uids'])==UIDS and len(c['replacesMany'])==2 and not c.get('replaces');assert ref(ROOT/c['path'])['sha256']==c['sha256']
 patch=STAGE/Path(c['path']).name;shutil.copyfile(ROOT/c['path'],patch);p=read(patch);assert p.get('nativeMesh') and not p.get('patches')
 assert p['meta']['parentTerrain']=='city/data/terrain.json' and p['meta']['parentSha256']==ref(ROOT/'3d-viewer/city/data/terrain.json')['sha256']
 terrain=dict(source=ref(patch)['path'],sha256=ref(patch)['sha256'],destination='city/data/'+patch.name,resolution=p['cell'],area=catalogue['area']+' indexed original terrain')
 native=read(PHYSICAL/'native-neighbour-checks.json');assert all(r['passed'] for r in native['rows']);manifest=ROOT/'3d-viewer/city/data/manifest.json';current=read(manifest);replacements=[]
 for i,replacement in enumerate(c['replacesMany']):
  assert ref(ROOT/'3d-viewer'/replacement['url'])['sha256']==replacement['sha256'];assert replacement['url'] in {r['url'] for r in current['terrainPatches']}
  assert set(replacement['retainedUids'])<=set(p['meta']['targetUids']) and set(replacement['retainedUids'])<={r['uid'] for r in native['rows']}
  review=dict(status='approved-for-integration',supersededURL=replacement['url'],supersededSHA256=replacement['sha256'],replacementSHA256=terrain['sha256'],sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,retainedUids=replacement['retainedUids'],replacementTargetUids=p['meta']['targetUids'],fullMeshCheck=ref(PHYSICAL/'native-neighbour-checks.json'))
  reviewpath=DOC/f'native-replacement-review-{i}.json';save(reviewpath,review);replacements.append(dict(**replacement,nativeReview=ref(reviewpath)))
 terrain['replacesMany']=replacements
 destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=catalogue['area'],catalogue=ref(STAGE/'catalogue.json')['path'],destination=destination)],topLevelTerrainPatches=[terrain]))
 dependencies=from_catalogues(manifest,[STAGE/'catalogue.json']);assert not any(r['blockers'] for r in dependencies['rows']);save(DOC/'dependencies.json',dependencies)
 save(STAGE/'browser-config.json',dict(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[terrain],fitBox=True,captureBoundsByModel={e['uid']:e['worldBounds'] for e in entries},browserUids=sorted(UIDS),failureTestUids=sorted(UIDS),nativeSupportUidsByModel={uid:['landsd/313032:0','landsd/99395:0'] for uid in UIDS}))
 evidence=[ref(q) for q in [Path(__file__),PHYSICAL/'result.json',ROLE/'result.json',ROLE/'typed-role.json.gz',DOC/'identity-publication-recheck.json',DOC/'typed-role-publication-recheck.json.gz',DOC/'dependencies.json',STAGE/'catalogue.json',STAGE/'plan.json',STAGE/'browser-config.json',HERE/'xl-terrain-recovery-20261009-market-six-current-role-v10.py',HERE/'reviewed_multi_native_terrain_publication_20261009.py',HERE/'test_reviewed_multi_native_terrain_publication_20261009.py',HERE/'xl-terrain-recovery-20261009-publish-reviewed-multi-native.py',HERE/'xl-terrain-recovery-20261009-multi-native-assembly-browser.mjs']]+[r['nativeReview'] for r in replacements]
 decision=dict(batch=BATCH,uids=sorted(UIDS),sourceSHA256s={r['uid']:r['sourceSHA256'] for r in rows},manifestSHA256=role['manifestSHA256'],checksPassed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,evidenceRefs=evidence)
 save(DOC/'stage.json',decision)
 call([sys.executable,str(HERE/'xl-terrain-recovery-20261009-publish-reviewed-multi-native.py'),ref(STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH])
 call(['node',str(HERE/'xl-terrain-recovery-20261009-multi-native-assembly-browser.mjs'),'staged',ref(STAGE/'browser-config.json')['path']])
 module('market_browser_validator',HERE/'integrate.py').browser_verified(DOC/'staged-browser.json',UIDS)
 for r in evidence:assert ref(ROOT/r['path'])==r
 recheck(HERE/'local'/BATCH/'identity-recheck-final')
 decision.update(stagedBrowser=ref(DOC/'staged-browser.json'),passed=True,failures=[],livePublicationRequired=True);save(DOC/'acceptance.json',decision);print(json.dumps(dict(stagedBrowserPassed=True,uids=sorted(UIDS),publication=False,newlyInstalled=0)),flush=True)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--owned',action='store_true');a=parser.parse_args()
 if a.owned:
  from publication_lock import locked_publication
  with locked_publication(ROOT,BATCH,timeout=300):owned()
  return
 assert not DOC.exists() and not STAGE.exists()
 forms=read(PHYSICAL/'neighbour-inputs.json.gz')['rows'];resources={'building:'+r['building']['uid'] for r in forms}|{'terrain-patch:'+u for u in UIDS}
 resources|={'terrain-surface:'+r['url'] for r in read(PHYSICAL/'terrain-candidates.json')[0]['replacesMany']}
 claim=reservations.claim('codex-market-stage-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
