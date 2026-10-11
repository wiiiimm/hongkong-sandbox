"""Draft root-completed Mount publication closure; no live actions or install credit.

Execute only after root reviews live exports and the verified result exists.
All reviewed source/stage numeric boundaries stay unchanged. The exact previous
manifest is the sole additional historical alias, not a terrain/source leaf.
"""
from pathlib import Path
import struct,sys
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/'government-xl-mount-verdant-installed-declared-scope-v1-20261011'
DECL=BASE/'government-xl-mount-verdant-stage-declared-scope-v1-20261011/declared-scope.json'
CERT=BASE/'government-xl-mount-verdant-stage-root-closure-v1-20261011/root-closed-scope.json'
INSTALL='government-xl-mount-verdant-two-unchanged-installed-v1-20261011';IDOC=BASE/INSTALL;LOCAL=HERE/'local'/INSTALL
STAGED='government-xl-terrain-recovery-mount-verdant-two-typed-stage-v1-20261011';SDOC=BASE/STAGED;STAGE=HERE/'accepted'/STAGED
UIDS={'landsd/261717:0','landsd/75782:0'};SOURCES={'landsd/261717:0':'c8e54f42cd1f52ce94d1112a5c51bd58674fdbe38d8af6ac0de2b9498fbddec1','landsd/75782:0':'4d3d6e5e5b08c6f33b1ce710161edc3554998f7afc7ee15ce29577f9e4c2f781'}
BEFORE='b61c0bc2d706793c7d436ef3334ccb41e93675d3d50c29818a2dca3b56f8830e'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert '--root-live-export-review-complete'in sys.argv and not DOC.exists()
 prior=read(DECL);certificate=read(CERT);assert certificate['independentlyVerified']
 result=read(IDOC/'result.json');installed=read(IDOC/'installed-acceptance.json');sync=read(IDOC/'neon-sync.json')
 assert result['publication']and result['newlyInstalled']==installed['newlyInstalled']==2 and set(result['installedUids'])==UIDS
 assert result['fullXLCurrentCounts']==dict(total=521,installedVerified=227,remaining=294)
 assert ref(ROOT/result['manifest']['path'])==result['manifest'] and sync['resultVerified']and sync['jobId']==result['jobId']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
  for uid in UIDS:assert c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(result['snapshotId'],uid)).fetchone()==('installed-verified',SOURCES[uid])
 report=read(SDOC/'live-browser.json');assert report['passed']and not report['errors']and not report.get('retainedNativeOwnViews')
 views=[v for v in report['views']if 'time'in v];assert len(views)==8 and {(v['uid'],v['width'],v['time'])for v in views}=={(u,w,t)for u in UIDS for w in[1280,390]for t in['15:00','22:00']}
 assert {v['uid']for v in report['views']if v.get('fallbackRetained')}==UIDS
 for v in views:
  expected={'landsd/75782:0'}if v['uid']=='landsd/261717:0'else set();assert set(v['nativeSupports'])==expected
  assert all(p['active']and p['visible']and p.get('declaredCandidateSupport')for p in v['nativeSupports'].values())
  raw=(SDOC/v['file']).read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n'and struct.unpack('>II',raw[16:24])[0]==v['width']
 before=LOCAL/'manifest-before-installation.json';assert digest(before.read_bytes())==BEFORE
 aliases=list(prior['historicalManifestAliases']);aliases.append(dict(originalPath='3d-viewer/city/data/manifest.json',sha256=BEFORE,archive=ref(before)))
 paths=set(prior['closedPaths'])|set(certificate['paths'])|{str(DECL.relative_to(ROOT)),str(CERT.relative_to(ROOT)),str(Path(__file__).relative_to(ROOT))}
 for folder in[IDOC,LOCAL,SDOC,STAGE,ROOT/'docs/astra-city/model-integration-20260909'/INSTALL]:
  assert folder.is_dir();paths.update(str(p.relative_to(ROOT))for p in folder.rglob('*')if p.is_file())
 plan=read(IDOC/'atomic-plan.json');assert len(plan['areas'])==len(plan['topLevelTerrainPatches'])==1
 catalogue=ROOT/'3d-viewer'/plan['areas'][0]['destination'];paths.update(str(p.relative_to(ROOT))for p in catalogue.parent.rglob('*')if p.is_file())
 terrain=ROOT/'3d-viewer'/plan['topLevelTerrainPatches'][0]['destination'];assert ref(terrain)['sha256']==plan['topLevelTerrainPatches'][0]['sha256'];paths.add(str(terrain.relative_to(ROOT)))
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';inventory=ROOT/read(pointer)['inventory'];assert read(pointer)['snapshotId']==read(inventory)['snapshotId']==result['snapshotId']
 paths.update(str(p.relative_to(ROOT))for p in[pointer,inventory])
 for name in['3d-viewer/city/data/manifest.json','3d-viewer/city/data/building-progress.json','3d-viewer/scripts/building-progress/review-proof.json','3d-viewer/scripts/building-progress/screening-proof.json','docs/astra-city/landmark-completion-audit/neon-snapshot.json','source-scripts/city/building-progress/export.py','3d-viewer/scripts/build_progress.mjs','source-scripts/city/government-import/xl-current-installed-count-audit.py']:paths.add(name)
 out=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],metadataLeafPaths=prior['metadataLeafPaths'],metadataLeafJsonPointers=prior['metadataLeafJsonPointers'],historicalManifestAliases=aliases,sourceStageDeclaration=ref(DECL),sourceStageCertificate=ref(CERT),newMetadataLeaves=False,newMetadataPointerContract=False,newHistoricalAlias=aliases[-1],rootLiveExportsReviewed=True,fullNumericalSourceClosureRequired=True,sourceGeometryChanges=0,liveWritesExcluded=True,recordsRootPublication=True,installedReceipt=ref(IDOC/'result.json'),installedSnapshot=result['snapshotId'],installedNeonJob=result['jobId'],installedCounts=result['fullXLCurrentCounts'],newlyInstalled=0)
 assert out['metadataLeafPaths']==prior['metadataLeafPaths']and out['metadataLeafJsonPointers']==prior['metadataLeafJsonPointers'];save(DOC/'declared-scope.json',out);print(dict(paths=len(paths),recordsRootPublication=True,liveWrites=False),flush=True)
if __name__=='__main__':main()
