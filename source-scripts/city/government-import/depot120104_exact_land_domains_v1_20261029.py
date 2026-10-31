"""Prove land-only candidate domains; no terrain construction or publication."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_land_cell_rectangles_v1_20261029 import partition
from inherited_parent_coverage_v1 import qualify
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-depot120104-exact-land-domains-v1-20261029'
FAILED='government-xl-depot120104-terrain-sequence-v1-20261029-120104-0-inset'
CURRENT='government-xl-oceanwalk-depot-current-v1-20261029'
UID='landsd/120104:0'


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    scope=take(FAILED,BASE/FAILED/'scope.json');capture=take(FAILED,HERE/'local'/FAILED/'parent.json')
    faces=np.asarray(capture['triangles'],dtype='<f8');land=shapely.union_all(shapely.polygons(faces[:,:,[0,2]]));extent=shapely.box(*scope['bounds']);missing=extent.difference(land)
    assert missing.area==19600 and land.difference(extent).is_empty
    selection=take(CURRENT+'-runtime',BASE/(CURRENT+'-runtime')/'selection.json.gz');source=next(r for r in selection['rows']if r['uid']==UID)
    attr=next(r for r in take(CURRENT+'-attributes',BASE/(CURRENT+'-attributes')/'attributes.json.gz')['rows']if r['uid']==UID)
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==attr['sourceSHA256']==source['sourceSHA256'];refs.append(asset)
    ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);literal=np.asarray(attr['completeLiteralWorldPosition']).reshape(-1,3);original=literal.copy();original[ix.ravel()]=decode_original_world_triangles(asset.read_bytes()).reshape(-1,3)
    worlds=[original,literal,np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1,3),np.asarray(attr['completeExplicitBalancedFloat32WorldPosition']).reshape(-1,3)]
    projections=[shapely.union_all(shapely.polygons(p[ix][:,:,[0,2]]))for p in worlds]
    projection=shapely.union_all(projections);core=projection.buffer(1,join_style='mitre');outer=core.buffer(3,join_style='mitre')
    assert projection.intersection(missing).is_empty and outer.intersection(missing).is_empty and projection.distance(missing)>72
    rects,polys=partition(land,scope['bounds'],scope['cells'],outer);assert len(rects)==3
    assert rects==[[231,414,236,415],[229,415,236,416],[228,416,236,420]]
    pieces=[];assigned=set();edges=[];out.mkdir()
    face_polys=shapely.polygons(faces[:,:,[0,2]])
    for i,(cells,poly)in enumerate(zip(rects,polys)):
        selected=[j for j,p in enumerate(face_polys)if poly.covers(p)]
        assert selected and not assigned.intersection(selected);assigned.update(selected)
        proof=qualify(faces[selected],list(poly.bounds))
        assert proof['rawOverlayDifferenceM2']==proof['renderedFloat32DifferenceM2']==0
        pieces.append(dict(member=i,coarseCells=cells,bounds=list(poly.bounds),parentFaceIds=selected,parentCoverage=proof))
        for j,other in enumerate(polys[:i]):
            shared=poly.boundary.intersection(other.boundary)
            if shared.length:
                assert shared.geom_type=='LineString';edges.append(dict(left=j,right=i,sharedEdgeWKT=shared.wkt,lengthM=shared.length))
    assert assigned==set(range(len(faces)))and len(edges)==2
    assert sorted(sum(i in [e['left'],e['right']]for e in edges)for i in range(3))==[1,1,2]
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    result=dict(uids=[UID],sourceSHA256=source['sourceSHA256'],currentManifestSHA256=selection['manifestSHA256'],
                parentLandFacets=len(faces),omittedWaterAreaM2=missing.area,omittedWaterWKT=missing.wkt,
                minimumFourWorldSourceDistanceToOmittedWaterM=projection.distance(missing),
                sourceAndFourMetreReturnRegionEntirelyOnLand=True,members=pieces,sharedEdges=edges,
                exactLandUnionRetained=True,allThreeOrdinaryParentCoverageChecksPassed=True,
                readyForPrivateThreeMemberInset=True,sourceGeometryChanges=0,terrainGeometryChanges=0,
                coverageExceptionsAdded=0,installationApproved=False,publication=False,
                qualification='The failed whole rectangle includes four absent coastal grid cells, not defective model/TIN geometry. Three non-overlapping rectangles preserve the exact existing88-facet land union and omit all19600m2 of water. All four source coordinate representations plus the1mcore/3mreturn are supported on that land, over72m from the omitted water. Each rectangle independently passes unchanged parent coverage rules with zero residue. Next construct one globally consistent original-TIN inset and prove both shared native boundaries; domains alone are not terrain or approval.')
    save(out/'summary.json',result);refs.extend([HERE/'exact_land_cell_rectangles_v1_20261029.py',HERE/'test_exact_land_cell_rectangles_v1_20261029.py',HERE/'inherited_parent_coverage_v1.py',HERE/'float32_coverage.py',HERE/'exact_packed_world_geometry_20261009.py'])
    module('depot_land_domains_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-coast-preserving-three-domain-original-inset-plan',refs,result)


if __name__=='__main__':main()
