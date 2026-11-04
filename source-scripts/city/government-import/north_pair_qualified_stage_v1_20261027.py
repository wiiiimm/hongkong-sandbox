"""Stage exact two originals/three terrain members/one availability annotation.

Dry run only. Canonical publication, native-terrain, dependency and rollback
guards are preserved through the existing exact North pair hooks.
"""
import copy,shutil,sys
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from west_kowloon_pair_physical_review_v1_20261027 import P,SOURCES
from original_independent_atomic_contract_v1_20261027 import verify_existing_atomic_group,triple_layout
from north_pair_publisher_hooks_v1_20261027 import install
BASE=ROOT/'docs/astra-city/government-import';BATCH=P+'qualified-stage-v2-20261027';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not STAGE.exists();refs=[Path(__file__)];pins={}
 def receipt(suffix):
  name=P+suffix+'-20261027'
  if name not in pins:pins[name]=authenticate(BASE/name)[1];refs.append(BASE/name/'result.json')
  return name
 def take(suffix,path=None):
  name=receipt(suffix);path=path or BASE/name/'summary.json'
  assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 physical=take('physical-source-review-v1');visual=take('visual-qualification-v1');surface=take('three-member-surface-v2');terrain=take('retained-terrain-review-v2');identity=take('identity-revalidated-v1')
 assert physical['physicalAcceptance']and visual['visualAcceptance']and identity['identityAccepted']and terrain['proposalTerrainNonRegressionPassed']
 assert all(r['sourceSHA256ByUid']==SOURCES for r in [physical,visual,surface,terrain,identity])
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=ref(manifest);refs.append(manifest)
 assert before==surface['currentManifest']and before['sha256']==visual['currentManifestSHA256']
 originals={r['uid']:r['candidate']['entry']for r in take('three-member-runtime-v2',BASE/(P+'three-member-runtime-v2-20261027')/'selection.json.gz')['rows']}
 prior=HERE/'local'/(P+'full-existing-peer-browser-v2-20261027')
 cat=take('desktop-complete-mobile-held-v1',prior/'catalogue.json');cfg=take('desktop-complete-mobile-held-v1',prior/'config-1280.json');forms=take('desktop-complete-mobile-held-v1',prior/'source-forms.json')
 assert len(cfg['availabilityOverlays'])==1 and not cfg['catalogueReplacements']and not cfg['failureTestUids']
 overlay=cfg['availabilityOverlays'][0];oldpath=ROOT/'3d-viewer'/overlay['url'];overlaypath=ROOT/overlay['source'];refs.extend([oldpath,overlaypath])
 assert ref(oldpath)['sha256']==overlay['beforeSHA256']and ref(overlaypath)['sha256']==overlay['afterSHA256']
 old=next(m for m in read(oldpath)['models']if m['uid']==overlay['uid']);new=next(m for m in read(overlaypath)['models']if m['uid']==overlay['uid'])
 verify_existing_atomic_group(cat['models'],SOURCES,originals,dict.fromkeys(SOURCES),{old['uid']:old},{new['uid']:new})
 current=[m for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']]
 assert len(current)==len({m['uid']for m in current})==6989 and not set(SOURCES)&{m['uid']for m in current}
 qualification=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,visualAcceptance=True,privateStageQualified=True,sourceGeometryChanges=0,sourcePoseChanges=0,existingNativeReaccepted=False,publication=False)
 save(DOC/'qualification.json',qualification)
 for m in cat['models']:
  asset=prior/m['asset'];assert ref(asset)['sha256']==SOURCES[m['uid']]and asset.stat().st_size==m['bytes'];refs.append(asset)
  dest=STAGE/m['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset,dest)
  m.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,sourceIdentityReview=ref(BASE/(P+'identity-revalidated-v1-20261027')/'summary.json'),sourceFunctionalApplicability=ref(DOC/'qualification.json'),aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,placementReview=BATCH)
 verify_existing_atomic_group(cat['models'],SOURCES,originals,dict.fromkeys(SOURCES),{old['uid']:old},{new['uid']:new})
 save(STAGE/'catalogue.json',cat);save(STAGE/'source-forms.json',forms);save(STAGE/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']))
 tested=copy.deepcopy(cfg['terrain']);assert len(tested)==3
 for e in tested:
  e['sha256']=digest((ROOT/e['source']).read_bytes())
 entries=copy.deepcopy(tested)
 for m in surface['members']:
  e=next(e for e in entries if e['source']==m['candidate']['path']);assert e['sha256']==m['candidate']['sha256']and e['replaces']==m['replaces']
  e['destination']='city/data/government-native-north-pair-'+m['member']+'-v1-20261027.json';e['area']='West Kowloon North pair original terrain'
  r=next(r for r in terrain['members']if r['member']==m['member']);path=ROOT/r['path'];assert ref(path)['sha256']==r['sha256'];refs.append(path);e['nativeReview']=ref(path)
 triple_layout(tested,entries,[m['replaces']for m in surface['members']])
 destination='city/data/official-models/'+BATCH+'/catalogue.json';plan=dict(areas=[dict(area='West Kowloon original North pair',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=entries)
 save(STAGE/'plan.json',plan);cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',catalogueURL=destination,terrain=entries);save(STAGE/'live-browser-config.json',cfg)
 pub=module('north_exact_qualified_publisher',HERE.parent/'island-detail-integration/publish.py');install(pub,ROOT,surface,overlay,originals);pub.DOC=DOC/'publisher-dry-run';oldargv=sys.argv[:]
 try:sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main()
 finally:sys.argv=oldargv
 assert read(pub.DOC/'publication-plan.json')['published']is False and ref(manifest)==before
 for name,group in pins.items():
  for path in refs:
   relative=str(path.relative_to(ROOT))
   if relative in group:assert digest(path.read_bytes())==group[relative]
 refs.extend([HERE/'north_pair_publisher_hooks_v1_20261027.py',HERE/'original_independent_atomic_contract_v1_20261027.py',HERE/'original_availability_overlay_v1_20261027.py',HERE.parent/'island-detail-integration/publish.py'])
 refs.extend(p for p in STAGE.rglob('*')if p.is_file())
 module('north_exact_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-independent-originals-three-member-terrain-availability-plan',list(dict.fromkeys(refs)),dict(**qualification,qualifiedForLiveVerification=True,newVisibleModels=2,previousNativeActors=6989,newRuntimeCount=6991,expectedFixedXLDelta=1))
if __name__=='__main__':main()
