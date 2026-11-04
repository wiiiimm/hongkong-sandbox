"""Run the existing guarded publisher with isolated evidence and live model ownership."""
import argparse,importlib.util,json,sys,hashlib
from contextlib import contextmanager
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'))
from db import connect
from psycopg.rows import dict_row
import reservations
p=argparse.ArgumentParser();p.add_argument('plan');p.add_argument('--receipt',action='append',required=True);p.add_argument('--phase',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
assert a.phase.replace('-','').isalnum()
initial_inputs={}
def initial_load(path):
 path=path.resolve();raw=path.read_bytes();initial_inputs[path]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
plan_path=(ROOT/a.plan).resolve()
plan=initial_load(plan_path);uids={m['uid'] for area in plan['areas'] for m in initial_load(ROOT/area['catalogue'])['models']}
for area in plan['areas']:
 for estimate in area.get('estimates',[]):
  uids.update(b['uid'] for b in initial_load(ROOT/estimate)['buildings'])
for review in plan.get('dependencyReviews',[])+plan.get('priorityReviews',[]):
 uids.update(c['uid'] for c in initial_load(ROOT/review['path'])['changes'])
@contextmanager
def publication_guard():
 with connect() as con:
  con.row_factory=dict_row
  con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
  resources=set()
  for receipt in a.receipt:
   group=reservations._current(con,json.loads(Path(receipt).read_text()));assert group,'Reservation expired or superseded'
   resources.update(group['resources'])
  assert {'building:'+uid for uid in uids}<=resources,'Missing source ownership'
  for path,digest in initial_inputs.items():
   assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,'Publication ownership input changed'
  yield
# Initial ownership check is quick; no map preparation runs under its lock.
with publication_guard():pass
spec=importlib.util.spec_from_file_location('publisher',ROOT/'source-scripts/city/island-detail-integration/publish.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.DOC=ROOT/'docs/astra-city/model-integration-20260909'/a.phase
module.PUBLICATION_GUARD=publication_guard
sys.argv=['publish.py',a.plan]+(['--apply'] if a.apply else [])
from reviewed_multi_native_terrain_publication_20261009 import stage_top_level
original_stage=module.stage_top_level_terrain
module.stage_top_level_terrain=lambda plan,original,manifest,edits,report:stage_top_level(module,plan,original,manifest,edits,report,original_stage)
module.main()
