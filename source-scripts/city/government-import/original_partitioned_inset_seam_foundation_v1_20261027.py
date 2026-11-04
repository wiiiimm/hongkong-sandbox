"""Diagnostic exact partition seam and whole-source foundation; no acceptance."""
import argparse
import json
from fractions import Fraction
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_native_upper_surface_pair_seam_v3_20261010 import verify_pair
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','candidate','runtime']:
        parser.add_argument('--'+key,required=True)
    args=parser.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/args.batch
    assert args.batch.startswith('government-xl-') and '/' not in args.batch and not out.exists()
    candidate,pins=authenticate(base/args.candidate);runtime,runtime_pins=authenticate(base/args.runtime)
    assert candidate['status']=='private-partition-faces-coverage-passed' and len(candidate['rows'])==2
    assert candidate['uids']==runtime['uids']==['landsd/234188:0']
    refs=[Path(__file__),base/args.candidate/'result.json',base/args.runtime/'result.json',
          HERE/'exact_native_upper_surface_pair_seam_v3_20261010.py',HERE/'xl-final-script-pass.py']
    parts=[]
    for row in candidate['rows']:
        path=ROOT/row['privateFacesPath'];assert digest(path.read_bytes())==row['privateFacesSHA256'];refs.append(path)
        parts.append(np.asarray(read(path)['triangles'],float))
    a,b=candidate['rows'];assert a['bounds'][1]==b['bounds'][3]
    z=a['bounds'][1];x0=max(a['bounds'][0],b['bounds'][0]);x1=min(a['bounds'][2],b['bounds'][2]);assert x0<x1
    segment=np.asarray([[x0,0,z],[x1,0,z]])
    seams=[]
    for name,values in [('raw',parts),('renderedFloat32',[p.astype('float32').astype(float) for p in parts])]:
        proof=verify_pair(segment,*values);save(out/('seam-'+name+'.json.gz'),proof)
        gaps=[abs(Fraction(r['exactGapM'])) for r in proof['completeClosedPointsAndAffineOpenIntervals'] if r['exactGapM'] is not None]
        seams.append(dict(mode=name,passed=proof['passedCompleteFiniteUpperSeam'],
                          checks=len(proof['completeClosedPointsAndAffineOpenIntervals']),maxFiniteGapM=float(max(gaps)) if gaps else None))
    path=HERE/'local'/args.runtime/'runtime-geometry.json.gz';assert digest(path.read_bytes())==runtime_pins[str(path.relative_to(ROOT))];refs.append(path)
    geometry=read(path)['rows'][0];assert geometry['sourceSHA256']==candidate['sourceSHA256']
    tri=np.asarray(geometry['position']).reshape(-1,3)[np.asarray(geometry['index']).reshape(-1,3)]
    selection_path=base/args.runtime/'selection.json.gz';assert digest(selection_path.read_bytes())==runtime_pins[str(selection_path.relative_to(ROOT))];refs.append(selection_path)
    building=read(selection_path)['rows'][0]['source']['building'];target=shapely.Polygon(building['rings'][0],building['rings'][1:])
    kernel=module('partitioned_foundation_kernel',HERE/'xl-final-script-pass.py');ground=np.concatenate(parts);foundations=[]
    for name,terrain in [('raw',ground),('renderedFloat32',ground.astype('float32').astype(float))]:
        foundation=kernel.foundation_context(tri,terrain,target);save(out/('foundation-'+name+'.json'),foundation)
        foundations.append(dict(mode=name,**{k:foundation[k] for k in ['completeTerrainTriangles','fullyBuriedTriangles','fullyBuriedUpwardTriangles','minimumGapM']}))
    for binding in [pins,runtime_pins]:
        for name,sha in binding.items():assert digest((ROOT/name).read_bytes())==sha
    result=dict(uids=candidate['uids'],sourceSHA256=candidate['sourceSHA256'],seams=seams,foundations=foundations,
                installationApproved=False,publication=False,sourceGeometryChanges=0,
                qualification='Exact full seam upper-envelope and current captured whole-source foundation diagnostics only. Not canonical patch validation, four-world acceptance, retained-actor regression, identity approval or browser acceptance.')
    result=json.loads(json.dumps(result));save(out/'summary.json',result)
    module('partitioned_seam_foundation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch,'private-partitioned-inset-exact-seam-and-source-foundation',list(dict.fromkeys(refs)),result)
    print(dict(seams=seams,foundations=foundations),flush=True)


if __name__=='__main__':main()
