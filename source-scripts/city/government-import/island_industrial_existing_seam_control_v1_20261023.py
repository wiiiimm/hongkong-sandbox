"""Check the full existing native seam as a control for coordinated-boundary math."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from coordinated_native_boundary_v1_20261023 import seam_segments,seam_comparison_report


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-industrial-existing-seam-control-v1-20261023';out=base/batch;assert not out.exists()
    capture='government-xl-after-fu-tor-loy-island-industrial-current-capture-v1-20261023';_,pins=authenticate(base/capture)
    paths=[ROOT/'3d-viewer/city/data/government-native-225173-0.json',ROOT/'3d-viewer/city/data/government-native-fu-tor-loy-original-v1-20261023.json']
    refs=[Path(__file__),base/capture/'result.json'];curves=[];sources=[]
    for p in paths:
        assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);node=read(p)
        vertices=np.asarray(node['nativeMesh']['position']).reshape(-1,3);tri=vertices[np.asarray(node['nativeMesh']['index']).reshape(-1,3)]
        curves.append(seam_segments(tri,2,-4027.5,-27.5,392.5));sources.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
    proof=seam_comparison_report(*curves,-27.5,392.5)
    save(out/'curve-segments.json.gz',[[[str(v)for v in segment]for segment in curve]for curve in curves])
    result=dict(uids=['landsd/159422:0','landsd/20270:0'],sources=sources,axis='z',coordinate=-4027.5,range=[-27.5,392.5],segments=[len(c)for c in curves],proof=proof,sourceGeometryChanges=0,installationApproved=False,qualification='Existing unchanged native surfaces only: complete rational upper-envelope seam control. No new terrain boundary accepted; production validator and publication contract remain unchanged.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['coordinated_native_boundary_v1_20261023.py','test_coordinated_native_boundary_v1_20261023.py'])
    module('existing_seam_control_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-existing-native-seam-control',refs,result)
    print(dict(segments=result['segments'],proof=proof),flush=True)


if __name__=='__main__':main()
