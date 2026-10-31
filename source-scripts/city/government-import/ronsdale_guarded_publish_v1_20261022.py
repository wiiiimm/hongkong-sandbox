"""Lease-fenced publication of the fully reviewed Ronsdale original assembly."""
import argparse,copy,json,sys
from pathlib import Path
from contextlib import contextmanager
import ronsdale_qualified_stage_v1_20261022 as stage
from run import connect,reservations,dict_row
ROOT=stage.ROOT;HERE=stage.HERE;BASE=stage.BASE
BATCH='government-xl-ronsdale-original-installed-v1-20261022'
BROWSER=BASE/'government-xl-ronsdale-three-staged-browser-v2-20261022';REVIEW=BASE/'government-xl-ronsdale-three-source-acceptance-v1-20261022'
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
 assert len(q['imagesActuallyViewed'])==12
 for image in q['imagesActuallyViewed']:check(image)
 sources=stage.SOURCES;assert set(sources)=={'landsd/233771:0','landsd/256898:0','landsd/256702:0'}
 for report in q['browserReports']:
  check(report);r=stage.read(ROOT/report['path']);assert r['passed']and not r['errors'];views=[v for v in r['views']if 'time'in v];assert len(views)==6
  for v in views:assert v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==sources[v['uid']]
  assert r['jointViews']and all({m['uid']:m['sourceSHA256']for m in j['models']}==sources and all(m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])for j in r['jointViews'])
 physical=stage.read(REVIEW/'ROOT-PHYSICAL-REVIEW.json');assert physical['sourceSpecificPhysicalInterpretationAccepted']and physical['completeNeighbourInterpretationAccepted']and physical['sourceSHA256ByUid']==sources
 assert len(physical['accounts'])==2 and all(r['remainingUninterpretedWarnings']==0 for r in physical['accounts'])
 approved=stage.read(stage.STAGE/'catalogue.json');original=stage.read(stage.PREVIOUS/'catalogue.json');stripped=copy.deepcopy(approved)
 fields=['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved','sourceIdentityReview','sourceFunctionalApplicability','aiGeometryModelling','sourceEvidenceInterpretationUsedAI','placementReview']
 for model,old in zip(stripped['models'],original['models']):
  for key in fields:
   if key in old:model[key]=old[key]
   else:model.pop(key,None)
 assert stripped==original,'Published rendering metadata differs from the tested original catalogue'
 plan=stage.read(stage.STAGE/'plan.json');assert len(plan['areas'])==len(plan['topLevelTerrainPatches'])==1
 new=plan['topLevelTerrainPatches'][0];old=stage.read(stage.PREVIOUS/'browser-config-390.json')['terrain'][0];assert new['sha256']==old['sha256']and new['resolution']==old['resolution'];check(dict(path=new['source'],sha256=new['sha256']));check(dict(path=old['source'],sha256=old['sha256']))
 update=stage.read(stage.STAGE/'estimated-bases.json')['buildings'];assert len(update)==1 and update[0]['uid']=='landsd/307560:0'
 return set(q['leaseResources'])
def assert_publication_idle():assert stage.read(stage.DOC/'qualification.json')['currentManifest']==stage.ref(ROOT/'3d-viewer/city/data/manifest.json')
def main():
 p=argparse.ArgumentParser();p.add_argument('plan');p.add_argument('--receipt',required=True);p.add_argument('--phase',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args();assert a.phase==BATCH and(ROOT/a.plan).resolve()==stage.STAGE/'plan.json';keys=evidence();lease=json.loads(Path(a.receipt).read_text())
 @contextmanager
 def guard():
  with connect()as db:
   db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));live=reservations._current(db,lease);assert live and keys<=set(live['resources']);assert_publication_idle();yield
 with guard():pass
 pub=stage.module('ronsdale_guarded_publisher',HERE.parent/'island-detail-integration/publish.py');pub.PUBLICATION_GUARD=guard;pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/a.phase;sys.argv=['publish.py',a.plan]+(['--apply']if a.apply else[]);pub.main()
if __name__=='__main__':main()
