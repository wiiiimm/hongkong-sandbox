"""Reproduce an original-TIN envelope failure and retain all overlap evidence."""
import argparse
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from ronsdale_local_inset_v2_20261022 import plane,lift
from exact_affine_halfplane_clip_v2_20261024 import lower_region

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','inset','capture','terrain-check','uid']:ap.add_argument('--'+k,required=True)
    a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,path):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    scope=take(a.inset,base/a.inset/'scope.json');assert scope['uids']==[a.uid];outer=shapely.box(*scope['outerBounds'])
    selected=take(a.capture,base/a.capture/'selection.json.gz');row=next(r for r in selected['rows']if r['uid']==a.uid)
    # Recreate the actual buffered source projection rather than its bounding box.
    runtime=take(a.capture,HERE/'local'/a.capture/'runtime-geometry.json.gz');g=next(r for r in runtime['rows']if r['uid']==a.uid);tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));outer=projection.buffer(1,join_style='mitre').buffer(3,join_style='mitre');assert list(outer.bounds)==scope['outerBounds']
    checked=next(r for r in take(a.terrain_check,base/a.terrain_check/'summary.json')['rows']if r['uid']==a.uid);assert checked['sourceSHA256']==row['sourceSHA256']==g['sourceSHA256']
    decoder=module('upper_overlap_original_decoder',HERE/'xl-second-pass.py');decoder.LOCAL=HERE/'local'/a.batch;source=[];planes=[];origins=[]
    for name in checked['sourceTerrainPaths']:
        path=ROOT/name;meta=take(a.terrain_check,path)
        for b in meta.get('buffers',[]):take_bytes=path.parent/b['uri'];assert digest(take_bytes.read_bytes())==pins[a.terrain_check][str(take_bytes.relative_to(ROOT))];refs.append(take_bytes)
        for index,face in enumerate(decoder.terrain_triangles(path)):
            polygon=shapely.Polygon(face[:,[0,2]])
            if polygon.area<=1e-10 or not polygon.intersects(outer):continue
            coefficients=plane(face)
            parts=lift(polygon.intersection(outer),coefficients);source.extend(parts);planes.extend(coefficients.copy()for _ in parts);origins.extend(dict(path=name,face=index,vertices=face.tolist())for _ in parts)
    polygons=shapely.polygons(np.asarray(source)[:,:,[0,2]]);tree=shapely.STRtree(polygons);upper=[];lineage=[]
    for i,polygon in enumerate(polygons):
        cuts=[]
        for j in tree.query(polygon,predicate='intersects'):
            if i==j:continue
            overlap=polygon.intersection(polygons[j])
            if overlap.area<=1e-10:continue
            if np.array_equal(planes[i],planes[j]):
                if j<i:cuts.append(overlap)
            else:cuts.append(lower_region(overlap,planes[j]-planes[i]))
        kept=polygon.difference(shapely.union_all(cuts))if cuts else polygon
        for face in lift(kept,planes[i]):upper.append(face);lineage.append(i)
    polys=shapely.polygons(np.asarray(upper)[:,:,[0,2]]);tree=shapely.STRtree(polys);pairs=[]
    for i,p in enumerate(polys):
        for j in tree.query(p,predicate='intersects'):
            if j<=i:continue
            overlap=p.intersection(polys[j])
            if overlap.area<=1e-12:continue
            left,right=planes[lineage[i]],planes[lineage[j]];point=overlap.representative_point();xz=np.asarray([point.x,point.y,1]);pairs.append(dict(left=int(i),right=int(j),areaM2=float(overlap.area),overlapWKT=overlap.wkt,equalFloatPlanes=bool(np.array_equal(left,right)),heightDifferenceAtInteriorM=float(xz@(left-right)),leftOrigin=origins[lineage[i]],rightOrigin=origins[lineage[j]],leftPlane=left.tolist(),rightPlane=right.tolist()))
    result=dict(uids=[a.uid],sourceSHA256=row['sourceSHA256'],sourceInputFragments=len(source),upperFragments=len(upper),overlapAreaM2=float(shapely.area(polys).sum()-shapely.union_all(polys).area),changedCoverageAreaM2=float(shapely.union_all(polys).symmetric_difference(shapely.union_all(polygons)).area),overlappingPairs=len(pairs),allOverlappingPairPlanesEqual=all(r['equalFloatPlanes']for r in pairs),maximumInteriorHeightDifferenceM=max((abs(r['heightDifferenceAtInteriorM'])for r in pairs),default=0),sourceGeometryChanges=0,installationApproved=False,publication=False,qualification='Exact replay of frozen producer upper-envelope construction. Every positive overlap pair retained; no epsilon increase, source repair, model edit, terrain publication or acceptance.')
    save(out/'overlap-pairs.json.gz',dict(rows=pairs));save(out/'upper-fragments.json.gz',dict(triangles=np.asarray(upper).tolist(),lineage=lineage,sourceOrigins=origins));save(out/'summary.json',result)
    refs.extend([HERE/'xl-second-pass.py',HERE/'ronsdale_local_inset_v2_20261022.py',HERE/'exact_affine_halfplane_clip_v2_20261024.py'])
    module('upper_overlap_diagnostic_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'original-tin-upper-envelope-overlap-diagnostic',refs,result);print(result,flush=True)

if __name__=='__main__':main()
