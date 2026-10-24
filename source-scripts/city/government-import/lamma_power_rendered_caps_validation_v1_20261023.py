"""Run unchanged map terrain guards on private exact rendered seam caps."""
from pathlib import Path
import traceback
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-lamma-power-rendered-caps-validation-v1-20261023';out=base/batch;local=HERE/'local'/batch
    assert not out.exists()and not local.exists();prior='government-xl-lamma-power-rendered-seam-caps-v1-20261023';_,pins=authenticate(base/prior);refs=[Path(__file__),base/prior/'result.json']
    def take(p):
        assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
    s=take(base/prior/'summary.json');patch=take(ROOT/s['candidate']['path']);scope=take(base/prior/'scope.json');parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);refs.append(parentpath)
    result=dict(uids=s['uids'],sourceGeometryChanges=0,installationApproved=False,publication=False,newlyInstalled=0,permanentRejection=False)
    out.mkdir();save(out/'scope.json',scope)
    try:
        from float32_coverage import approve_roundoff
        from native_patch_resolution import projected_context
        _,polys,_,_=projected_context(patch,scope['bounds'])
        if shapely.union_all(polys).symmetric_difference(shapely.box(*scope['bounds'])).area:save(out/'numerical-coverage.json',approve_roundoff(patch,scope['bounds']))
        overlap=module('lamma_caps_map_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=out;overlap.overlap_proof(patch,refs.copy())
        builder=module('lamma_caps_map_builder',HERE/'resolve_pass_indexed_parent_clipping_v2.py');builder.validate_patch(patch,parent)
        faces=len(patch['nativeMesh']['index'])//3;assert faces<=25000
        candidate=local/'candidate-terrain.json';save(candidate,patch);refs.append(candidate)
        result.update(status='private-terrain-validator-passed',candidate=dict(path=str(candidate.relative_to(ROOT)),sha256=digest(candidate.read_bytes())),terrainTriangles=faces)
    except Exception as e:
        result.update(status='private-terrain-investigation',errorType=type(e).__name__,reason=str(e));save(out/'failure.json',dict(traceback=traceback.format_exc()))
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['float32_coverage.py','native_patch_resolution.py','sham_shui_po_pool_shared_terrain_v2_20261016.py','resolve_pass_indexed_parent_clipping_v2.py'])
    module('lamma_caps_validation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'private-rendered-seam-cap-map-terrain-validation',refs,result)
    print(result,flush=True)

if __name__=='__main__':main()
