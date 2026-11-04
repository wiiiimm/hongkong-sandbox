"""Prove derived-terrain normalization against the actual production parser."""
import argparse,subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
    p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--patch',required=True);a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();receipt,pins=authenticate(base/a.patch);candidate=receipt['candidate'];path=ROOT/candidate['path'];assert digest(path.read_bytes())==candidate['sha256']==pins[str(path.relative_to(ROOT))]
    mesh=read(path)['nativeMesh'];tool=HERE/'rendered_native_terrain_input_probe_v1_20261029.mjs';out.mkdir()
    with(out/'probe.log').open('w')as log:subprocess.run(['node',str(tool),str(path.relative_to(ROOT)),str((out/'probe.json').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    probe=read(out/'probe.json');assert probe['sourcePatchSHA256']==candidate['sha256']and probe['identicalRenderedPositionBytes']and probe['identicalRenderedIndices']
    positions=np.asarray(mesh['position'],dtype='<f4');assert digest(positions.tobytes())==probe['renderedPositionsSHA256']
    result=dict(uids=receipt['uids'],renderedInputProof=probe,sourceGeometryChanges=0,installationApproved=False,qualification='Actual production parser and independent NumPy Float32 encoding agree for every input terrain position. Normalization preserves all rendered bytes and indices. No source geometry, terrain shape, pipeline guard or approval is changed by this diagnostic.')
    save(out/'summary.json',result);refs=[Path(__file__),tool,path,base/a.patch/'result.json',ROOT/'3d-viewer/city/native-terrain.js',ROOT/'3d-viewer/city/exact-finite-triangle-projection.js']
    module('rendered_native_input_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'actual-production-native-terrain-input-representation-equivalence',refs,result)

if __name__=='__main__':main()
