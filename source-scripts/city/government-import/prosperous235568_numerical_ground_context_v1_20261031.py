"""Measure source clearance over existing declared numerical grid fallback gaps."""
import copy,subprocess
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from float32_coverage import approve_roundoff
from native_patch_resolution import projected_context
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-prosperous235568-';BATCH=P+'numerical-ground-context-v1-20261031'

def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    runtime=P+'six-original-patch-runtime-v1-20261031';attrs=P+'six-original-attributes-v1-20261031';patchbatch='government-xl-after-villa-premiere-235568-source-floor-return-v1-20261031'
    selection=take(runtime,BASE/runtime/'selection.json.gz');attributes={r['uid']:r for r in take(attrs,BASE/attrs/'attributes.json.gz')['rows']}
    summary=take(patchbatch,BASE/patchbatch/'summary.json');path=ROOT/summary['candidate']['path'];patch=take(patchbatch,path);assert digest(path.read_bytes())==summary['candidate']['sha256']
    parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);refs.append(parentpath);helper=module('prosperous_existing_grid_extent',HERE/'resolve_pass_indexed_parent_clipping_v2.py');bounds=helper.extent(patch['coarseCells'],parent)
    declared=patch['nativeMesh']['source']['numericalCoverageGap'];replayed=approve_roundoff(copy.deepcopy(patch),bounds);assert replayed==declared
    native,polygons,missing,_=projected_context(patch,bounds);assert missing.area<=.25 and declared['maximumRoundoffDistanceM']==.002
    out.mkdir();gridpath=out/'production-grid-fallback.json.gz';tool=HERE/'native_grid_height_fallback_capture_v1_20261029.mjs';refs.append(tool);subprocess.run(['node',str(tool),str(path.relative_to(ROOT)),str(gridpath.relative_to(ROOT))],cwd=ROOT,check=True)
    grid=read(gridpath);assert grid['sourceSHA256']==summary['candidate']['sha256'];ground=np.asarray(grid['position'],dtype='<f8').reshape(-1,3)[np.asarray(grid['index']).reshape(-1,3)];gp=shapely.polygons(ground[:,:,[0,2]]);assert missing.difference(shapely.union_all(gp)).is_empty
    rows=[]
    for source in selection['rows']:
        attr=attributes[source['uid']]
        asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']==attr['sourceSHA256'];refs.append(asset);ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
        worlds=dict(original=decode_original_world_triangles(asset.read_bytes()),**{m:np.asarray(attr[f],dtype='<f8').reshape(-1,3)[ix]for m,f in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]})
        def heights(t,points):
            n=np.cross(t[1]-t[0],t[2]-t[0]);assert n[1]!=0;return t[0,1]-(n[0]*(points[:,0]-t[0,0])+n[2]*(points[:,1]-t[0,2]))/n[1]
        for mode,tri in worlds.items():
            projections=shapely.polygons(tri[:,:,[0,2]]);valid=shapely.area(projections)>1e-10;parts=[]
            for face in np.flatnonzero(valid&shapely.intersects(projections,missing)):
                region=projections[face].intersection(missing)
                if region.area<=0:continue
                values=[];clips=[]
                for j in np.flatnonzero(shapely.intersects(gp,region)):
                    part=gp[j].intersection(region);points=shapely.get_coordinates(part)
                    if not len(points):continue
                    values.extend((heights(tri[face],points)-heights(ground[j],points)).tolist());clips.append(int(j))
                assert values;parts.append(dict(sourceFace=int(face),rawMissingProjectionAreaM2=region.area,gridFacetIds=clips,minimumGridFallbackGapM=min(values),maximumGridFallbackGapM=max(values),passesExistingMinimumClearance=min(values)>=-.5))
            rows.append(dict(uid=source['uid'],mode=mode,completeSourceFaces=len(tri),sourceWorldSHA256=digest(tri.tobytes()),sourceFacesOverNumericalGaps=parts,allGridFallbackClear=all(p['passesExistingMinimumClearance']for p in parts)))
    for p,h in grid['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    result=dict(uids=sorted(attributes),sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in selection['rows']},sourceGeometryChanges=0,sourcePoseChanges=0,declaredCoveragePolicyReproduced=True,nativeMissingAreaM2=float(missing.area),nativeGapsRemainUnfilled=True,allFourGridFallbackClear=all(r['allGridFallbackClear']for r in rows),rows=rows,installationApproved=False,physicalAcceptance=False,publication=False,qualification='Existing0.25m2/2mm policy independently reproduced on the exact candidate. Every positive-area source-face intersection with the declared missing native regions is clipped to every actual production grid-height fallback facet; affine source-minus-grid extrema retain the existing-.5m clearance bound in all four source coordinate streams. This records height-sampler fallback, not a claim that holes are drawn mesh or that raw native coverage is complete. Original model and terrain assets remain unchanged; source roles, full neighbour and publisher acceptance remain separate.')
    save(out/'summary.json',result);refs.extend([HERE/'float32_coverage.py',HERE/'native_patch_resolution.py',HERE/'resolve_pass_indexed_parent_clipping_v2.py'])
    module('prosperous_numerical_ground_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'existing-numerical-gap-four-world-production-grid-height-fallback-context',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
