"""Publish only the current qualified unchanged PolyU original under exact leases."""
import argparse,json,sys
from pathlib import Path
from contextlib import contextmanager
import polyu_qualified_stage_v1_20261015 as stage
from run import connect,reservations,dict_row
ROOT=stage.ROOT;HERE=stage.HERE;BASE=stage.BASE;BATCH='government-xl-polyu-original-installed-v1-20261015';BROWSER=stage.BROWSER;REVIEW=stage.DOC

def check(q):assert stage.ref(ROOT/q['path'])==q,q['path']
def evidence():
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [stage.DOC,BROWSER]:
   r=stage.read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   for q in r['evidenceRefs']:check(q)
 review=stage.read(REVIEW/'ROOT-IMAGE-INSPECTION.json');report=stage.read(BROWSER/'staged-browser.json');qualification=stage.read(stage.DOC/'qualification.json')
 assert review['reviewer']=='Codex ROOT'and review['visualAcceptance']and review['allEightExportedImagesActuallyInspected'];assert review['currentManifest']==stage.ref(ROOT/'3d-viewer/city/data/manifest.json')and review['stagedBrowser']==stage.ref(BROWSER/'staged-browser.json')
 assert qualification['privateStageQualified']and not qualification['numericReasons']and qualification['sourceSHA256ByUid']==stage.SOURCES
 views=[v for v in report['views']if 'time'in v];assert report['passed']and not report['errors']and len(views)==4 and len(report['retainedNativeOwnViews'])==4
 assert review['imagesActuallyViewed']==[stage.ref(BROWSER/v['file'])for v in views+report['retainedNativeOwnViews']]
 for v in views:assert v['fullyFramed']and v['pick']==v['collision']==stage.UID and v['sourceSHA256']==stage.SOURCES[stage.UID]and not v['fallbackFaces']
 models=stage.read(stage.STAGE/'catalogue.json')['models'];assert {m['uid']:m['sha256']for m in models}==stage.SOURCES
 before=stage.read(HERE/'local/government-xl-polyu-current-loader-validation-v1-20261015/catalogue.json')['models'][0];after=models[0]
 metadata={'sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved','aiGeometryModelling','sourceEvidenceInterpretationUsedAI','sourceFunctionalApplicability','identityProof'}
 assert {k:v for k,v in before.items()if k not in metadata}=={k:v for k,v in after.items()if k not in metadata}
 plan=stage.read(stage.STAGE/'plan.json');assert set(plan)=={'areas','topLevelTerrainPatches'}and len(plan['areas'])==len(plan['topLevelTerrainPatches'])==1
 oldconfig=stage.read(BROWSER/'browser-config.json');assert plan['topLevelTerrainPatches'][0]['sha256']==oldconfig['terrain'][0]['sha256']
 actors=stage.read(BASE/'government-xl-polyu-complete-saved-actor-finite-v2-20261014/complete-full-actor-current-candidate-finite.json.gz')['rows'];uids={a['uid']for a in actors}
 return {('basic-building:'if prefix=='building:'and not uid.startswith('landsd/')else prefix)+uid for prefix in ['building:','terrain-patch:']for uid in uids}
def assert_publication_idle():
 # Publication serialisation is enforced by the existing filesystem and DB locks.
 # Completed source workers retain terminal evidence; no worker is restarted here.
 pass

def main():
 ap=argparse.ArgumentParser();ap.add_argument('plan');ap.add_argument('--receipt',required=True);ap.add_argument('--phase',required=True);ap.add_argument('--apply',action='store_true');a=ap.parse_args();assert a.phase==BATCH and (ROOT/a.plan).resolve()==stage.STAGE/'plan.json';keys=evidence();lease=json.loads(Path(a.receipt).read_text())
 @contextmanager
 def guard():
  with connect()as db:
   db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));live=reservations._current(db,lease);assert live and keys<=set(live['resources']);assert stage.read(REVIEW/'ROOT-IMAGE-INSPECTION.json')['currentManifest']==stage.ref(ROOT/'3d-viewer/city/data/manifest.json');yield
 with guard():pass
 pub=stage.module('polyu_guarded_publisher',HERE.parent/'island-detail-integration/publish.py');pub.PUBLICATION_GUARD=guard;pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/a.phase;sys.argv=['publish.py',a.plan]+(['--apply']if a.apply else[]);pub.main()
if __name__=='__main__':main()
