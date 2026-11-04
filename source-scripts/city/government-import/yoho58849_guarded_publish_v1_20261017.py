"""Guarded exact original Yoho publication, no terrain edits."""
import argparse,json,sys
from pathlib import Path
from contextlib import contextmanager
import yoho58849_qualified_stage_v1_20261017 as stage
from run import connect,reservations,dict_row
from fixed_xl_source_binding import resolve_uid
ROOT=stage.ROOT;HERE=stage.HERE;BASE=stage.BASE;BATCH='government-xl-yoho58849-original-installed-v1-20261017';BROWSER=stage.folder('private-browser-v1');REVIEW=stage.folder('source-review-v1');check=stage.check

def inventory_delta(previous,models,*,manifest_sha,snapshot):
 assert previous['manifestSHA256']==manifest_sha and previous['snapshotId']==snapshot
 assert len(previous['rows'])==len({r['sourceKey']for r in previous['rows']})==previous['counts']['total']==521
 assert {m['uid']:m['sha256']for m in models}==stage.SOURCES and len(models)==1
 keys={m['originalSourceKey']for m in models};matched=[r for r in previous['rows']if r['sourceKey']in keys];assert len(matched)==1 and not matched[0]['installedVerified'];uids=[resolve_uid(r,models)for r in matched];assert uids==[stage.UID]
 return dict(returnedModels=1,fixedXLTotal=521,newFixedXLUids=uids,newFixedXLSourceKeys=[r['sourceKey']for r in matched],expectedFixedXLDelta=1,previousInstalled=previous['counts']['installedVerified'])
def evidence():
 r=stage.read(stage.DOC/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={}
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e;pins[e['path']]=e
 for e in pins.values():check(e)
 q=stage.read(stage.DOC/'qualification.json');assert q['privateStageQualified']and q['sourceSHA256ByUid']==stage.SOURCES and q['noTerrainChange'];check(q['currentManifest'])
 review=stage.read(REVIEW/'ROOT-SOURCE-REVIEW.json');assert review['originalSourceReviewAccepted']and review['policyReasons']==[]
 for p in review['inspectedImages']:check(p)
 models=stage.read(stage.STAGE/'catalogue.json')['models'];assert {m['uid']:m['sha256']for m in models}==stage.SOURCES
 for m in models:
  assert all(m.get(k)is True for k in ['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved']);assert m['proceduralWindows']is False and not m.get('suppressesBuildingUids')and not m.get('supportDependencies')
 report=stage.read(BROWSER/'staged-browser.json');assert report['passed']and not report['errors']and len([v for v in report['views']if 'time'in v])==4
 failures=[v for v in report['views']if v.get('phase')=='failed-download'];assert len(failures)==1 and failures[0]['fallbackRetained']
 assert not stage.read(stage.STAGE/'plan.json').get('topLevelTerrainPatches')
 return {'building:'+stage.UID}|{'building:'+r['uid']for r in q['retainedNeighbours']}
def assert_publication_idle():check(stage.read(stage.DOC/'qualification.json')['currentManifest'])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('plan');ap.add_argument('--receipt',required=True);ap.add_argument('--phase',required=True);ap.add_argument('--apply',action='store_true');a=ap.parse_args();assert a.phase==BATCH and(ROOT/a.plan).resolve()==stage.STAGE/'plan.json';keys=evidence();lease=json.loads(Path(a.receipt).read_text())
 @contextmanager
 def guard():
  with connect()as db:
   db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));live=reservations._current(db,lease);assert live and keys<=set(live['resources']);assert_publication_idle();yield
 with guard():pass
 pub=stage.module('yoho_atomic_publisher',HERE.parent/'island-detail-integration/publish.py');pub.PUBLICATION_GUARD=guard;pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/a.phase;sys.argv=['publish.py',a.plan]+(['--apply']if a.apply else[]);pub.main()
if __name__=='__main__':main()
