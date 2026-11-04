"""Independent installed source, all old actors/assets, fixed XL and support audit."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from peninsula_private_group_roof_contract_v1_20261029 import SOURCES,OWNER,TOWER,ROOF
BASE=ROOT/'docs/astra-city/government-import'
INSTALL='government-xl-peninsula-exact-original-pair-original-installed-v3-20261029'
BATCH='government-xl-peninsula-exact-pair-installed-root-readback-v1-20261029'
IMAGES='government-xl-peninsula-exact-pair-live-image-review-v1-20261029'
def main():
 installed=BASE/INSTALL;out=BASE/BATCH;assert not out.exists()
 receipt,pins=authenticate(installed)
 assert receipt['sourceSHA256ByUid']==SOURCES and receipt['newlyInstalled']==1 and set(receipt['installedUids'])==set(SOURCES)
 assert receipt['fullXLCurrentCounts']==dict(total=521,installedVerified=405,remaining=116)and receipt['completeCurrentCatalogueModels']==7021
 refs=[Path(__file__),installed/'result.json'];verified=0
 runtime_batch=BASE/'government-xl-peninsula-runtime-roof-binding-checkpoint-v1-20261029'
 _,runtime_pins=authenticate(runtime_batch);refs.append(runtime_batch/'result.json');runtime_code=[]
 for name in ['official-models.js','official-model-assets.js','official-model-reviewed-osm-roof.js','streaming.js','app.js','geo.js']:
  path=ROOT/'3d-viewer/city'/name;key=str(path.relative_to(ROOT))
  # geo.js was unchanged and may be absent from the scoped runtime checkpoint.
  if name=='geo.js'and key not in runtime_pins:continue
  assert digest(path.read_bytes())==runtime_pins[key];refs.append(path);runtime_code.append(dict(path=key,sha256=runtime_pins[key]))
 for path,sha in pins.items():
  p=ROOT/path;assert digest(p.read_bytes())==sha,path;refs.append(p);verified+=1
 manifest=ROOT/'3d-viewer/city/data/manifest.json';current=read(manifest)
 original=next(r for r in receipt['historicalMutableByteSnapshots']if r['originalPath']=='3d-viewer/city/data/manifest.json')
 oldpath=ROOT/original['savedHistoricalBytes']['path'];assert digest(oldpath.read_bytes())==original['originalSHA256'];old=read(oldpath)
 def models(data):
  rows=[]
  for url in data['officialModelCatalogues']:
   path=ROOT/'3d-viewer'/url;rows.extend(read(path)['models']);refs.append(path)
  return rows
 before,after=models(old),models(current)
 assert len(before)==len({r['uid']for r in before})==7019
 assert len(after)==len({r['uid']for r in after})==7021
 assert after[:-2]==before and {m['uid']:m['sha256']for m in after[-2:]}==SOURCES
 rows={m['uid']:m for m in after[-2:]};owner=rows[OWNER];tower=rows[TOWER]
 assert owner['triangles']==15114 and tower['triangles']==2872
 for source in rows.values():
  assert all(source[k]is True for k in ['placementReviewed','publicationApproved','identityReviewApproved','sourceIdentityReviewed'])and source['proceduralWindows']is False
  assert source['activationGroup']==sorted(SOURCES)and source.get('verticalPlacementOffsetHKPD',0)==0 and not source.get('retainedBasicSupportDependencies')
 assert not owner.get('supportDependencies')and owner['suppressesBuildingUids']==[ROOF]
 assert tower['supportDependencies']==[dict(uid=OWNER,state='installed',buildingCSUID=owner['buildingCSUID'],sha256=SOURCES[OWNER])]
 assets=0
 for url in current['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url
  for entry in read(path)['models']:
   asset=path.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256'];assets+=1
 assert assets==7021
 previous=BASE/'government-xl-depot120104-coastal-original-installed-v4-20261029/full-xl-current-count.json'
 oldrows={r['sourceKey']:r for r in read(previous)['rows']};newrows={r['sourceKey']:r for r in read(installed/'full-xl-current-count.json')['rows']}
 assert set(oldrows)==set(newrows)and len(newrows)==521
 changed=[r for k,r in newrows.items()if r!=oldrows[k]];assert len(changed)==1 and changed[0]['uid']==OWNER and changed[0]['installedVerified']and changed[0]['runtimeSourceSHA256']==changed[0]['indexedSourceSHA256']==SOURCES[OWNER]
 supportguard=module('peninsula_independent_global_support',HERE.parent/'island-detail-integration/retained_basic_support.py');support={};supportguard.stage_retained_basic_support(ROOT,current,{},support,read)
 assert {('landsd/312858:0','landsd/176739:0'),('landsd/6801:0','landsd/304712:0')}<={(r['uid'],r['supportUid'])for r in support['retainedBasicSupportChecks']}
 image_receipt,image_pins=authenticate(BASE/IMAGES);imagepath=BASE/IMAGES/'ROOT-LIVE-IMAGE-OBSERVATIONS.json';inspection=read(imagepath)
 assert digest(imagepath.read_bytes())==image_pins[str(imagepath.relative_to(ROOT))]and inspection['reviewer']=='ROOT'and inspection['visualAcceptance']
 expected=set()
 for width in [390,1280]:
  folder=installed/('viewport-'+str(width));report=read(folder/'live-browser.json');assert report['passed']and not report['errors']
  views=[v for v in report['views']if 'time'in v];assert len(views)==4
  for v in views:
   assert v['uid']==v['pick']==v['collision']and v['sourceSHA256']==SOURCES[v['uid']]and v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']
   expected.add(str((folder/v['file']).relative_to(ROOT)))
 assert {r['path']for r in inspection['imagesActuallyViewed']}==expected and len(expected)==8
 for q in inspection['imagesActuallyViewed']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']==pins[q['path']]
 atomic=read(installed/'atomic-lifecycle/report.json');assert atomic['passed']and not atomic['pageErrors']and atomic['liveInstalledHTTP']and not atomic['catalogueAndTerrainSubstitution']
 assert {(c['width'],c['failedUid'])for c in atomic['cases']}=={(1280,None),(390,OWNER),(390,TOWER)}
 for c in atomic['cases']:
  assert c['baseOnlyRestoredCompleteGroup']and c['completeGroupEvicted']and not c['audit']['violations']and c['audit']['frames']>0
  for phase in c['canopyLifecycle']:
   active=phase['phase']in ['original-active','auto-restored'];assert phase['ownerActive']is active and phase['basicCanopyVisible']is not active
  if c['failedUid']:assert c['failureKeptAllBasics']
 # No unrelated manifest, terrain, tile or count changes.
 assert {k:v for k,v in old.items()if k!='officialModelCatalogues'}=={k:v for k,v in current.items()if k!='officialModelCatalogues'}
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert read(pointer)['snapshotId']==receipt['snapshotId']
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for uid,sha in SOURCES.items():assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(receipt['snapshotId'],uid)).fetchone()==('installed-verified',sha)
 result=dict(installedRuntimeCodeBindings=runtime_code,uids=sorted(SOURCES),passed=True,installationIndependentlyVerified=True,sourceSHA256ByUid=SOURCES,installedJobId=receipt['jobId'],snapshotId=receipt['snapshotId'],fullXLCurrentCounts=receipt['fullXLCurrentCounts'],completeCurrentCatalogueModels=7021,oldEntriesPreserved=7019,allCurrentAssetsRehashed=assets,verifiedEvidenceFiles=verified,completeFixedXLRowsCompared=521,onlyChangedFixedXLUid=OWNER,liveExportsActuallyViewed=inspection['imagesActuallyViewed'],retainedBasicSupportChecks=support['retainedBasicSupportChecks'],completeAtomicPairAndRoofLifecycleVerified=True,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False)
 save(out/'ROOT-READBACK.json',result);refs.extend([manifest,oldpath,previous,pointer,BASE/IMAGES/'result.json',imagepath,HERE.parent/'island-detail-integration/retained_basic_support.py'])
 module('peninsula_independent_installed_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'installed-Peninsula-pair-independent-whole-xl-assets-unchanged-ground-atomic-roof-readback',list(dict.fromkeys(refs)),result)
 print(dict(passed=True,installedFixedXL=405,actors=7021,sourceGeometryChanges=0),flush=True)
if __name__=='__main__':main()
