"""Lease-fenced publication of the fully reviewed standalone original source(s)."""
import argparse,copy,json,sys
from pathlib import Path
from contextlib import contextmanager
import peninsula_exact_pair_qualified_stage_v1_20261029 as stage
from run import connect,reservations,dict_row
ROOT=stage.ROOT;HERE=stage.HERE;BASE=stage.BASE
BATCH=stage.CONFIG['prefix']+'-original-installed-v3-'+stage.CONFIG['date']
BROWSER=BASE/stage.CONFIG['browser'];REVIEW=BASE/stage.CONFIG['physical']
stage.SOURCES=stage.read(stage.DOC/'qualification.json')['sourceSHA256ByUid']
def check(q):assert stage.ref(ROOT/q['path'])==q,q['path']
def evidence():
 # Authenticate completed jobs; rehash the exact current consumed evidence rather
 # than obsolete mutable references inherited from historical diagnostic jobs.
 from china_ferry_current_foundations_v1_20261020 import authenticate
 from peninsula_exact_pair_install_contract_v1_20261029 import verify,PUBLIC_FIELDS
 cache={}
 def take(batch,path):
  if batch not in cache:cache[batch]=authenticate(BASE/batch)[1]
  q=stage.ref(path);assert cache[batch][q['path']]==q['sha256'];return stage.read(path)
 q=take(stage.DOC.name,stage.DOC/'qualification.json')
 assert q['privateStageQualified']and q['originalSourceReviewAccepted']and q['visualAcceptance']
 assert q['currentManifest']==stage.ref(ROOT/'3d-viewer/city/data/manifest.json')
 assert q['sourceSHA256ByUid']==stage.SOURCES==stage.CONFIG['sources']
 review=take(stage.CONFIG['review'],stage.SOURCE/'ROOT-SOURCE-REVIEW.json')
 physical=take(stage.CONFIG['physical'],REVIEW/'ROOT-PHYSICAL-REVIEW.json')
 lifecycle=take(stage.CONFIG['lifecycle'],BASE/stage.CONFIG['lifecycle']/'summary.json')
 private_review=take(stage.CONFIG['privateReview'],BASE/stage.CONFIG['privateReview']/'ROOT-PRIVATE-EXPERIMENT-REVIEW.json')
 scope=take(stage.CONFIG['scope'],BASE/stage.CONFIG['scope']/'270876:0-forms.json.gz')
 forms={r['building']['uid']:r['building']for r in scope}
 approved=take(stage.DOC.name,stage.STAGE/'catalogue.json')
 verify(approved['models'],review,physical,lifecycle,private_review,forms,approved=True)
 original=take(stage.CONFIG['browser'],stage.PREVIOUS/'catalogue.json')
 stripped=copy.deepcopy(approved)
 for model,old in zip(stripped['models'],original['models']):
  for key in PUBLIC_FIELDS:
   if key in old:model[key]=old[key]
   else:model.pop(key,None)
 assert stripped==original,'Published rendering metadata differs from exact tested private catalogue'
 assert len(q['imagesActuallyViewed'])==8 and len(q['browserReports'])==2
 for image in q['imagesActuallyViewed']:check(image)
 for report in q['browserReports']:
  check(report);r=take(stage.CONFIG['browser'],ROOT/report['path'])
  assert r['passed']and not r['errors'];views=[v for v in r['views']if 'time'in v]
  assert len(views)==4
  for v in views:assert v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==stage.SOURCES[v['uid']]and not v['retained']
  assert r['jointViews'] and all({m['uid']:m['sourceSHA256']for m in j['models']}==stage.SOURCES and all(m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])for j in r['jointViews'])
 for m in approved['models']:
  assert stage.ref(stage.STAGE/m['asset'])['sha256']==m['sha256']
  assert cache[stage.DOC.name][str((stage.STAGE/m['asset']).relative_to(ROOT))]==m['sha256']
 plan=take(stage.DOC.name,stage.STAGE/'plan.json')
 assert len(plan['areas'])==1 and plan['topLevelTerrainPatches']==[]
 assert take(stage.CONFIG['browser'],stage.PREVIOUS/'browser-config-390.json')['terrain']==[]
 assert not any(a.get('estimates')for a in plan['areas'])and not(stage.STAGE/'estimated-bases.json').exists()
 assert q['leaseResources']==sorted(set(review['leaseResources']))
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
