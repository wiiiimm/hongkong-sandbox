"""Private multi-source affine original-TIN proposal across authenticated adjacent parents."""
import argparse
import json
import traceback
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from inherited_parent_coverage_v1 import qualify
from original_affine_inset_kernel_v1_20261027 import source_upper_surface, inset_parent
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','parents','terrain']:
        parser.add_argument('--'+key,required=True)
    parser.add_argument('--runtime',required=True)
    parser.add_argument('--uid',action='append',required=True)
    args=parser.parse_args()
    base=ROOT/'docs/astra-city/government-import'
    out,local=base/args.batch,HERE/'local'/args.batch
    assert args.batch.startswith('government-xl-') and '/' not in args.batch and not out.exists() and not local.exists()
    parents,pins=authenticate(base/args.parents)
    original,source_pins=authenticate(base/args.terrain)
    runtime,runtime_pins=authenticate(base/args.runtime)
    assert 1 < len(args.uid) <= 16 and len(set(args.uid)) == len(args.uid)
    assert set(args.uid).issubset(runtime['uids'])
    assert parents['uids']==['landsd/234188:0']
    refs=[Path(__file__),base/args.parents/'result.json',base/args.terrain/'result.json',
          HERE/'original_affine_inset_kernel_v1_20261027.py',HERE/'inherited_parent_coverage_v1.py',
          HERE/'float32_coverage.py',HERE/'native_patch_resolution.py',HERE/'ronsdale_local_inset_v2_20261022.py',
          HERE/'china_merchants_finite_inset_v4_20261021.py',HERE/'exact_affine_halfplane_clip_v1_20261024.py',HERE/'affine_terrain_blend_v1.py']
    summary_path=base/args.terrain/'summary.json'
    assert digest(summary_path.read_bytes())==source_pins[str(summary_path.relative_to(ROOT))]
    refs.append(summary_path)
    terrain=next(r for r in read(summary_path)['rows'] if r['uid']==parents['uids'][0])
    assert terrain['sourceSHA256']==parents['sourceSHA256']
    # Reuse only the authenticated current parent domains. Recompute the complete
    # projection from every explicitly nominated, immutable source component.
    runtime_path=HERE/'local'/args.runtime/'runtime-geometry.json.gz'
    selection_path=base/args.runtime/'selection.json.gz'
    for path in [runtime_path,selection_path]:
        assert digest(path.read_bytes())==runtime_pins[str(path.relative_to(ROOT))]
        refs.append(path)
    refs.append(base/args.runtime/'result.json')
    geometries=read(runtime_path)['rows']; selections=read(selection_path)['rows']
    projections=[]; source_shas={}
    for uid in args.uid:
        geometry=next(r for r in geometries if r['uid']==uid)
        selected=next(r for r in selections if r['uid']==uid)
        asset=ROOT/selected['candidate']['path']
        assert digest(asset.read_bytes())==geometry['sourceSHA256']==selected['sourceSHA256']
        refs.append(asset);source_shas[uid]=selected['sourceSHA256']
        triangles=np.asarray(geometry['position']).reshape(-1,3)[np.asarray(geometry['index']).reshape(-1,3)]
        assert len(triangles)==selected['triangles'] and np.isfinite(triangles).all()
        projections.append(shapely.union_all(shapely.polygons(triangles[:,:,[0,2]])))
    projection=shapely.union_all(projections)
    core=projection.buffer(1,join_style='mitre')
    outer=core.buffer(3,join_style='mitre')
    domains=[shapely.box(*r['bounds']) for r in parents['rows']]
    for i,region in enumerate(domains):
        assert all(region.intersection(other).area==0 for other in domains[:i])
    domain=shapely.union_all(domains)
    assert domain.covers(outer) and outer.distance(domain.boundary)>0
    decoder=module('partitioned_original_tin_decoder',HERE/'xl-second-pass.py');decoder.LOCAL=local
    refs.append(HERE/'xl-second-pass.py')
    source=[]
    for name in terrain['sourceTerrainPaths']:
        path=ROOT/name;assert digest(path.read_bytes())==source_pins[name];refs.append(path)
        for buffer in read(path).get('buffers',[]):
            member=path.parent/buffer['uri'];assert digest(member.read_bytes())==source_pins[str(member.relative_to(ROOT))];refs.append(member)
        source.append(decoder.terrain_triangles(path))
    result=dict(uids=args.uid,sourceSHA256ByUid=source_shas,outerWKT=outer.wkt,rawProjectionAreaM2=projection.area,rows=[],
                publication=False,installationApproved=False,sourceGeometryChanges=0,
                qualification='Private derived terrain faces only. Model bytes unchanged. Coverage, area conservation and unchanged-parent facets checked; coordinated seam, canonical patch construction, retained supports, identity and browser acceptance remain separate.')
    try:
        upper,planes=source_upper_surface(np.concatenate(source),projection,core,outer)
        for row in parents['rows']:
            path=ROOT/row['capturePath'];assert digest(path.read_bytes())==row['captureSHA256'];refs.append(path)
            baseline=np.asarray(read(path)['triangles'],float)
            output,lineage=inset_parent(baseline,upper,planes,core,outer)
            coverage=qualify(output,row['bounds'])
            unchanged=[(i,p['parentFace']) for i,p in enumerate(lineage['outputLineage']) if p['kind']=='unchanged']
            assert all(np.array_equal(output[i],baseline[j]) for i,j in unchanged)
            dest=local/('private-faces-'+str(row['index'])+'.json.gz');save(dest,dict(triangles=output.tolist(),lineage=lineage));refs.append(dest)
            result['rows'].append(dict(index=row['index'],bounds=row['bounds'],parentFaces=len(baseline),
                privateFaces=len(output),changedParentFaces=len(lineage['changedParentFaces']),
                exactUnchangedParentFaces=len(unchanged),coverage=coverage,
                removedAreaM2=lineage['removedAreaM2'],insertedAreaM2=lineage['insertedAreaM2'],
                privateFacesPath=str(dest.relative_to(ROOT)),privateFacesSHA256=digest(dest.read_bytes())))
            print('Completed private partition',row['index'],len(output),flush=True)
        result['status']='private-partition-faces-coverage-passed'
    except Exception as error:
        result.update(status='bounded-partition-inset-investigation',reason=str(error),errorType=type(error).__name__)
        save(out/'failure.json',dict(errorType=type(error).__name__,message=str(error),traceback=traceback.format_exc()))
    for mapping in [pins,source_pins,runtime_pins]:
        for name,sha in mapping.items():assert digest((ROOT/name).read_bytes())==sha
    result=json.loads(json.dumps(result));save(out/'summary.json',result)
    module('partitioned_inset_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch,'private-original-partitioned-affine-inset-proposal',list(dict.fromkeys(refs)),result)
    print(dict(status=result['status'],reason=result.get('reason')),flush=True)


if __name__=='__main__':main()
