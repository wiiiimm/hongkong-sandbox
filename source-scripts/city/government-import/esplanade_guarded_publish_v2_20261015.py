"""Publish only the exact reviewed original pair under current evidence and leases.

The manifest binding deliberately expires after any intervening installation.
Rebind affected-current evidence before using this publisher on a changed map.
"""
import argparse,json,sys
from pathlib import Path
from contextlib import contextmanager
import esplanade_joint_private_stage_v1_20261015 as stage
from run import connect,reservations,dict_row
ROOT=stage.ROOT;HERE=stage.HERE;BASE=stage.BASE
BATCH='government-xl-esplanade-original-installed-v2-20261015'
BROWSER=BASE/'government-xl-esplanade-joint-staged-browser-v2-20261015'
REVIEW=BASE/'government-xl-esplanade-staged-image-review-v2-20261015'

def check(q):
 assert stage.digest((ROOT/q['path']).read_bytes())==q['sha256'],q['path']

def evidence():
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [BASE/'government-xl-esplanade-museum-current-rebind-v1-20261015',BROWSER,REVIEW]:
   r=stage.read(folder/'result.json')
   assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   for q in r['evidenceRefs']:check(q)
 review=stage.read(BROWSER/'ROOT-IMAGE-INSPECTION.json');report=stage.read(BROWSER/'staged-browser.json')
 assert review['reviewer']=='Codex ROOT'and review['visualAcceptance']and review['allEightExportedImagesActuallyInspected']
 assert review['stagedBrowser']==stage.ref(BROWSER/'staged-browser.json')and review['sourceStage']==stage.ref(stage.DOC/'result.json')
 assert review['currentManifest']==stage.ref(ROOT/'3d-viewer/city/data/manifest.json'),'Current map changed; reconcile affected-current evidence before publication'
 views=[v for v in report['views']if 'time'in v]
 assert report['passed']and not report['errors']and len(views)==8
 assert review['imagesActuallyViewed']==[stage.ref(BROWSER/v['file'])for v in views]
 assert len(report['jointViews'])==4
 for joint in report['jointViews']:
  assert {m['uid']:m['sourceSHA256']for m in joint['models']}==stage.SOURCES
  assert all(m['active']and m['visible']and not m['fallbackFaces']for m in joint['models'])
 for v in views:assert v['fullyFramed']and v['solidAppearance']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==stage.SOURCES[v['uid']]
 plan=stage.read(stage.STAGE/'plan.json');assert set(plan)=={'areas','topLevelTerrainPatches'}and len(plan['areas'])==len(plan['topLevelTerrainPatches'])==1
 assert set(plan['areas'][0])=={'area','catalogue','destination'}
 models=stage.read(stage.STAGE/'catalogue.json')['models'];assert {m['uid']:m['sha256']for m in models}==stage.SOURCES
 actors=stage.read(BASE/stage.NAMES['capture']/'basic-actors.json.gz')['rows']
 keys={p+uid for p in ['building:','terrain-patch:']for uid in {r['uid']for r in actors}|set(stage.SOURCES)}
 return keys

def assert_publication_idle():
 for pid,name in [(1132389,'polyu_complete_saved_actor_finite_v2_draft_20261014.py'),(1136726,'polyu_complete_saved_actor_finite_v2_draft_20261014.py'),(1136786,'polyu_complete_saved_actor_finite_v2_draft_20261014.py'),(2288665,'heritage165054_original_live_install_v1_20261015.py')]:
  p=Path('/proc')/str(pid)/'cmdline'
  try:command=p.read_bytes()
  except FileNotFoundError:continue
  assert name.encode()not in command,'Prior pinned worker or installer remains live: '+str(pid)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('plan');ap.add_argument('--receipt',required=True);ap.add_argument('--phase',required=True);ap.add_argument('--apply',action='store_true');a=ap.parse_args()
 assert a.phase==BATCH and (ROOT/a.plan).resolve()==stage.STAGE/'plan.json'
 if a.apply:assert_publication_idle()
 keys=evidence();lease=json.loads(Path(a.receipt).read_text())
 @contextmanager
 def guard():
  if a.apply:assert_publication_idle()
  with connect()as db:
   db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));live=reservations._current(db,lease)
   assert live and keys<=set(live['resources']),'Missing or incomplete original-model lease'
   assert stage.read(BROWSER/'ROOT-IMAGE-INSPECTION.json')['currentManifest']==stage.ref(ROOT/'3d-viewer/city/data/manifest.json')
   yield
 with guard():pass
 pub=stage.module('esplanade_unchanged_publisher',HERE.parent/'island-detail-integration/publish.py');pub.PUBLICATION_GUARD=guard;pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/a.phase
 sys.argv=['publish.py',a.plan]+(['--apply']if a.apply else[]);pub.main()
if __name__=='__main__':main()
