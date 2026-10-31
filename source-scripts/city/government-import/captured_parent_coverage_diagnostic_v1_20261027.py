"""Measure saved parent-domain holes in raw and rendered Float32 space; no repair."""
import argparse
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from native_patch_resolution import projected_context
from primrose_compound_foundation_v2_20261015 import module


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','proposal']:ap.add_argument('--'+k,required=True)
    a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()
    receipt,pins=authenticate(base/a.proposal);refs=[Path(__file__),base/a.proposal/'result.json']
    scopepath=base/a.proposal/'scope.json';parentpath=HERE/'local'/a.proposal/'parent.json'
    for p in [scopepath,parentpath]:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
    scope,parent=read(scopepath),read(parentpath);assert parent['domain']==scope['bounds']
    for path,sha in parent['inputHashes'].items():p=ROOT/path;assert digest(p.read_bytes())==sha;refs.append(p)
    tri=np.asarray(parent['triangles'],dtype='<f8');assert tri.ndim==3 and tri.shape[1:]==(3,3)and np.isfinite(tri).all()
    domain=shapely.box(*scope['bounds']);raw=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));patch=dict(nativeMesh=dict(position=tri.reshape(-1).tolist(),index=list(range(tri.size//3)),source={}))
    _,polygons,_,_=projected_context(patch,scope['bounds']);rendered=shapely.union_all(polygons)
    core=shapely.box(*scope['coreBounds']);outer=shapely.box(*scope['outerBounds']);rows=[]
    for mode,coverage in [('raw',raw),('renderedFloat32',rendered)]:
        missing=domain.difference(coverage);excess=coverage.difference(domain);parts=[p for p in shapely.get_parts(missing)if p.area>0]
        save(out/(mode+'-missing.geojson'),json_object:=__import__('json').loads(shapely.to_geojson(missing)))
        rows.append(dict(mode=mode,completeParentFaces=len(tri),missingAreaM2=float(missing.area),outsideDomainAreaM2=float(excess.area),symmetricDifferenceM2=float(coverage.symmetric_difference(domain).area),missingCoreBoundingBoxAreaM2=float(missing.intersection(core).area),missingOuterBoundingBoxAreaM2=float(missing.intersection(outer).area),missingComponents=[dict(areaM2=float(p.area),bounds=list(p.bounds),touchesDomainBoundary=bool(p.intersects(domain.boundary)))for p in sorted(parts,key=lambda p:-p.area)],missingBoundaries=[list(p.exterior.coords)for p in parts if p.geom_type=='Polygon']))
    result=dict(uids=receipt['uids'],proposal=a.proposal,parentGeometrySHA256=digest(tri.tobytes()),domainBounds=scope['bounds'],rows=rows,rawRenderedProjectionSymmetricDifferenceM2=float(raw.symmetric_difference(rendered).area),sourceGeometryChanges=0,terrainGeometryChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Complete saved parent face projections only. Both raw and actual Float32 projection differences are measured without rounding-credit or threshold changes. Core/outer intersections are bounding-box diagnostics, not exact edit masks. Boundary contact alone does not prove coastline, NoData or a harmless gap. No geometry repair, missing-face fill or acceptance granted.')
    save(out/'summary.json',result);refs.append(HERE/'native_patch_resolution.py')
    module('captured_parent_coverage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-saved-parent-raw-and-rendered-domain-coverage-diagnostic',refs,result)
    print([{k:r[k]for k in ['mode','missingAreaM2','outsideDomainAreaM2','missingCoreBoundingBoxAreaM2']}for r in rows],flush=True)

if __name__=='__main__':main()
