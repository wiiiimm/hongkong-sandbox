"""Lease-fenced publication of the fully reviewed standalone original source(s)."""
import argparse,copy,json,sys
from pathlib import Path
from contextlib import contextmanager
import pok_oi_original_stage_v1_20261026 as stage
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
 assert len(q['imagesActuallyViewed'])==4*len(stage.SOURCES)
 for image in q['imagesActuallyViewed']:check(image)
 sources=stage.SOURCES;assert sources==stage.CONFIG['sources']
 for report in q['browserReports']:
  check(report);r=stage.read(ROOT/report['path']);assert r['passed']and not r['errors'];views=[v for v in r['views']if 'time'in v];assert len(views)==2*len(sources)
  for v in views:assert v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==sources[v['uid']]
  assert r['jointViews'] and all(j['models'] and all(m['uid']in sources and m['sourceSHA256']==sources[m['uid']] and m['active'] and m['visible'] and not m['fallbackFaces'] for m in j['models']) for j in r['jointViews'])
  assert q['retainedBasicSupportDependencies']==[] and q['retainedNativeEntries']=={}
  assert all(v['retained']=={} and v['nativeSupports']=={} for v in views)
  assert r.get('retainedNativeOwnViews',[])==[]
 physical=stage.read(REVIEW/'ROOT-PHYSICAL-REVIEW.json');assert physical['sourceSpecificPhysicalInterpretationAccepted']and physical['sourceSHA256ByUid']==sources
 assert physical['completeFourWorldSourceClearance'] and physical['completeCurrentNeighbourChecks']==stage.CONFIG['neighbourForms']
 from pok_oi_original_admission_v1_20261026 import replay
 for path in replay(stage.CONFIG,physical):assert str(path.relative_to(ROOT))in pins and stage.ref(path)==pins[str(path.relative_to(ROOT))]
 assert all(physical['identityProof'][k] for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted'])
 approved=stage.read(stage.STAGE/'catalogue.json');original=stage.read(stage.PREVIOUS/'catalogue.json');stripped=copy.deepcopy(approved)
 fields=['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved','sourceIdentityReview','sourceFunctionalApplicability','aiGeometryModelling','sourceEvidenceInterpretationUsedAI','placementReview','retainedBasicSupportDependencies','supportDependencies']
 for model,old in zip(stripped['models'],original['models']):
  for key in fields:
   if key in old:model[key]=old[key]
   else:model.pop(key,None)
 assert stripped==original,'Published rendering metadata differs from the tested original catalogue'
 assert {m['uid']:m['retainedBasicSupportDependencies'] for m in approved['models']}=={uid:[d for d in physical['retainedBasicSupportDependencies'] if d['uid']==uid] for uid in sources}
 for model in approved['models']:
  assert model['supportDependencies']==stage.expected_dependencies(model['uid'],physical)
 plan=stage.read(stage.STAGE/'plan.json');assert len(plan['areas'])==1 and plan['topLevelTerrainPatches']==[]
 assert stage.read(stage.PREVIOUS/'browser-config-390.json')['terrain']==[] and physical['terrainEdits'] is False
 assert not any(a.get('estimates')for a in plan['areas']) and not(stage.STAGE/'estimated-bases.json').exists()
 failurefolder=BASE/'government-xl-pok-oi-peer-dependency-failure-v1-20261026'
 failreceipt,failpins=stage.authenticate(failurefolder)
 assert failreceipt['passed'] and failreceipt['sourceSHA256']==sources['landsd/71329:0'] and failreceipt['parentSHA256']==sources['landsd/213579:0']
 for path,sha in failpins.items():check(dict(path=path,sha256=sha))
 failure=stage.read(failurefolder/'browser.json');assert failure['passed'] and not failure['errors'] and failure['deniedParentRequests']>0 and failure['successfulParentRequests']>0
 failed=failure['failed'];assert failed['parentFailed'] and not failed['active'] and not failed['parentActive'] and failed['basicLoaded'] and not failed['basicHidden'] and not failed['detailSuppressed'] and failed['basicGroupVisible'] and failed['ownFeaturePresent']
 assert failed['dependencies']==stage.expected_dependencies('landsd/71329:0',physical)
 assert {r['uid']:r['sourceSHA256']for r in failure['recovered']}==sources and all(r['active'] and r['visible']for r in failure['recovered'])
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
