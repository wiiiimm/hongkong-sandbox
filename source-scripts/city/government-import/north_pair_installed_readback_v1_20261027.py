"""Independent full-runtime/521-source/Neon readback after actual installation."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
import north_pair_guarded_publish_v1_20261027 as guard
from north_pair_install_transition_v1_20261027 import verify as verify_entries
from original_independent_atomic_contract_v1_20261027 import manifest_triple_transition
P=guard.P;BASE=guard.BASE;SOURCES=guard.SOURCES

def main():
 installed=BASE/guard.BATCH;out=BASE/(P+'installed-root-readback-v1-20261027');assert not out.exists()
 receipt,pins=authenticate(installed);refs=[Path(__file__),installed/'result.json']
 assert receipt['sourceSHA256ByUid']==SOURCES and receipt['newlyInstalled']==1 and receipt['completeCurrentCatalogueModels']==6991
 assert receipt['fullXLCurrentCounts']==dict(total=521,installedVerified=396,remaining=125)
 for path,sha in pins.items():
  p=ROOT/path;assert digest(p.read_bytes())==sha,path;refs.append(p)
 history=read(installed/'historical-input-context.json');historical={r['originalPath']:r for r in history['mutableCurrentByteSnapshots']}
 manifest=ROOT/'3d-viewer/city/data/manifest.json';oldref=historical[str(manifest.relative_to(ROOT))]['savedHistoricalBytes'];oldpath=ROOT/oldref['path'];assert digest(oldpath.read_bytes())==oldref['sha256'];before=read(oldpath);after=read(manifest)
 assert before['tiles']==after['tiles']and before['counts']==after['counts']
 before_models=[];old_assets=[]
 for url in before['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;refs.append(path)
  for m in read(path)['models']:
   asset=path.parent/m['asset'];assert digest(asset.read_bytes())==m['sha256'];refs.append(asset);old_assets.append(m['uid']);before_models.append(m)
 assert len(old_assets)==len(set(old_assets))==6989
 after_models=[m for url in after['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']]
 new=[m for m in after_models if m['uid']in SOURCES]
 cfg=read(guard.stage.STAGE/'live-browser-config.json');overlay=cfg['availabilityOverlays'][0]
 assert verify_entries(before_models,after_models,new,overlay['activationGroup'])
 planned=read(guard.stage.STAGE/'plan.json')['topLevelTerrainPatches'];manifest_triple_transition(before,after,planned)
 oldfields={k:v for k,v in before.items()if k not in ['officialModelCatalogues','terrainPatches']};newfields={k:v for k,v in after.items()if k not in ['officialModelCatalogues','terrainPatches']};assert oldfields==newfields
 for m in new:
  assert m['rootTranslation']==[-834500,0,816500]and m.get('verticalPlacementOffsetHKPD',0)==0
  assert not m.get('supportDependencies')and m['proceduralWindows']is False
  assert all(m[k]is True for k in ['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved'])
 global_dir=BASE/(P+'live-global-before-v1-20261027');_,global_pins=authenticate(global_dir);global_path=global_dir/'summary.json'
 assert digest(global_path.read_bytes())==global_pins[str(global_path.relative_to(ROOT))];global_before=read(global_path);refs.extend([global_dir/'result.json',global_path])
 assert global_before['currentManifestSHA256']==oldref['sha256']and global_before['tileCount']==len(before['tiles'])
 for relative,sha in global_before['globalInputHashes'].items():
  if relative=='3d-viewer/city/data/manifest.json':continue
  path=ROOT/relative;assert digest(path.read_bytes())==sha,relative;refs.append(path)
 prior=read(BASE/'government-xl-ocean-coordinated-original-original-installed-v1-20261027/full-xl-current-count.json');current=read(installed/'full-xl-current-count.json')
 assert len(prior['rows'])==len(current['rows'])==521
 assert sum(r['uid']is None for r in prior['rows'])==sum(r['uid']is None for r in current['rows'])==2
 gained=[]
 for a,b in zip(prior['rows'],current['rows']):
  assert a['indexedSourceSHA256']==b['indexedSourceSHA256']and a['uid']==b['uid']
  assert not a['installedVerified']or b['installedVerified']
  if b['installedVerified']and not a['installedVerified']:gained.append(b['uid'])
 assert gained==['landsd/182397:0']
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert read(pointer)['snapshotId']==receipt['snapshotId']
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for uid,sha in SOURCES.items():assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(receipt['snapshotId'],uid)).fetchone()==('installed-verified',sha)
 observations=read(installed/'ROOT-LIVE-EXPORT-OBSERVATIONS.json');assert observations['actuallyInspectedExports']==8 and observations['aiGeometryModelling']is False
 assert {(r['uid'],r['width'],r['time'])for r in observations['rows']}=={(u,w,t)for u in SOURCES for w in [390,1280]for t in ['15:00','22:00']}
 for row in observations['rows']:
  path=ROOT/row['image']['path'];assert digest(path.read_bytes())==row['image']['sha256'];refs.append(path)
 refs.extend([manifest,pointer,installed/'ROOT-LIVE-EXPORT-OBSERVATIONS.json',installed/'full-xl-current-count.json',guard.stage.STAGE/'plan.json',HERE/'north_pair_install_transition_v1_20261027.py'])
 result=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,fullOldRuntimeAssetsVerified=6989,completeCurrentCatalogueModels=6991,fullXLCurrentCounts=current['counts'],onlyNewFixedXLUid=gained[0],unmatchedUIDKeysRetained=2,snapshotId=receipt['snapshotId'],existingSouthChange='activationGroup-only',sourceGeometryChanges=0,sourcePoseChanges=0,allBasicTilesUnchanged=True,allOtherManifestFieldsUnchanged=True,rootLiveExportsActuallyInspected=8,installationIndependentlyVerified=True)
 save(out/'ROOT-READBACK.json',result)
 module('north_independent_readback_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(out.name,'independent-complete-original-pair-installed-readback',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
