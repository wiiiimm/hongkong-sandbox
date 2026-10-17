"""ROOT-only scoped Upton wrapper around unchanged publisher/ownership guards.
Only metadata replacement ordering differs; preserves captured parent slot.
"""
import argparse,importlib.util,json,sys,hashlib
from pathlib import Path
from contextlib import contextmanager
from upton_preserve_replacement_slot_v1_20261014 import preserve_slot
from upton_original_functional_applicability_adapter_v1_20261014 import EXPECTED,OWNED
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'))
from db import connect
from psycopg.rows import dict_row
import reservations
def main():
    parser=argparse.ArgumentParser();parser.add_argument('plan');parser.add_argument('--receipt',required=True);parser.add_argument('--phase',required=True);parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    assert args.phase.startswith('government-xl-upton-joint-original-functional-')and args.phase.replace('-','').isalnum()
    initial={}
    def load(p):
        p=p.resolve();assert p.is_relative_to(ROOT);b=p.read_bytes();initial[p]=hashlib.sha256(b).hexdigest();return json.loads(b)
    plan=load(ROOT/args.plan);assert len(plan['areas'])==len(plan['topLevelTerrainPatches'])==1
    models=load(ROOT/plan['areas'][0]['catalogue'])['models'];assert [m['uid']for m in models]==OWNED
    for m in models:assert (m['buildingCSUID'],m['sha256'])==EXPECTED[m['uid']]
    terrain=plan['topLevelTerrainPatches'][0];assert terrain['replaces']['url']=='city/data/government-native-79882-0.json'and terrain['sha256']=='f367dc82a617357da96ddeb004d4e6aa75329ca237a5f5033ce3f21daf1f7848'
    @contextmanager
    def guard():
        with connect()as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));g=reservations._current(con,json.loads(Path(args.receipt).read_text()));assert g
            assert {'building:'+u for u in OWNED}<=set(g['resources'])
            for p,h in initial.items():assert hashlib.sha256(p.read_bytes()).hexdigest()==h
            yield
    with guard():pass
    spec=importlib.util.spec_from_file_location('upton_unchanged_publisher',ROOT/'source-scripts/city/island-detail-integration/publish.py');publisher=importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher)
    original_fn=publisher.stage_top_level_terrain
    def source_slot(plan,original,manifest,edits,report):
        original_fn(plan,original,manifest,edits,report) # All native/overlap/source guards unchanged.
        report['uptonExactCapturedReplacementSlot']=preserve_slot(original,manifest,terrain['replaces']['url'],terrain['destination'])
    publisher.stage_top_level_terrain=source_slot;publisher.DOC=ROOT/'docs/astra-city/model-integration-20260909'/args.phase;publisher.PUBLICATION_GUARD=guard
    sys.argv=['publish.py',args.plan]+(['--apply']if args.apply else[]);publisher.main()
if __name__=='__main__':main()
