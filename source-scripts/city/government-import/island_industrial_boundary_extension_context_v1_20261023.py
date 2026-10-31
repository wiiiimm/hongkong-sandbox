"""Measure a one-column envelope extension without creating or approving terrain."""
from pathlib import Path
from collections import Counter
import subprocess
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from retained_rendered_union_template_v1_20261023 import verify_retained_faces


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-industrial-boundary-extension-context-v1-20261023'
    out=base/batch;local=HERE/'local'/batch;assert not out.exists()and not local.exists()
    capture='government-xl-after-fu-tor-loy-island-industrial-current-capture-v1-20261023';_,pins=authenticate(base/capture)
    mp=ROOT/'3d-viewer/city/data/manifest.json';assert digest(mp.read_bytes())==pins[str(mp.relative_to(ROOT))]
    pp=ROOT/'3d-viewer/city/data/terrain.json';parent=read(pp)
    oldpath=ROOT/'3d-viewer/city/data/government-native-225173-0.json';old=read(oldpath);assert digest(oldpath.read_bytes())==pins[str(oldpath.relative_to(ROOT))]
    cells=old['coarseCells'].copy();cells[2]+=1
    builder=module('boundary_extension_bounds',HERE/'validated_parent_roundoff_template_v2.py');bounds=builder.extent(cells,parent)
    save(out/'scope.json',dict(uids=['landsd/159422:0','landsd/20270:0'],cells=cells,bounds=bounds,qualification='Capture-only one-column envelope; no proposed mesh.'))
    tool=HERE/'selected_original_parent_capture_v1.mjs'
    with (out/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str((out/'scope.json').relative_to(ROOT)),str((local/'parent.json').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    captured=read(local/'parent.json');refs=[Path(__file__),base/capture/'result.json',out/'scope.json',tool,local/'parent.json']
    for path,sha in captured['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    baseline=np.asarray(captured['triangles']);vertices=np.asarray(old['nativeMesh']['position']).reshape(-1,3);original=vertices[np.asarray(old['nativeMesh']['index']).reshape(-1,3)]
    domain=shapely.box(*bounds);proof=verify_retained_faces(baseline,[original],domain)
    union=shapely.union_all([shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in baseline]);missing=domain.difference(union)
    oldbounds=builder.extent(old['coarseCells'],parent);extension=domain.difference(shapely.box(*oldbounds))
    save(out/'missing-domain.wkt',missing.wkt)
    result=dict(uids=['landsd/159422:0','landsd/20270:0'],coarseCells=cells,bounds=bounds,retainedSource=dict(path=str(oldpath.relative_to(ROOT)),sha256=digest(oldpath.read_bytes())),exactOriginalFaces=proof,missingAreaM2=missing.area,extensionAreaM2=extension.area,missingAreaInExtensionM2=missing.intersection(extension).area,sourceGeometryChanges=0,installationApproved=False,qualification='Actual renderer whole-envelope capture and exact old-face/duplicate preservation diagnostics only. No surface authored, boundary validator changed, coverage waived or model installed.')
    save(out/'summary.json',result);refs.extend([HERE/'retained_rendered_union_template_v1_20261023.py',HERE/'validated_parent_roundoff_template_v2.py'])
    module('boundary_extension_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-rendered-boundary-extension-diagnostic',refs,result)
    print({k:v for k,v in result.items()if k not in ['qualification','retainedSource']},flush=True)


if __name__=='__main__':main()
