"""Diagnostic every shared partition boundary and nominated whole source; no acceptance."""
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
    parser.add_argument('--uid',action='append',required=True)
    args=parser.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/args.batch
    assert args.batch.startswith('government-xl-') and '/' not in args.batch and not out.exists()
    candidate,pins=authenticate(base/args.candidate);runtime,runtime_pins=authenticate(base/args.runtime)
    assert candidate['status']=='private-partition-faces-coverage-passed' and 1 < len(candidate['rows']) <= 8
    assert 1 < len(args.uid) <= 16 and len(args.uid)==len(set(args.uid))
    assert set(candidate['uids']) <= set(args.uid) <= set(runtime['uids'])
    refs=[Path(__file__),base/args.candidate/'result.json',base/args.runtime/'result.json',
          HERE/'exact_native_upper_surface_pair_seam_v3_20261010.py',HERE/'xl-final-script-pass.py']
    parts=[]
    for row in candidate['rows']:
        path=ROOT/row['privateFacesPath'];assert digest(path.read_bytes())==row['privateFacesSHA256'];refs.append(path)
        parts.append(np.asarray(read(path)['triangles'],float))
    seams=[]
    connected=set()
    for i,left in enumerate(candidate['rows']):
        for j in range(i+1,len(candidate['rows'])):
            right=candidate['rows'][j]
            intersection=shapely.box(*left['bounds']).intersection(shapely.box(*right['bounds']))
            assert intersection.area==0, 'Partition interiors overlap'
            if intersection.is_empty:
                continue
            assert intersection.geom_type in ['LineString','Point'], 'Non-rectangular shared boundary'
            coordinates=list(intersection.coords)
            assert 1 <= len(coordinates) <= 2
            start,end=coordinates[0],coordinates[-1]
            segment=np.asarray([[start[0],0,start[1]],[end[0],0,end[1]]])
            connected.update([i,j])
            for name,values in [('raw',parts),('renderedFloat32',[p.astype('float32').astype(float) for p in parts])]:
                proof=verify_pair(segment,values[i],values[j])
                save(out/('seam-'+str(i)+'-'+str(j)+'-'+name+'.json.gz'),proof)
                gaps=[abs(Fraction(r['exactGapM'])) for r in proof['completeClosedPointsAndAffineOpenIntervals'] if r['exactGapM'] is not None]
                seams.append(dict(left=i,right=j,segment=segment.tolist(),mode=name,passed=proof['passedCompleteFiniteUpperSeam'],
                                  checks=len(proof['completeClosedPointsAndAffineOpenIntervals']),maxFiniteGapM=float(max(gaps)) if gaps else None))
    assert connected==set(range(len(parts))), 'An isolated partition has no checked boundary'
    path=HERE/'local'/args.runtime/'runtime-geometry.json.gz';assert digest(path.read_bytes())==runtime_pins[str(path.relative_to(ROOT))];refs.append(path)
    geometries=read(path)['rows']
    selection_path=base/args.runtime/'selection.json.gz';assert digest(selection_path.read_bytes())==runtime_pins[str(selection_path.relative_to(ROOT))];refs.append(selection_path)
    selections=read(selection_path)['rows']
    kernel=module('partitioned_foundation_kernel',HERE/'xl-final-script-pass.py');ground=np.concatenate(parts);foundations=[];source_shas={}
    for uid in args.uid:
        geometry=next(g for g in geometries if g['uid']==uid)
        selected=next(r for r in selections if r['uid']==uid)
        asset=ROOT/selected['candidate']['path'];refs.append(asset)
        assert digest(asset.read_bytes())==geometry['sourceSHA256']==selected['sourceSHA256']
        if uid in candidate['uids']:
            assert candidate['sourceSHA256ByUid'][uid]==selected['sourceSHA256']
        source_shas[uid]=selected['sourceSHA256']
        tri=np.asarray(geometry['position']).reshape(-1,3)[np.asarray(geometry['index']).reshape(-1,3)]
        assert len(tri)==selected['triangles'] and np.isfinite(tri).all()
        building=selected['source']['building'];target=shapely.Polygon(building['rings'][0],building['rings'][1:])
        for name,terrain in [('raw',ground),('renderedFloat32',ground.astype('float32').astype(float))]:
            foundation=kernel.foundation_context(tri,terrain,target)
            save(out/('foundation-'+uid.replace('/','-').replace(':','-')+'-'+name+'.json'),foundation)
            foundations.append(dict(uid=uid,mode=name,**{k:foundation[k] for k in ['completeTerrainTriangles','fullyBuriedTriangles','fullyBuriedUpwardTriangles','minimumGapM']}))
    for binding in [pins,runtime_pins]:
        for name,sha in binding.items():assert digest((ROOT/name).read_bytes())==sha
    result=dict(uids=args.uid,terrainEditOwnerUids=candidate['uids'],sourceSHA256ByUid=source_shas,seams=seams,foundations=foundations,
                installationApproved=False,publication=False,sourceGeometryChanges=0,
                qualification='Exact full seam upper-envelope and current captured whole-source foundation diagnostics only. Not canonical patch validation, four-world acceptance, retained-actor regression, identity approval or browser acceptance.')
    result=json.loads(json.dumps(result));save(out/'summary.json',result)
    module('complete_partition_seam_foundation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch,'private-partitioned-inset-exact-seam-and-source-foundation',list(dict.fromkeys(refs)),result)
    print(dict(seams=seams,foundations=foundations),flush=True)


if __name__=='__main__':main()
