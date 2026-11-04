"""Exact reviewed nine-original publication guard; preserves dependencies and BASIC fixes."""
import argparse,json,sys
from pathlib import Path
from contextlib import contextmanager
import wave_verdant_qualified_stage_v1_20261018 as stage
from run import connect,reservations,dict_row
from fixed_xl_source_binding import resolve_uid
ROOT=stage.ROOT;HERE=stage.HERE;BASE=stage.BASE;BATCH='government-xl-wave-verdant-original-installed-v1-20261018';BROWSER=stage.BROWSER;REVIEW=stage.REVIEW;check=stage.check
stage.SOURCES=stage.read(REVIEW/'ROOT-SOURCE-REVIEW.json')['sourceSHA256ByUid']
def inventory_delta(previous,models,*,manifest_sha,snapshot):
 assert previous['manifestSHA256']==manifest_sha and previous['snapshotId']==snapshot
 assert len(previous['rows'])==len({r['sourceKey']for r in previous['rows']})==previous['counts']['total']==521
 assert {m['uid']:m['sha256']for m in models}==stage.SOURCES and len(models)==9
 keys={m['originalSourceKey']for m in models};matched=[r for r in previous['rows']if r['sourceKey']in keys];assert matched and all(not r['installedVerified']for r in matched)
 uids=[resolve_uid(r,models)for r in matched];assert len(uids)==len(set(uids))
 return dict(returnedModels=9,fixedXLTotal=521,newFixedXLUids=uids,newFixedXLSourceKeys=[r['sourceKey']for r in matched],expectedFixedXLDelta=len(matched),previousInstalled=previous['counts']['installedVerified'])
def evidence():
 r=stage.read(stage.DOC/'result.json');pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e;pins[e['path']]=e
 for e in pins.values():check(e)
 q=stage.read(stage.DOC/'qualification.json');assert q['privateStageQualified']and q['sourceSHA256ByUid']==stage.SOURCES;check(q['currentManifest'])
 review=stage.read(REVIEW/'ROOT-SOURCE-REVIEW.json');assert review['originalSourceReviewAccepted']and review['policyReasons']==[];check(q['sourceReview'])
 models=stage.read(stage.STAGE/'catalogue.json')['models'];assert {m['uid']:m['sha256']for m in models}==stage.SOURCES
 original=stage.read(stage.OLD/'catalogue.json')['models'];prior={m['uid']:m for m in original}
 for m in models:
  assert all(m.get(k)is True for k in ['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved']);assert m['proceduralWindows']is False and not m.get('suppressesBuildingUids');assert m.get('supportDependencies')==prior[m['uid']].get('supportDependencies');check(dict(path=str((stage.STAGE/m['asset']).relative_to(ROOT)),sha256=m['sha256']))
 report=stage.read(BROWSER/'staged-browser.json');assert report['passed']and not report['errors']and len([v for v in report['views']if 'time'in v])==36
 plan=stage.read(stage.STAGE/'plan.json');assert len(plan['topLevelTerrainPatches'])==1;t=plan['topLevelTerrainPatches'][0];assert t==q['terrainCandidate']and not t.get('replaces');check(dict(path=t['source'],sha256=t['sha256']))
 assert len(plan['illustrativeFoundations'])==1 and plan['illustrativeFoundations'][0]['uid']=='landsd/268957:0'
 scope=stage.read(BASE/'government-xl-wave-verdant-current-terrain-rebind-v5-20261018/scope.json');assert scope['currentNativeActors']==6684 and not scope['touchingNativeUids']
 return {'building:'+u for u in scope['basicAndNativeForms']}|{'terrain:city/data/terrain.json','terrain:'+t['destination']}
def assert_publication_idle():check(stage.read(stage.DOC/'qualification.json')['currentManifest'])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('plan');ap.add_argument('--receipt',required=True);ap.add_argument('--phase',required=True);ap.add_argument('--apply',action='store_true');a=ap.parse_args();assert a.phase==BATCH and(ROOT/a.plan).resolve()==stage.STAGE/'plan.json';keys=evidence();lease=json.loads(Path(a.receipt).read_text())
 @contextmanager
 def guard():
  with connect()as db:
   db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));live=reservations._current(db,lease);assert live and keys<=set(live['resources']);assert_publication_idle();yield
 with guard():pass
 pub=stage.module('wave_atomic_publisher',HERE.parent/'island-detail-integration/publish.py');pub.PUBLICATION_GUARD=guard;pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/a.phase;sys.argv=['publish.py',a.plan]+(['--apply']if a.apply else[]);pub.main()
if __name__=='__main__':main()
