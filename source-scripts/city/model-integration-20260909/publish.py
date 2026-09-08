"""Run the existing guarded publisher with isolated evidence and live model ownership."""
import argparse,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'))
from db import connect
from psycopg.rows import dict_row
import reservations
p=argparse.ArgumentParser();p.add_argument('plan');p.add_argument('--receipt',action='append',required=True);p.add_argument('--phase',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
assert a.phase.replace('-','').isalnum()
plan=json.loads((ROOT/a.plan).read_text());uids={m['uid'] for area in plan['areas'] for m in json.loads((ROOT/area['catalogue']).read_text())['models']}
with connect() as con:
 con.row_factory=dict_row
 con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
 resources=set()
 for receipt in a.receipt:
  group=reservations._current(con,json.loads(Path(receipt).read_text()));assert group,'Reservation expired or superseded'
  resources.update(group['resources'])
 assert {'building:'+uid for uid in uids}<=resources,'Missing source ownership'
 spec=importlib.util.spec_from_file_location('publisher',ROOT/'source-scripts/city/island-detail-integration/publish.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 module.DOC=ROOT/'docs/astra-city/model-integration-20260909'/a.phase
 sys.argv=['publish.py',a.plan]+(['--apply'] if a.apply else [])
 module.main()
