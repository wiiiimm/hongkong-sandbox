"""Lease-fenced publication of the exact reviewed atomic Tung Cheong pair.

Preserves the original v7 evidence/byte/retention/transaction guards. Reads the
actual compound review schema, every inspected export and per-peer lifecycle.
No individual identity threshold, geometry or original source matching is edited.
"""
import argparse,copy,json,sys
from pathlib import Path
from contextlib import contextmanager
import tung_cheong_atomic_retained_qualified_stage_v1_20261104 as stage
from exact_single_terrain_replacement_v1_20261102 import replacement as canonical_replacement
from fuying_five_member_terrain_stage_v1_20261029 import complete_boundary_validators
from run import connect,reservations,dict_row
ROOT=stage.ROOT;HERE=stage.HERE;BASE=stage.BASE
BATCH=stage.CONFIG['prefix']+'-original-installed-v1-'+stage.CONFIG['date']
BROWSER=BASE/stage.CONFIG['browser'];REVIEW=BASE/stage.CONFIG['physical']
stage.SOURCES=stage.read(stage.DOC/'qualification.json')['sourceSHA256ByUid']
def check(q):assert stage.ref(ROOT/q['path'])==q,q['path']
def evidence():
 pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [stage.DOC,BROWSER,stage.SOURCE,REVIEW]:
   r=stage.read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   for q in r['evidenceRefs']:
    assert q['path']not in pins or pins[q['path']]==q;pins[q['path']]=q
 for q in pins.values():check(q)
 q=stage.read(stage.DOC/'qualification.json');assert q['privateStageQualified']and q['originalSourceReviewAccepted']and q['visualAcceptance'];assert q['currentManifest']==stage.ref(ROOT/'3d-viewer/city/data/manifest.json')
 observations=stage.read(REVIEW/'ROOT-EXPORT-OBSERVATIONS.json');assert observations['visualAcceptance']is True and len(observations['imagesActuallyViewed'])==47
 assert str((REVIEW/'ROOT-EXPORT-OBSERVATIONS.json').relative_to(ROOT))in pins
 for image in observations['imagesActuallyViewed']:check({k:image[k]for k in ['path','sha256']})
 reports=[stage.ref(BROWSER/str(width)/'staged-browser.json')for width in [1280,390]]
 for report in reports:assert pins[report['path']]==report
 sources=stage.SOURCES;assert sources==stage.CONFIG['sources']
 for report in reports:
  check(report);r=stage.read(ROOT/report['path']);assert r['passed']and not r['errors'];views=[v for v in r['views']if 'time'in v];assert len(views)==2*len(sources)
  for v in views:assert v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==sources[v['uid']]
  assert r['jointViews']and all({m['uid']:m['sourceSHA256']for m in j['models']}==sources and all(m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])for j in r['jointViews'])
 physical=stage.read(REVIEW/'ROOT-PHYSICAL-REVIEW.json');assert physical['sourceSpecificPhysicalInterpretationAccepted']and physical['sourceSHA256ByUid']==sources
 assert physical['requiredOriginalAssembly']==sources and physical['activationGroupRequired']and physical['standaloneLowSourceIdentityAccepted']is False
 assert physical['retainedNativeRegression']['forms']==stage.CONFIG['neighbourForms']==40
 assert physical['terrainGroundOwnerUids']==['landsd/53799:0']and physical['unchangedSurfaceCompanionUids']==['landsd/223636:0']
 context_path=BASE/'government-xl-tung-cheong-atomic-identity-context-v1-20261104/summary.json'
 context_receipt=stage.read(context_path.parent/'result.json');assert any(r['path']==str(context_path.relative_to(ROOT))and r['sha256']==stage.ref(context_path)['sha256']for r in context_receipt['evidenceRefs'])
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(context_receipt['jobId'],)).fetchone()==('complete',context_receipt)
 context=stage.read(context_path);assert context['targetUnionCoveredByOriginals']>=.95 and context['completeProjectionCoveredByTenMetreTargetBuffer']and not context['foreignExcessOverlaps']
 assert all(c['targetUnionCoversWholeCell']and c['sourceUnionCellCoverage']['coversWholeCell']for c in context['compoundGeographicCells'])
 retained=set(physical['retainedNativeRegression']['requiredNativeUids'])
 assert retained and retained==set(physical['retainedNativeRegression']['nativeResolved'])
 assert set(stage.read(stage.STAGE/'live-browser-config.json')['additionalRetainedUids'])==retained
 current={m['uid']:m for url in stage.read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues'] for m in stage.read(ROOT/'3d-viewer'/url)['models']}
 for report in reports:
  r=stage.read(ROOT/report['path']);views=r['retainedNativeOwnViews']
  assert {(v['uid'],v['time']) for v in views}=={(uid,time) for uid in retained for time in ['15:00','22:00']} and len(views)==2*len(retained)
  for v in views:
   assert v['active'] and v['visible'] and v['fullyFramed'] and not v['fallbackFaces']
   assert v['sourceSHA256']==current[v['uid']]['sha256'] and v['originalTriangles']==current[v['uid']]['triangles']
   assert all(v['meshVisibility']) and not any(v['wireframeFlags'])

 assert physical['compoundIdentityAccepted']and physical['identityAccepted']and physical['nativeMatchingRowsChanged']==0 and physical['nativeLowViewerUid']is None
 assert {a['uid']:a['sourceSHA256']for a in context['accounts']}==sources
 assert all(a['completeNamedGraphVerified']and a['uniqueCurrentGeoRef']for a in context['accounts'])
 lifecycle_path=BROWSER/'atomic-lifecycle/report.json';assert pins[str(lifecycle_path.relative_to(ROOT))]==stage.ref(lifecycle_path)
 lifecycle=stage.read(lifecycle_path);assert lifecycle['passed']and not lifecycle['pageErrors']and len(lifecycle['cases'])==3
 assert {c['failedUid']for c in lifecycle['cases']if c['width']==390}==set(sources)
 assert all(c['baseOnlyRestoredCompleteGroup']and c['completeGroupEvicted']and not c['audit']['violations']for c in lifecycle['cases'])
 assert all(c['failureKeptAllBasics']for c in lifecycle['cases']if c['width']==390)
 approved=stage.read(stage.STAGE/'catalogue.json');original=stage.read(stage.PREVIOUS/'catalogue.json');stripped=copy.deepcopy(approved)
 fields=['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved','sourceIdentityReview','sourceFunctionalApplicability','aiGeometryModelling','sourceEvidenceInterpretationUsedAI','placementReview']
 for model,old in zip(stripped['models'],original['models']):
  for key in fields:
   if key in old:model[key]=old[key]
   else:model.pop(key,None)
 assert stripped==original,'Published rendering metadata differs from the tested original catalogue'
 plan=stage.read(stage.STAGE/'plan.json');assert len(plan['areas'])==len(plan['topLevelTerrainPatches'])==1
 new=plan['topLevelTerrainPatches'][0];old=stage.read(stage.PREVIOUS/'browser-config-390.json')['terrain'][0];assert new['sha256']==old['sha256']and new['resolution']==old['resolution'];check(dict(path=new['source'],sha256=new['sha256']));check(dict(path=old['source'],sha256=old['sha256']))
 replacement=physical['exactTerrainReplacement'];assert new['replaces']==canonical_replacement(old)==replacement
 assert set(stage.read(ROOT/new['source'])['meta']['targetUids'])==set(replacement['retainedUids'])|{'landsd/53799:0'}
 oldpath=ROOT/'3d-viewer'/replacement['url'];check(dict(path=str(oldpath.relative_to(ROOT)),sha256=replacement['sha256']))
 assert set(stage.read(oldpath)['meta']['targetUids'])==set(replacement['retainedUids'])
 check(new['nativeReview']);decision=stage.read(ROOT/new['nativeReview']['path']);assert decision['supersededURL']==replacement['url'] and decision['supersededSHA256']==replacement['sha256']
 assert decision['replacementSHA256']==new['sha256'] and set(decision['retainedUids'])==set(replacement['retainedUids'])
 check(decision['fullMeshCheck']);mesh=stage.read(ROOT/decision['fullMeshCheck']['path']);assert {r['uid'] for r in mesh['rows']}==retained and all(r['passed'] for r in mesh['rows'])
 assert not any(a.get('estimates')for a in plan['areas']) and not(stage.STAGE/'estimated-bases.json').exists()
 return set(q['leaseResources'])
def assert_publication_idle():assert stage.read(stage.DOC/'qualification.json')['currentManifest']==stage.ref(ROOT/'3d-viewer/city/data/manifest.json')
def main():
 p=argparse.ArgumentParser();p.add_argument('plan');p.add_argument('--receipt',required=True);p.add_argument('--phase',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args();assert a.phase==BATCH and(ROOT/a.plan).resolve()==stage.STAGE/'plan.json';keys=evidence();lease=json.loads(Path(a.receipt).read_text())
 @contextmanager
 def guard():
  with connect()as db:
   db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));live=reservations._current(db,lease);assert live and keys<=set(live['resources']);assert_publication_idle();yield
 with guard():pass
 pub=stage.module('selected_original_guarded_publisher',HERE.parent/'island-detail-integration/publish.py');pub.PUBLICATION_GUARD=guard;pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/a.phase;sys.argv=['publish.py',a.plan]+(['--apply']if a.apply else[])
 with complete_boundary_validators():pub.main()
if __name__=='__main__':main()
