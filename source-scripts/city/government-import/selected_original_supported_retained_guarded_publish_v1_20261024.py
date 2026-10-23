"""Lease-fenced publication of the fully reviewed standalone original source(s)."""
import argparse,copy,json,sys
from pathlib import Path
from contextlib import contextmanager
import selected_original_supported_retained_qualified_stage_v1_20261024 as stage
from run import connect,reservations,dict_row
ROOT=stage.ROOT;HERE=stage.HERE;BASE=stage.BASE
BATCH=stage.CONFIG['prefix']+'-supported-retained-original-installed-v1-'+stage.CONFIG['date']
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
 assert len(q['imagesActuallyViewed'])==4*len(stage.SOURCES)
 for image in q['imagesActuallyViewed']:check(image)
 sources=stage.SOURCES;assert sources==stage.CONFIG['sources']
 for report in q['browserReports']:
  check(report);r=stage.read(ROOT/report['path']);assert r['passed']and not r['errors'];views=[v for v in r['views']if 'time'in v];assert len(views)==2*len(sources)
  for v in views:assert v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==sources[v['uid']]
  assert r['jointViews']and all({m['uid']:m['sourceSHA256']for m in j['models']}==sources and all(m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])for j in r['jointViews'])
 physical=stage.read(REVIEW/'ROOT-PHYSICAL-REVIEW.json');assert physical['sourceSpecificPhysicalInterpretationAccepted']and physical['sourceSHA256ByUid']==sources
 assert physical['completeFourWorldFoundations'] and physical['completeCurrentNeighbourChecks']==stage.CONFIG['neighbourForms']
 retained=set(physical['retainedNativeUids'])
 native=stage.read(BASE/stage.CONFIG['nativeNeighbours']/'summary.json')
 assert retained and retained==set(native['requiredNativeUids'])==set(native['nativeResolved'])
 assert stage.verify_support_scope(stage.read(stage.PREVIOUS/'catalogue.json')['models'],sources,physical['supportByUid'])
 assert set(stage.read(stage.STAGE/'live-browser-config.json')['additionalRetainedUids'])==retained
 current={m['uid']:m for url in stage.read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues'] for m in stage.read(ROOT/'3d-viewer'/url)['models']}
 for report in q['browserReports']:
  r=stage.read(ROOT/report['path']);views=r['retainedNativeOwnViews']
  assert {(v['uid'],v['time']) for v in views}=={(uid,time) for uid in retained for time in ['15:00','22:00']} and len(views)==2*len(retained)
  for v in views:
   assert v['active'] and v['visible'] and v['fullyFramed'] and not v['fallbackFaces']
   assert v['sourceSHA256']==current[v['uid']]['sha256'] and v['originalTriangles']==current[v['uid']]['triangles']
   assert all(v['meshVisibility']) and not any(v['wireframeFlags'])

 assert all(physical['identityProof'][k] for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted'])
 approved=stage.read(stage.STAGE/'catalogue.json');original=stage.read(stage.PREVIOUS/'catalogue.json');stripped=copy.deepcopy(approved)
 fields=['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved','sourceIdentityReview','sourceFunctionalApplicability','aiGeometryModelling','sourceEvidenceInterpretationUsedAI','placementReview']
 for model,old in zip(stripped['models'],original['models']):
  for key in fields:
   if key in old:model[key]=old[key]
   else:model.pop(key,None)
 assert stripped==original,'Published rendering metadata differs from the tested original catalogue'
 plan=stage.read(stage.STAGE/'plan.json');assert len(plan['areas'])==len(plan['topLevelTerrainPatches'])==1
 new=plan['topLevelTerrainPatches'][0];old=stage.read(stage.PREVIOUS/'browser-config-390.json')['terrain'][0];assert new['sha256']==old['sha256']and new['resolution']==old['resolution'];check(dict(path=new['source'],sha256=new['sha256']));check(dict(path=old['source'],sha256=old['sha256']))
 replacement=stage.read(BASE/stage.CONFIG['patch']/'result.json')['candidate']['replaces'];assert new['replaces']==old['replaces']==replacement
 oldpath=ROOT/'3d-viewer'/replacement['url'];check(dict(path=str(oldpath.relative_to(ROOT)),sha256=replacement['sha256']))
 assert set(stage.read(oldpath)['meta']['targetUids'])==set(replacement['retainedUids'])
 check(new['nativeReview']);decision=stage.read(ROOT/new['nativeReview']['path']);assert decision['supersededURL']==replacement['url'] and decision['supersededSHA256']==replacement['sha256']
 assert decision['replacementSHA256']==new['sha256'] and set(decision['retainedUids'])==set(replacement['retainedUids'])
 check(decision['fullMeshCheck']);mesh=stage.read(ROOT/decision['fullMeshCheck']['path']);assert {r['uid'] for r in mesh['rows']}==retained and all(r['passed'] for r in mesh['rows'])
 assert len(q['retainedImagesActuallyViewed'])==4*len(retained)and len(q['dependencyFailureImagesActuallyViewed'])==1
 for image in q['retainedImagesActuallyViewed']+q['dependencyFailureImagesActuallyViewed']:check(image)
 update=physical['installedSupportUpdate'];assert q['installedSupportUpdate']==update and update['changedFields']==['supportDependencies']
 assert current[update['ownerUid']]==update['beforeEntry']
 expected=copy.deepcopy(update['beforeEntry']);expected['supportDependencies']=update['afterEntry']['supportDependencies'];assert expected==update['afterEntry']
 entries=plan['dependencyReviews'];assert len(entries)==1;depentry=entries[0];check(dict(path=depentry['path'],sha256=depentry['sha256']));check(depentry['visualApproval']);assert depentry['visualApproval']==stage.ref(stage.SOURCE/'ROOT-SOURCE-REVIEW.json')
 dep=stage.read(ROOT/depentry['path']);contact=BASE/stage.CONFIG['supportContacts']/'summary.json';assert dep['contactReport']==str(contact.relative_to(ROOT))and dep['contactReportSHA256']==stage.ref(contact)['sha256']
 oldpath=ROOT/'3d-viewer'/update['url'];assert dep['catalogues']==[dict(source=str(oldpath.relative_to(ROOT)),url=update['url'],oldSHA256=update['beforeSHA256'],models=[update['ownerUid']])]
 assert dep['changes']==[dict(catalogue=str(oldpath.relative_to(ROOT)),uid=expected['uid'],modelSHA256=expected['sha256'],modelId=expected['modelId'],buildingCSUID=expected['buildingCSUID'],oldSupportDependencies=update['beforeEntry']['supportDependencies'],supportDependencies=expected['supportDependencies'])]
 assert dep['requiresNewNativeUids']==sorted(d['uid']for d in expected['supportDependencies'])
 for report in q['browserReports']:
  r=stage.read(ROOT/report['path'])
  if r.get('retainedDependencyFallbackViews'):
   assert len(r['retainedDependencyFallbackViews'])==1
   v=r['retainedDependencyFallbackViews'][0];assert v['uid']==expected['uid']and v['sourceSHA256']==expected['sha256']and v['basicLoaded']and not v['basicHidden']and not v['active']and v['fallbackFaces']>0 and not v['loadingTravel']and not v['travelling']
   assert v['failedParents']==dep['requiresNewNativeUids']and v['supportDependencies']==expected['supportDependencies']
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
 pub=stage.module('selected_original_guarded_publisher',HERE.parent/'island-detail-integration/publish.py');pub.PUBLICATION_GUARD=guard;pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/a.phase;sys.argv=['publish.py',a.plan]+(['--apply']if a.apply else[]);pub.main()
if __name__=='__main__':main()
