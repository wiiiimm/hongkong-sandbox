"""Publish only the exact three-original Orchards assembly with all evidence and leases."""
import argparse,json,sys
from pathlib import Path
from contextlib import contextmanager
import orchards_qualified_stage_v1_20261017 as stage
from run import connect,reservations,dict_row
from fixed_xl_source_binding import resolve_uid
ROOT=stage.ROOT;HERE=stage.HERE;BASE=stage.BASE;BATCH='government-xl-orchards-original-installed-v1-20261017';BROWSER=stage.folder('assembly-private-browser-v4');REVIEW=stage.folder('assembly-visual-review-v1');check=stage.check

def inventory_delta(previous,models,*,manifest_sha,snapshot):
 assert previous['manifestSHA256']==manifest_sha and previous['snapshotId']==snapshot
 assert len(previous['rows'])==len({r['sourceKey']for r in previous['rows']})==previous['counts']['total']==521
 assert {m['uid']:m['sha256']for m in models}==stage.SOURCES
 keys={m['originalSourceKey']for m in models};assert len(keys)==len(models)==3
 matched=[r for r in previous['rows']if r['sourceKey']in keys];assert matched and all(not r['installedVerified']for r in matched)
 uids=[resolve_uid(r,models)for r in matched];assert len(uids)==len(set(uids))and set(uids)<=set(stage.SOURCES)
 return dict(returnedModels=3,fixedXLTotal=521,newFixedXLUids=uids,newFixedXLSourceKeys=[r['sourceKey']for r in matched],expectedFixedXLDelta=len(matched),previousInstalled=previous['counts']['installedVerified'])

def evidence():
 r=stage.read(stage.DOC/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={}
 for q in r['evidenceRefs']:
  assert q['path']not in pins or pins[q['path']]==q;pins[q['path']]=q
 for q in pins.values():check(q)
 q=stage.read(stage.DOC/'qualification.json');assert q['privateStageQualified']and q['sourceSHA256ByUid']==stage.SOURCES;check(q['currentManifest'])
 for review in q['sourceReviews']:check(review)
 images=stage.read(REVIEW/'ROOT-IMAGE-INSPECTION.json');assert images['sourceGeometryAppearanceAccepted']
 for image in images['reviewedImages']:check({k:image[k]for k in ['path','sha256']})
 models=stage.read(stage.STAGE/'catalogue.json')['models'];assert {m['uid']:m['sha256']for m in models}==stage.SOURCES
 companion=q['requiredIdentityCompanion'];assert companion==dict(owner=stage.PODIUM,uid=stage.COMMUNITY,sha256=stage.SOURCES[stage.COMMUNITY])
 for m in models:
  assert all(m.get(k)is True for k in ['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved']);assert m['proceduralWindows']is False and not m.get('suppressesBuildingUids')
  if m['uid']==stage.TOWER:
   deps=m['supportDependencies'];assert len(deps)==1 and deps[0]['uid']==stage.PODIUM and deps[0]['sha256']==stage.SOURCES[stage.PODIUM]and deps[0]['state']=='candidate'
  else:assert not m.get('supportDependencies')
 report=stage.read(BROWSER/'staged-browser.json');assert report['passed']and not report['errors']and len([v for v in report['views']if 'time'in v])==12
 failure=[v for v in report['views']if v.get('phase')=='failed-download'];assert len(failure)==1 and failure[0]['fallbackRetained']
 scope=stage.read(stage.folder('assembly-terrain-candidate-v1')/'scope.json');assert scope['touchingNativeUids']==[stage.RETAINED]
 neighbours=stage.read(stage.folder('assembly-neighbours-v1')/'summary.json');assert not neighbours['basicFlags']and neighbours['nativeResolved']==[stage.RETAINED]
 return {'building:'+u for u in scope['basicAndNativeForms']}|{'terrain:orchards:'+stage.read(stage.STAGE/'plan.json')['topLevelTerrainPatches'][0]['sha256']}

def assert_publication_idle():check(stage.read(stage.DOC/'qualification.json')['currentManifest'])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('plan');ap.add_argument('--receipt',required=True);ap.add_argument('--phase',required=True);ap.add_argument('--apply',action='store_true');a=ap.parse_args();assert a.phase==BATCH and(ROOT/a.plan).resolve()==stage.STAGE/'plan.json';keys=evidence();lease=json.loads(Path(a.receipt).read_text())
 @contextmanager
 def guard():
  with connect()as db:
   db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));live=reservations._current(db,lease);assert live and keys<=set(live['resources']);assert_publication_idle();yield
 with guard():pass
 pub=stage.module('orchards_atomic_publisher',HERE.parent/'island-detail-integration/publish.py');pub.PUBLICATION_GUARD=guard;pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/a.phase;sys.argv=['publish.py',a.plan]+(['--apply']if a.apply else[]);pub.main()
if __name__=='__main__':main()
