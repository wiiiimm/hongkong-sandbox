"""Bind measured numerical residue to existing private terrain policies; retain missing coverage."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-stanford-upper-runtime-candidate-v2-20261015';DOC=BASE/BATCH

def main():
 assert not DOC.exists();DOC.mkdir();prev=BASE/'government-xl-stanford-upper-terrain-candidate-v1-20261015';r=read(prev/'result.json');refs=[Path(__file__),prev/'result.json']
 for q in r['evidenceRefs']:
  p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];refs.append(p)
 p=prev/'private-patch.json.gz';patch=read(p);refs.append(p);summary=read(prev/'summary.json');m=patch['nativeMesh'];t=np.asarray(m['position'],dtype='<f4').astype(float).reshape(-1,3)[np.asarray(m['index']).reshape(-1,3)];polys=shapely.polygons(t[:,:,[0,2]]);union=shapely.union_all(polys[shapely.area(polys)>1e-10]);resolution=module('stanford_runtime_policy',HERE/'resolve-pass.py');parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);refs.extend([parentpath,HERE/'resolve-pass.py',ROOT/'3d-viewer/city/geo.js',ROOT/'3d-viewer/city/world.js',ROOT/'3d-viewer/city/native-terrain.js',HERE.parent/'island-detail-integration/native_terrain_validation.py']);bounds=resolution.extent(patch['coarseCells'],parent);missing=shapely.box(*bounds).difference(union)
 assert summary['rectangleDifferenceM2']<.25 and summary['projectedExcessM2']<.25
 m['source']['numericalCoverageGap']={'policy':'parent-grid-fallback','measuredAreaM2':summary['rectangleDifferenceM2'],'maximumAreaM2':.25}
 m['source']['numericalProjectionOverlap']={'policy':'highest-float32-surface','measuredAreaM2':summary['projectedExcessM2'],'maximumAreaM2':.25}
 patch['id']=BATCH
 try:resolution.validate_patch(patch,parent);validation={'passed':True}
 except (AssertionError,ValueError)as e:validation={'passed':False,'error':str(e)}
 recovery=read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows'];source=next(s for s in recovery if s['modelId']=='B365201779201063C0');asset=ROOT/source['asset']['path'];refs.append(asset);assert digest(asset.read_bytes())==source['sourceSHA256'];source_tri=decode_original_world_triangles(asset.read_bytes());source_polys=shapely.polygons(source_tri[:,:,[0,2]]);source_union=shapely.union_all(source_polys[shapely.area(source_polys)>1e-10]);under_source=missing.intersection(source_union);intersected=[int(i)for i in shapely.STRtree(source_polys).query(missing,predicate='intersects')]
 save(DOC/'private-patch.json.gz',patch);save(DOC/'residue.json',{'missingGeoJSON':shapely.to_geojson(missing),'underSourceGeoJSON':shapely.to_geojson(under_source),'sourceFaceIdsTouchingMissing':intersected,'sourceMissingAreaM2':float(under_source.area),'rendererDrawsGridInHoles':False,'samplerUsesGridInHoles':True,'mustReviewActualSourceAndNeighbourFallback':True})
 result={'validation':validation,'sourceMissingAreaM2':float(under_source.area),'sourceFacesTouchingMissing':len(intersected),'sourceGeometryChanges':0,'publication':False,'fullAcceptance':False,'nextAction':'Capture production terrain and complete source/actor clearance including sampler-only fallback; do not treat patch validation as installation acceptance.'};save(DOC/'summary.json',result)
 module('freeze_stanford_runtime_v2',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-existing-numerical-policy-private-candidate-v2',refs,{'uids':['landsd/305584:0','landsd/335875:0'],**result});print(result,flush=True)
if __name__=='__main__':main()
