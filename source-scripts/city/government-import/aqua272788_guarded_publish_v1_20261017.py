"""Publish only the exact reviewed unchanged Aqua Marine Block 2 source under current evidence and lease."""
import argparse,json,sys
from pathlib import Path
from contextlib import contextmanager
import aqua272788_qualified_stage_v1_20261017 as stage
from run import connect,reservations,dict_row
from fixed_xl_source_binding import resolve_uid
ROOT=stage.ROOT;HERE=stage.HERE;BASE=stage.BASE
BATCH='government-xl-aqua272788-original-installed-v1-20261017';BROWSER=stage.folder('private-browser-v1');REVIEW=stage.folder('current-junction-resolution-v1')
check=stage.check

def inventory_delta(previous,models,*,manifest_sha,snapshot):
 assert previous['manifestSHA256']==manifest_sha and previous['snapshotId']==snapshot
 assert len(previous['rows'])==len({r['sourceKey']for r in previous['rows']})==previous['counts']['total']==521
 matched=[r for r in previous['rows']if r['sourceKey']==models[0]['originalSourceKey']]
 assert len(models)==len(matched)==1 and not matched[0]['installedVerified']
 assert resolve_uid(matched[0],models)==stage.UID
 return {'returnedModels':1,'fixedXLTotal':521,'newFixedXLUids':[stage.UID],'newFixedXLSourceKeys':[matched[0]['sourceKey']],'expectedFixedXLDelta':1,'previousInstalled':previous['counts']['installedVerified']}

def evidence():
 r=stage.read(stage.DOC/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:check(q)
 q=stage.read(stage.DOC/'qualification.json');assert q['privateStageQualified'] and q['uid']==stage.UID and q['sourceSHA256']==stage.SHA;check(q['currentManifest']);check(q['completeFiniteEvidence'])
 review=stage.read(REVIEW/'ROOT-IMAGE-INSPECTION.json');assert review['sourceGeometryAppearanceAccepted']
 assert len(review['reviewedImages'])==4
 for image in review['reviewedImages']:check(image)
 models=stage.read(stage.STAGE/'catalogue.json')['models'];assert len(models)==1 and models[0]['uid']==stage.UID and models[0]['sha256']==stage.SHA and not models[0].get('suppressesBuildingUids')
 assert models[0]['originalSourceKey']==stage.SOURCE_KEY and models[0]['proceduralWindows'] is False
 assert all(models[0].get(k)is True for k in ['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved'])
 report=stage.read(BROWSER/'staged-browser.json');assert report['passed'] and not report['errors']
 assert len([v for v in report['views']if 'time'in v])==4
 failed=[v for v in report['views']if v.get('phase')=='failed-download'];assert len(failed)==1 and failed[0]['fallbackRetained']
 resolution=stage.read(REVIEW/'resolution.json');assert resolution['sourceSpecificJunctionAccepted'] and not resolution['remainingSourceSpecificReasons']
 finite=stage.read(stage.folder('four-world-junction-v1')/'summary.json');assert finite['allFourModesVerified']
 support=models[0]['supportDependencies'];assert len(support)==1 and support[0]['uid']==stage.PODIUM and support[0]['sha256']==stage.HOST and support[0]['state']=='installed'
 pointer=stage.read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(pointer['snapshotId'],stage.PODIUM)).fetchone()==('installed-verified',stage.HOST)
 neighbours=stage.read(stage.folder('current-physical-v3')/'neighbour-inputs.json.gz')['rows'];uids={r['building']['uid']for r in neighbours}|{stage.UID,stage.PODIUM}
 return {'building:'+uid for uid in uids}

def assert_publication_idle():
 # Global publication mutex and fenced shared leases serialize writes; stale map evidence cannot publish.
 check(stage.read(stage.DOC/'qualification.json')['currentManifest'])

def main():
 ap=argparse.ArgumentParser();ap.add_argument('plan');ap.add_argument('--receipt',required=True);ap.add_argument('--phase',required=True);ap.add_argument('--apply',action='store_true');a=ap.parse_args()
 assert a.phase==BATCH and (ROOT/a.plan).resolve()==stage.STAGE/'plan.json';keys=evidence();lease=json.loads(Path(a.receipt).read_text())
 @contextmanager
 def guard():
  with connect()as db:
   db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));live=reservations._current(db,lease);assert live and keys<=set(live['resources'])
   check(stage.read(stage.DOC/'qualification.json')['currentManifest']);yield
 with guard():pass
 pub=stage.module('aqua272788_unchanged_publisher',HERE.parent/'island-detail-integration/publish.py');pub.PUBLICATION_GUARD=guard;pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/a.phase
 sys.argv=['publish.py',a.plan]+(['--apply']if a.apply else[]);pub.main()
if __name__=='__main__':main()
