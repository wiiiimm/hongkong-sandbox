"""Bind production geometry promotion to the exact completed private prototype."""
import subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-sha-tin-';BATCH=PREFIX+'production-geometry-equivalence-v1-20261029'


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return path
    runtime=PREFIX+'seven-upward-floor-runtime-v1-20261029';context=PREFIX+'three-basic-continuation-foreign-volume-v1-20261029';proposal=PREFIX+'three-basic-ground-proposals-v2-20261029';fixture=PREFIX+'source-bound-full-scene-fixture-v2-20261029'
    paths=dict(selection=take(runtime,BASE/runtime/'selection.json.gz'),runtime=take(runtime,HERE/'local'/runtime/'runtime-geometry.json.gz'),basics=take(context,BASE/context/'basic.json'),proposal=take(proposal,BASE/proposal/'summary.json'),oldPrivateShadow=take(fixture,HERE/'local'/fixture/'private-building-geometry.js'))
    old_helper=subprocess.check_output(['git','show','b7c7e969aa:3d-viewer/city/source-bound-basic-ground.js'],cwd=ROOT,text=True);current=(ROOT/'3d-viewer/city/source-bound-basic-ground.js').read_text();assert old_helper[old_helper.index('const sha='):]==current[current.index('const sha='):]
    core=ROOT/'3d-viewer/city/building-geometry-core.js';assert digest(core.read_bytes())=='f3336a37c5164a78c931c702ad2ca5f62ed872adab9513787d3f8517fb3bdd4e';refs.append(core)
    selection=read(paths['selection'])
    for row in selection['rows']:
        asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
    out.mkdir();save(out/'input.json',dict(**{k:str(p.relative_to(ROOT))for k,p in paths.items()},inputHashes={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in paths.values()}))
    tool=HERE/'source_bound_production_geometry_equivalence_v1_20261029.mjs';refs.append(tool);subprocess.run(['node',str(tool),str((out/'input.json').relative_to(ROOT)),str((out/'summary.json').relative_to(ROOT))],cwd=ROOT,check=True)
    result=read(out/'summary.json')
    for path,sha in result['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    result['hintValidatorFunctionBodyUnchanged']=True;save(out/'summary.json',result)
    module('production_basic_adapter_equivalence_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'production-adapter-exact-original-and-private-prototype-geometry-equivalence',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
