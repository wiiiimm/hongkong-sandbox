"""Authenticate upstream proposals and record private real-source geometry checks."""
import subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import'
    batch='government-xl-sha-tin-three-basic-geometry-preservation-v1-20261029'
    proposal='government-xl-sha-tin-three-basic-ground-proposals-v2-20261029'
    runtime='government-xl-sha-tin-seven-upward-floor-runtime-v1-20261029'
    out=base/batch
    assert not out.exists()
    _,proposal_pins=authenticate(base/proposal)
    _,runtime_pins=authenticate(base/runtime)
    packet=base/proposal/'summary.json'
    geometry=HERE/'local'/runtime/'runtime-geometry.json.gz'
    for path,pins in [(packet,proposal_pins),(geometry,runtime_pins)]:
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
    tool=HERE/'source_bound_basic_geometry_capture_v1_20261029.mjs'
    out.mkdir()
    output=out/'summary.json'
    subprocess.run(['node',str(tool),str(packet.relative_to(ROOT)),str(geometry.relative_to(ROOT)),str(output.relative_to(ROOT))],cwd=ROOT,check=True)
    result=read(output)
    refs=[Path(__file__),tool,base/proposal/'result.json',base/runtime/'result.json']
    for path,sha in result['inputHashes'].items():
        p=ROOT/path
        assert digest(p.read_bytes())==sha
        refs.append(p)
    module('private_basic_geometry_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'private-original-source-basic-core-preservation-v1',refs,result)


if __name__=='__main__':
    main()
