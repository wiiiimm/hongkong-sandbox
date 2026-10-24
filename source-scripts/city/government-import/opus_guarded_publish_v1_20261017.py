"""Publish only the exact qualified three-source Opus original assembly."""
import argparse,json,sys
from pathlib import Path
from contextlib import contextmanager
import opus_qualified_stage_v1_20261017 as stage
from run import connect,reservations,dict_row
from fixed_xl_source_binding import resolve_uid
ROOT=stage.ROOT;HERE=stage.HERE;BASE=stage.BASE
BATCH='government-xl-opus-original-installed-v1-20261017';BROWSER=stage.DOC;REVIEW=stage.DOC

def check(q):assert stage.ref(ROOT/q['path'])==q

def inventory_delta(previous,models,*,manifest_sha,snapshot):
 assert previous['manifestSHA256']==manifest_sha and previous['snapshotId']==snapshot
 assert len(previous['rows'])==len({r['sourceKey']for r in previous['rows']})==previous['counts']['total']==521
 assert len(models)==3 and {m['uid']:m['sha256']for m in models}==stage.SOURCES
 matching=[r for r in previous['rows']if resolve_uid(r,models)in stage.SOURCES];assert matching
 for r in matching:
  u=resolve_uid(r,models);m=next(m for m in models if m['uid']==u);assert not r['installedVerified']and r['sourceKey']==m['originalSourceKey']and r['indexedSourceSHA256']==m['sha256']
 return dict(returnedModels=3,fixedXLTotal=521,newFixedXLUids=[resolve_uid(r,models)for r in matching],newFixedXLSourceKeys=[r['sourceKey']for r in matching],expectedFixedXLDelta=len(matching),previousInstalled=previous['counts']['installedVerified'])

def evidence():
 r=stage.read(stage.DOC/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={}
 for q in r['evidenceRefs']:assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():check(dict(path=p,sha256=h))
 q=stage.read(stage.DOC/'qualification.json');assert q['privateStageQualified']and q['sourceSHA256ByUid']==stage.SOURCES and q['remainingPolicyReasons']=={u:[]for u in stage.SOURCES}
 for k in ['currentManifest','sourceIdentityReview','sourceSupportReview','foundation','fullFinite']:check(q[k])
 review=stage.read(stage.DOC/'ROOT-IMAGE-INSPECTION.json');assert review['reviewer']=='Codex ROOT'and review['sourceGeometryAppearanceAccepted']and len(review['reviewedImages'])==4
 for image in review['reviewedImages']:check(image)
 models=stage.read(stage.STAGE/'catalogue.json')['models'];assert len(models)==3 and {m['uid']:m['sha256']for m in models}==stage.SOURCES
 for m in models:
  assert all(m.get(k)is True for k in ['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved']);assert m['proceduralWindows']is False and not m.get('suppressesBuildingUids')
  assert m['supportDependencies']==([]if m['uid']==stage.PODIUM else[dict(uid=stage.PODIUM,state='candidate',csuid='3599414486P20120215',sha256=stage.SOURCES[stage.PODIUM])])
 report=stage.data('original-group-browser-v1','staged-browser.json');assert report['passed']and not report['errors']and len([v for v in report['views']if 'time'in v])==12 and len(report['jointViews'])==6
 failed=[v for v in report['views']if v.get('phase')=='failed-download'];assert len(failed)==1 and failed[0]['fallbackRetained']and failed[0]['dependentFallbacks']=={stage.TOWER:{'active':False},stage.COMPANION:{'active':False}}
 finite=stage.data('basic-finite-v1','summary.json');assert finite['all2ActorsComplete']and finite['noIntroducedFailures']and len(finite['rows'])==2
 uids={r['uid']for r in finite['rows']}|set(stage.SOURCES)
 return {prefix+uid for prefix in ['building:','terrain-patch:']for uid in uids}

def assert_publication_idle():check(stage.read(stage.DOC/'qualification.json')['currentManifest'])

def main():
 ap=argparse.ArgumentParser();ap.add_argument('plan');ap.add_argument('--receipt',required=True);ap.add_argument('--phase',required=True);ap.add_argument('--apply',action='store_true');a=ap.parse_args()
 assert a.phase==BATCH and (ROOT/a.plan).resolve()==stage.STAGE/'plan.json';keys=evidence();lease=json.loads(Path(a.receipt).read_text())
 @contextmanager
 def guard():
  with connect()as db:
   db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));live=reservations._current(db,lease);assert live and keys<=set(live['resources']);assert_publication_idle();yield
 with guard():pass
 pub=stage.module('opus_unchanged_publisher',HERE.parent/'island-detail-integration/publish.py');pub.PUBLICATION_GUARD=guard;pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/a.phase
 sys.argv=['publish.py',a.plan]+(['--apply']if a.apply else[]);pub.main()
if __name__=='__main__':main()
