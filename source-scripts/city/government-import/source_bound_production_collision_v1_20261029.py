"""Freeze actual production BASIC collision/roof preservation evidence."""
import subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-sha-tin-';BATCH=P+'production-basic-collision-v1-20261029'


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];fi=P+'source-bound-production-fixture-v1-20261029';bc=P+'three-basic-continuation-foreign-volume-v1-20261029'
    _,fp=authenticate(BASE/fi);_,bp=authenticate(BASE/bc);cfg=HERE/'local'/fi/'config.json';basics=BASE/bc/'basic.json';assert digest(cfg.read_bytes())==fp[str(cfg.relative_to(ROOT))]and digest(basics.read_bytes())==bp[str(basics.relative_to(ROOT))];refs.extend([BASE/fi/'result.json',BASE/bc/'result.json',cfg,basics])
    out.mkdir();save(out/'input.json',dict(config=str(cfg.relative_to(ROOT)),basics=str(basics.relative_to(ROOT)),inputHashes={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in [cfg,basics]}));tool=HERE/'source_bound_production_collision_v1_20261029.mjs';refs.append(tool)
    subprocess.run(['node',str(tool),str((out/'input.json').relative_to(ROOT)),str((out/'summary.json').relative_to(ROOT))],cwd=ROOT,check=True);result=read(out/'summary.json')
    for path,sha in result['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    result['sourceGeometryChanges']=0;save(out/'summary.json',result)
    module('production_basic_collision_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'actual-production-basic-source-bound-lower-volume-and-roof-invariants',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
