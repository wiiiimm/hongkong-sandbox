"""Additive publisher: retain every source guard and require complete native proof."""
import selected_original_native_addition_qualified_stage_v1_20261025 as stage
import selected_original_supported_guarded_publish_v4_20261025 as base
from original_native_addition_contract_v1_20261025 import verify as verify_addition
from original_retained_own_views_contract_v1_20261025 import verify as verify_views
stage.SOURCES=stage.read(stage.DOC/'qualification.json')['sourceSHA256ByUid']
base.stage=stage
ROOT=stage.ROOT;HERE=stage.HERE;BASE=stage.BASE
BATCH=base.BATCH;BROWSER=base.BROWSER;REVIEW=base.REVIEW;check=base.check
original_evidence=base.evidence

def evidence():
 keys=original_evidence()
 q=stage.read(stage.DOC/'qualification.json')
 assert q['qualifiedNativeTerrainAddition'] and q['installedMetadataChanges']is False
 assert q['nativeAdditionProof']==stage.ref(BASE/stage.CONFIG['nativeAdditionProof']/'summary.json')
 retained=q['retainedNativeEntries'];assert set(retained)==set(stage.CONFIG['retainedNativeUids'])
 manifest=ROOT/'3d-viewer/city/data/manifest.json'
 current={m['uid']:(m,(ROOT/'3d-viewer'/url).parent/m['asset'])for url in stage.read(manifest)['officialModelCatalogues']for m in stage.read(ROOT/'3d-viewer'/url)['models']}
 for uid,entry in retained.items():
  old,asset=current[uid];assert old==entry and stage.ref(asset)['sha256']==entry['sha256']
 scope=stage.read(BASE/stage.CONFIG['terrainScope']/'scope.json')
 model_scope=stage.read(BASE/stage.CONFIG['scope']/'summary.json')
 model_forms={}
 for row in model_scope['rows']:
  for item in stage.read(BASE/stage.CONFIG['scope']/(row['uid'].split('/')[1]+'-forms.json.gz')):
   f=item['building'];assert f['uid']not in model_forms or model_forms[f['uid']]==f;model_forms[f['uid']]=f
 forms=verify_addition(model_forms,stage.read(BASE/stage.CONFIG['terrainScope']/'form-obligations.json.gz'),scope,model_scope,stage.read(BASE/stage.CONFIG['nativeRegression']/'summary.json'),retained,sources=stage.SOURCES,terrain_targets=stage.CONFIG['terrainTargetUids'],native_count=stage.CONFIG['currentNativeActors'],expected_count=stage.CONFIG['neighbourForms'])
 assert {('building:'if u.startswith('landsd/')else'source-form:')+u for u in forms}<=keys
 images=q['retainedImagesActuallyViewed']
 assert len(images)==4*len(retained) and len({i['path']for i in images})==len(images)
 assert {(i['uid'],i['width'],i['time'])for i in images}=={(u,w,t)for u in retained for w in [390,1280]for t in ['15:00','22:00']}
 for i in images:
  assert set(i)=={'uid','width','time','path','sha256'};check(dict(path=i['path'],sha256=i['sha256']))
 for report in q['browserReports']:
  r=stage.read(ROOT/report['path']);views=r['retainedNativeOwnViews']
  assert views
  width=views[0]['width'];assert width in [390,1280]
  assert verify_views(views,retained,widths=(width,))
  for v in views:
   expected=str(((ROOT/report['path']).parent/v['file']).resolve().relative_to(ROOT))
   assert len([i for i in images if i['path']==expected and (i['uid'],i['width'],i['time'])==(v['uid'],v['width'],v['time'])])==1
 plan=stage.read(stage.STAGE/'plan.json');new=plan['topLevelTerrainPatches'][0]
 assert not new.get('replaces') and not new.get('nativeReview') and not plan.get('dependencyReviews') and not plan.get('catalogueUpdates')
 cfg=stage.read(stage.STAGE/'live-browser-config.json');assert set(cfg['additionalRetainedUids'])==set(retained)
 return keys

base.evidence=evidence
assert_publication_idle=base.assert_publication_idle
main=base.main
if __name__=='__main__':main()
