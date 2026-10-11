"""DRAFT root-handoff closure; run only after atomic v4 installed receipt passes.

No publication or Git. Inherit reviewed source/stage metadata contracts; every
actual source/current numeric/ground dependency remains recursively verified.
"""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-park-haven-hkdi-three-atomic-installed-v4-20261010'
FAILED='government-xl-park-haven-hkdi-three-atomic-installed-v1-20261010'
FAILED_GUARD='government-xl-park-haven-hkdi-three-atomic-installed-v2-20261010'
FAILED_CATALOGUE_GUARD='government-xl-park-haven-hkdi-three-atomic-installed-v3-20261010'
OUT=BASE/'xl-terrain-recovery-20261010-park-hkdi-atomic-installed-scope-v3'
SOURCE=BASE/'xl-terrain-recovery-20261010-park-hkdi-current-source-scope-v1/declared-scope.json'
STAGE=BASE/'xl-terrain-recovery-20261010-park-hkdi-current-source-stage-scope-v1/declared-scope.json'
STAGES=['government-xl-terrain-recovery-park-haven-two-typed-stage-v5-20261010','government-xl-terrain-recovery-hkdi-block-b-qualified-native-stage-v1-20261010']
UIDS={'landsd/246467:0','landsd/320705:0','landsd/89613:0'}
AFE='afe71ffa851d82ab2d1350834b5a6cd1484f28e481bd6bf866ca7a6f73e05d0b'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-certificate',required=True);p.add_argument('--stage-certificate',required=True);a=p.parse_args();assert not OUT.exists()
 folder=BASE/BATCH;result=read(folder/'result.json');sync=read(folder/'neon-sync.json');assert result['publication']is True and result['newlyInstalled']==3 and set(result['installedUids'])==UIDS
 assert sync['jobId']==result['jobId'] and sync['resultVerified']is True and sync['snapshotId']==result['snapshotId'] and set(sync['installedUids'])==UIDS
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
  for uid,sha in result['sourceSHA256s'].items():assert c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(result['snapshotId'],uid)).fetchone()==('installed-verified',sha)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)==result['manifest']
 installed=read(folder/'installed-acceptance.json');assert installed['nativeReacceptance']is False and installed['currentNativeReacceptance']is False and installed['legacyNativeDiagnosticsPreserved']is True
 old=read(STAGE);paths=set(old['closedPaths']);leaves=set(old['metadataLeafPaths']);aliases=list(old['historicalManifestAliases'])
 def add(p):assert p.is_file();paths.add(str(p.relative_to(ROOT)))
 for x in [SOURCE,STAGE,Path(__file__)]:add(x)
 certificates=[]
 for arg in [a.source_certificate,a.stage_certificate]:
  f=ROOT/arg;certificate=read(f);assert certificate['independentlyVerified']is True and certificate['paths'] and certificate['verifiedReferenceVersions']>0;add(f);certificates.append(ref(f));assert ref(f)in read(folder/'acceptance.json')['evidenceRefs']
 assert set(read(SOURCE)['closedPaths'])<=set(read(ROOT/a.source_certificate)['paths'])
 assert set(old['closedPaths'])<=set(read(ROOT/a.stage_certificate)['paths'])
 for parent in [folder,BASE/FAILED,BASE/FAILED_GUARD,BASE/FAILED_CATALOGUE_GUARD,HERE/'local'/BATCH,HERE/'local'/FAILED,HERE/'local'/FAILED_GUARD,HERE/'local'/FAILED_CATALOGUE_GUARD]:
  for x in parent.rglob('*'):
   if x.is_file():add(x)
 for name in STAGES:
  for parent in [BASE/name,HERE/'accepted'/name]:
   for x in parent.rglob('*'):
    if x.is_file():add(x)
  live=read(BASE/name/'live-browser.json');assert live['passed']is True and live['errors']==[]
 for n in ['xl-park-haven-hkdi-three-atomic-live-install-v1-20261010.py','xl-park-haven-hkdi-three-atomic-live-install-v2-20261010.py','xl-park-haven-hkdi-three-atomic-live-install-v3-20261010.py','xl-park-haven-hkdi-three-atomic-live-install-v4-20261010.py']:add(HERE/n)
 failure=read(BASE/FAILED/'live-failure-rollback.json');assert failure['manifestRestoredSHA256']==AFE and failure['installedCreditGranted']is False
 archive_path=BASE/FAILED/'rolled-back-viewer-assets/archive-proof.json';archive=read(archive_path);add(archive_path)
 assert archive['manifestBeforeSHA256']==AFE and archive['publication']is False and archive['modelGeometryChanges']==0 and len(archive['rows'])==2
 original_plan=read(BASE/FAILED/'atomic-plan.json')
 for ar in archive['rows']:
  assert ar['exactAssetBytesPreserved']is True and ar['unreferencedByCurrentManifest']is True
  directory=ROOT/ar['archiveDirectory'];assert directory.is_relative_to(BASE/FAILED/'rolled-back-viewer-assets')
  actual={str(f.relative_to(ROOT)):digest(f.read_bytes())for f in directory.rglob('*')if f.is_file()};assert actual==ar['hashes']
  area=next(x for x in original_plan['areas']if '3d-viewer/'+x['destination']==ar['originalViewerDirectory']+'/catalogue.json')
  assert ref(directory/'catalogue.json')['sha256']==ref(ROOT/area['catalogue'])['sha256']
  for entry in read(directory/'catalogue.json')['models']:
   assert entry['uid']in UIDS and entry['sha256']==result['sourceSHA256s'][entry['uid']]
   assert ref(directory/entry['asset'])['sha256']==entry['sha256']
  for f in directory.rglob('*'):
   if f.is_file():add(f);assert str(f.relative_to(ROOT))not in leaves
 orphan=ROOT/'3d-viewer/city/data/terrain-government-xl-park-haven-original-pair-installed-v1-20261010.json'
 oldplan=read(folder/'atomic-plan.json');assert len(oldplan['topLevelTerrainPatches'])==1
 assert ref(orphan)['sha256']==oldplan['topLevelTerrainPatches'][0]['sha256']
 assert 'city/data/terrain-government-xl-park-haven-original-pair-installed-v1-20261010.json'not in {t['url']for t in read(manifest)['terrainPatches']}
 add(orphan);assert str(orphan.relative_to(ROOT))not in leaves
 before=HERE/'local'/BATCH/'manifest-before-installation.json';assert ref(before)['sha256']==AFE
 add(before);leaves.add(str(before.relative_to(ROOT)));aliases.append(dict(originalPath='3d-viewer/city/data/manifest.json',sha256=AFE,archive=ref(before)))
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';current=read(pointer);assert current['snapshotId']==result['snapshotId'];inventory=ROOT/current['inventory'];assert read(inventory)['derivedFrom']=='af8dc86b47d2b0aa'
 globalmeta=[manifest,pointer,inventory,ROOT/'3d-viewer/city/data/building-progress.json',ROOT/'3d-viewer/scripts/building-progress/review-proof.json',ROOT/'3d-viewer/scripts/building-progress/screening-proof.json',ROOT/'docs/astra-city/landmark-completion-audit/neon-snapshot.json']
 for x in globalmeta:add(x);leaves.add(str(x.relative_to(ROOT)))
 plan=read(folder/'atomic-plan.json');assert len(plan['areas'])==2 and len(plan['topLevelTerrainPatches'])==1
 for area in plan['areas']:
  catalogue=ROOT/'3d-viewer'/area['destination'];add(catalogue)
  for e in read(catalogue)['models']:
   assert e['uid']in UIDS and e['sha256']==result['sourceSHA256s'][e['uid']] and e['proceduralWindows']is False and not e.get('suppressesBuildingUids')
   asset=catalogue.parent/e['asset'];assert ref(asset)['sha256']==e['sha256'];add(asset)
 terrain=ROOT/'3d-viewer'/plan['topLevelTerrainPatches'][0]['destination'];assert ref(terrain)['sha256']==plan['topLevelTerrainPatches'][0]['sha256'];add(terrain)
 # Terrain/model assets above are NUMERICAL inputs, never newly declared leaves.
 assert str(terrain.relative_to(ROOT))not in leaves
 counts=read(folder/'full-xl-current-count.json')['counts'];assert counts==result['fullXLCurrentCounts'] and counts['total']==521 and counts['installedVerified']+counts['remaining']==521
 save(OUT/'declared-scope.json',{**old,'closedPaths':sorted(paths),'closedExplicitPaths':sorted(paths),'presentFileBindings':[ref(ROOT/x)for x in sorted(paths)],'metadataLeafPaths':sorted(leaves),'historicalManifestAliases':aliases,'sourceScope':ref(SOURCE),'stageScope':ref(STAGE),'rootIndependentCertificates':certificates,'completedAtomicInstallation':ref(folder/'result.json'),'installedSnapshot':result['snapshotId'],'publication':True,'newlyInstalled':3,'fullXLCurrentCounts':counts,'noInferredXLDeltaFromThreeSources':True,'nativeReacceptance':False,'currentNativeReacceptance':False,'failedV1RollbackPreserved':True,'failedV2ExistingTerrainGuardPreserved':True,'failedV3ExistingCatalogueGuardPreserved':True,'failedV1PublishedCatalogueArchive':ref(archive_path),'unreferencedFailedV1TerrainArtifact':ref(orphan),'newNumericalMetadataLeaves':False,'rootIndependentRecursiveVerificationRequired':True,'qualification':'Root-owned atomic v4 installed three unchanged sources after all20 live original/retained views and3 retries. Failed v1 server refusal/base rollback plus v2 existing-terrain guard, v3 existing-catalogue guard, byte-identical archived v1 catalogues/assets and unreferenced exact v1 terrain retained without installed credit. Exact reviewed source/stage metadata leaves and pointer contracts inherited; only byte-bound global catalogue/progress/ledger metadata outputs added. Every actual source/terrain/ground/role numeric dependency recursively verified. No native reacceptance, geometry edits or new pointer waiver.'})
 print(dict(paths=len(paths),snapshot=result['snapshotId'],publication=True,newlyInstalled=3),flush=True)
if __name__=='__main__':main()
