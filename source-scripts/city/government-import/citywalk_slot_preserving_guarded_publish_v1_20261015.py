"""ROOT-only scoped Citywalk wrapper around unchanged publisher/ownership guards.
Only metadata replacement ordering differs; preserves captured parent slot.
"""
import argparse,importlib.util,json,sys,hashlib
from pathlib import Path
from contextlib import contextmanager
from upton_preserve_replacement_slot_v1_20261014 import preserve_slot
OWNED=['landsd/134332:0']
EXPECTED={OWNED[0]:('2976025668P20070723','b2d26e9f7a3b033877cd8c2aa6e6c363fec2cdcc2c09af8b06a1e3f583ad17df')}
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'))
from db import connect
from psycopg.rows import dict_row
import reservations
def main():
    parser=argparse.ArgumentParser();parser.add_argument('plan');parser.add_argument('--receipt',required=True);parser.add_argument('--phase',required=True);parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    assert args.phase.startswith('government-xl-citywalk-reviewed-')and args.phase.replace('-','').isalnum()
    initial={}
    def load(p):
        p=p.resolve();assert p.is_relative_to(ROOT);b=p.read_bytes();initial[p]=hashlib.sha256(b).hexdigest();return json.loads(b)
    plan=load(ROOT/args.plan);assert len(plan['areas'])==len(plan['topLevelTerrainPatches'])==1
    models=load(ROOT/plan['areas'][0]['catalogue'])['models'];assert [m['uid']for m in models]==OWNED
    for m in models:assert (m['buildingCSUID'],m['sha256'])==EXPECTED[m['uid']]
    terrain=plan['topLevelTerrainPatches'][0];assert terrain['replaces']['url']=='city/data/government-native-134332-0.json'and terrain['sha256']=='6ee29029c6d5d6ae4aacefba7dc8c4d87c604776eeed923df5960d1d2bb117d6'
    dependencies=set()
    for item in plan.get('dependencyReviews',[]):
        dependencies.update(c['uid']for c in load(ROOT/item['path'])['changes'])
    assert dependencies=={'landsd/215992:0','landsd/216991:0','landsd/218019:0','landsd/218095:0','landsd/218258:0'}
    @contextmanager
    def guard():
        with connect()as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));g=reservations._current(con,json.loads(Path(args.receipt).read_text()));assert g
            assert {'building:'+u for u in set(OWNED)|dependencies}<=set(g['resources'])
            for p,h in initial.items():assert hashlib.sha256(p.read_bytes()).hexdigest()==h
            yield
    with guard():pass
    spec=importlib.util.spec_from_file_location('upton_unchanged_publisher',ROOT/'source-scripts/city/island-detail-integration/publish.py');publisher=importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher)
    original_fn=publisher.stage_top_level_terrain
    def source_slot(plan,original,manifest,edits,report):
        original_fn(plan,original,manifest,edits,report) # All native/overlap/source guards unchanged.
        report['citywalkExactCapturedReplacementSlot']=preserve_slot(original,manifest,terrain['replaces']['url'],terrain['destination'])
    publisher.stage_top_level_terrain=source_slot;publisher.DOC=ROOT/'docs/astra-city/model-integration-20260909'/args.phase;publisher.PUBLICATION_GUARD=guard
    sys.argv=['publish.py',args.plan]+(['--apply']if args.apply else[]);publisher.main()
if __name__=='__main__':main()
