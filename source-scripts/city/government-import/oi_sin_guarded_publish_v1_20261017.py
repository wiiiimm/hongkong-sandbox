"""Publish only the exact reviewed Oi Sin assembly under current evidence and leases."""
import argparse,json,sys
from pathlib import Path
from contextlib import contextmanager
import oi_sin_qualified_stage_v2_20261017 as stage
from run import connect,reservations,dict_row
from fixed_xl_source_binding import resolve_uid
ROOT=stage.ROOT;HERE=stage.HERE;BASE=stage.BASE;BATCH='government-xl-oi-sin-original-installed-v1-20261017';BROWSER=stage.folder('four-originals-browser-v4');REVIEW=BROWSER;check=stage.check

def inventory_delta(previous,models,*,manifest_sha,snapshot):
 assert previous['manifestSHA256']==manifest_sha and previous['snapshotId']==snapshot
 assert len(previous['rows'])==len({r['sourceKey']for r in previous['rows']})==previous['counts']['total']==521
 assert {m['uid']:m['sha256']for m in models}==stage.SOURCES
 keys={m['originalSourceKey']for m in models};assert len(keys)==len(models)==4
 matched=[r for r in previous['rows']if r['sourceKey']in keys];assert matched and all(not r['installedVerified']for r in matched)
 uids=[resolve_uid(r,models)for r in matched];assert len(uids)==len(set(uids))and set(uids)<=set(stage.SOURCES)
 return dict(returnedModels=4,fixedXLTotal=521,newFixedXLUids=uids,newFixedXLSourceKeys=[r['sourceKey']for r in matched],expectedFixedXLDelta=len(matched),previousInstalled=previous['counts']['installedVerified'])

def evidence():
 r=stage.read(stage.DOC/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:check(q)
 q=stage.read(stage.DOC/'qualification.json');assert q['privateStageQualified']and q['sourceSHA256ByUid']==stage.SOURCES;check(q['currentManifest'])
 for review in q['sourceReviews']:check(review)
 images=stage.read(REVIEW/'ROOT-IMAGE-INSPECTION.json');assert images['sourceGeometryAppearanceAccepted']
 for image in images['reviewedImages']:check(image)
 models=stage.read(stage.STAGE/'catalogue.json')['models'];assert {m['uid']:m['sha256']for m in models}==stage.SOURCES
 for m in models:
  assert all(m.get(k)is True for k in ['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved']);assert m['proceduralWindows']is False and not m.get('suppressesBuildingUids')
  if m['uid']!=stage.PODIUM:
   deps=m['supportDependencies'];assert len(deps)==1 and deps[0]['uid']==stage.PODIUM and deps[0]['sha256']==stage.SOURCES[stage.PODIUM]and deps[0]['state']=='candidate'
 report=stage.read(BROWSER/'staged-browser.json');assert report['passed']and not report['errors']and len([v for v in report['views']if 'time'in v])==16
 failure=[v for v in report['views']if v.get('phase')=='failed-download'];assert len(failure)==1 and failure[0]['fallbackRetained']
 neighbours=stage.read(stage.folder('four-originals-neighbours-v2')/'neighbour-inputs.json.gz')['rows'];uids={r['building']['uid']for r in neighbours}|set(stage.SOURCES)
 assert not stage.read(stage.folder('four-originals-neighbours-v2')/'summary.json')['remainingFailures']
 return {'building:'+u for u in uids}|{'terrain:oi-sin:'+stage.read(stage.STAGE/'plan.json')['topLevelTerrainPatches'][0]['sha256']}

def assert_publication_idle():check(stage.read(stage.DOC/'qualification.json')['currentManifest'])

def main():
 ap=argparse.ArgumentParser();ap.add_argument('plan');ap.add_argument('--receipt',required=True);ap.add_argument('--phase',required=True);ap.add_argument('--apply',action='store_true');a=ap.parse_args();assert a.phase==BATCH and(ROOT/a.plan).resolve()==stage.STAGE/'plan.json';keys=evidence();lease=json.loads(Path(a.receipt).read_text())
 @contextmanager
 def guard():
  with connect()as db:
   db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));live=reservations._current(db,lease);assert live and keys<=set(live['resources']);assert_publication_idle();yield
 with guard():pass
 pub=stage.module('oi_sin_atomic_publisher',HERE.parent/'island-detail-integration/publish.py');pub.PUBLICATION_GUARD=guard;pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/a.phase;sys.argv=['publish.py',a.plan]+(['--apply']if a.apply else[]);pub.main()
if __name__=='__main__':main()
