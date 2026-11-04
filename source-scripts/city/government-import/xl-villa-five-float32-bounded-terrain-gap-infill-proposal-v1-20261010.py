"""Construct bounded conservative terrain infill under complete Villa projection cracks.

Keep every existing terrain record/index and every original building byte. New
Float32 rectangles cover the full measured gaps and lie below every intersected
old terrain facet vertex and upward original/runtime source facet vertex. Full
independent physical/clearance/root checks remain required; no tolerance credit.
"""
import importlib.util,json
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from native_patch_resolution import _faces
from bounded_float32_terrain_gap_boxes_20261010 import bounded_boxes,down,up
BASE=ROOT/'docs/astra-city/government-import'
PHYSICAL=BASE/'government-xl-villa-five-original-coupled-physical-v2-20261010'
FINITE=BASE/'government-xl-villa-five-original-and-rendered-paired-finite-v2-20261010'
BATCH='government-xl-villa-five-float32-bounded-terrain-gap-infill-proposal-v1-20261010';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS={'landsd/89917:0','landsd/58497:0','landsd/121309:0','landsd/148052:0'}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
    assert not DOC.exists() and not LOCAL.exists()
    manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest)
    selection=read(PHYSICAL/'selection.json.gz');assert selection['manifestSHA256']==start['sha256']
    candidate=read(PHYSICAL/'terrain-candidates.json')[0];path=ROOT/candidate['path'];assert ref(path)['sha256']==candidate['sha256']
    patch=read(path);before=_faces(patch);original_position=list(patch['nativeMesh']['position']);original_index=list(patch['nativeMesh']['index'])
    runtime_path=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';runtime=read(runtime_path)['rows']
    old_polys=shapely.polygons(before[:,:,[0,2]]);old_union=shapely.union_all(old_polys[shapely.area(old_polys)>0])
    complete=[];assets=[]
    for row in selection['rows']:
        asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];assets.append(asset)
        source=decode_original_world_triangles(raw);r=next(r for r in runtime if r['uid']==row['uid']);actual=np.asarray(r['position'],float).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]
        assert source.shape==actual.shape
        for tri in [source,actual]:
            n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);lens=np.linalg.norm(n,axis=1)
            complete.append(tri[(lens>0)&(n[:,1]>.25*lens)])
    upward=np.concatenate(complete);up_polys=shapely.polygons(upward[:,:,[0,2]])
    proofs=[];new_faces=[]
    for row in runtime:
        if row['uid'] not in UIDS:continue
        tri=np.asarray(row['position'],float).reshape(-1,3)[np.asarray(row['index']).reshape(-1,3)]
        ground=np.asarray(row['drawnGroundGeometry'],float).reshape(-1,3,3)
        projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));gap=projection.difference(shapely.union_all(shapely.polygons(ground[:,:,[0,2]])))
        assert gap.area>0
        # Establish these are actual candidate holes, not bounded checker omissions.
        global_gap=projection.difference(old_union);assert global_gap.area>0
        rectangles=[];subdivision_records=[]
        bounded=[]
        for complete_part in shapely.get_parts(gap):
            assert complete_part.geom_type=='Polygon' and complete_part.area>0
            pieces,accounting=bounded_boxes(complete_part)
            subdivision_records.append(dict(completeGapWKT=shapely.to_wkt(complete_part,rounding_precision=-1),positiveAreaM2=float(complete_part.area),**accounting))
            bounded.extend(pieces)
        for part,box in bounded:
            x0,z0,x1,z1=box.bounds
            assert 0<part["positiveAreaM2"]<.0001 and box.area<.1
            ids=np.flatnonzero(shapely.intersects(old_polys,box));assert len(ids)
            roofs=np.flatnonzero(shapely.intersects(up_polys,box))
            level=float(before[ids,:,1].min())
            if len(roofs):level=min(level,float(upward[roofs,:,1].min()))
            level=down(level)
            points=np.asarray([[x0,level,z0],[x1,level,z0],[x0,level,z1],[x1,level,z1]],float)
            faces=points[np.asarray([[0,2,1],[1,2,3]])]
            assert np.array_equal(faces.astype(np.float32).astype(float),faces)
            new_faces.extend(faces.tolist());rectangles.append(dict(exactClippedGap=part,literalFloat32Rectangle=faces.tolist(),allIntersectedOriginalTerrainFacets=ids.tolist(),allIntersectedCompleteOriginalAndLiteralUpwardFaces=roofs.tolist(),conservativeTerrainLevelM=level,originalTerrainMinimumVertexY=float(before[ids,:,1].min())))
        proofs.append(dict(uid=row['uid'],completeOriginalFaces=len(tri),completeBoundedDrawnGroundSHA256=digest(ground.tobytes()),positiveGapAreaM2=float(gap.area),completeCandidateGapAreaM2=float(global_gap.area),rectangles=rectangles,completeGapSubdivision=subdivision_records))
    assert {p['uid'] for p in proofs}==UIDS and new_faces
    flat=np.asarray(new_faces,float).reshape(-1,3);offset=len(original_position)//3
    patch['nativeMesh']['position'].extend(flat.reshape(-1).tolist());patch['nativeMesh']['index'].extend(range(offset,offset+len(flat)))
    assert patch['nativeMesh']['position'][:len(original_position)]==original_position and patch['nativeMesh']['index'][:len(original_index)]==original_index
    assert len(patch['nativeMesh']['index'])//3<100000
    output=LOCAL/'government-native-89917-0.json';save(output,patch);save(DOC/'terrain-candidates.json',[{**candidate,'path':str(output.relative_to(ROOT)),'sha256':ref(output)['sha256']}])
    result=dict(rows=proofs,originalTerrainRecordsAndIndicesUnchanged=True,addedTerrainTriangles=len(new_faces),completeCandidateTerrainFaces=len(patch['nativeMesh']['index'])//3,sourceGeometryChanges=0,proposalCreated=True,constructionLimitsUnchanged=dict(positivePieceAreaM2=.0001,outwardRectangleAreaM2=.1,terrainFaceBudget=100000),surfaceUnchangedClaim=False,independentCompleteFiniteProofRequired=True,currentAcceptancePassed=False,fullAcceptance=False,installationApproved=False,publication=False)
    save(DOC/'diagnostic.json.gz',result);assert ref(manifest)==start
    refs=[Path(__file__),manifest,path,output,PHYSICAL/'selection.json.gz',PHYSICAL/'result.json',FINITE/'result.json',FINITE/'diagnostic.json.gz',runtime_path,HERE/'bounded_float32_terrain_gap_boxes_20261010.py',HERE/'test_bounded_float32_terrain_gap_boxes_20261010.py',HERE/'native_patch_resolution.py',HERE/'exact_packed_world_geometry_20261009.py',*assets]
    s=importlib.util.spec_from_file_location('float32_terrain_seam_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    m.freeze(BATCH,'complete-villa-bounded-float32-terrain-only-conservative-gap-infill-proposal-v1',refs,{**result,'rowsSummary':[dict(uid=r['uid'],positiveGapAreaM2=r['positiveGapAreaM2']) for r in proofs],'uids':[r['uid'] for r in selection['rows']],'manifestSHA256':start['sha256'],'humanStatus':'held-for-compute','humanDecisionRequired':False,'aiGeometryModellingRequired':False})
    print(json.dumps(dict(addedTerrainTriangles=len(new_faces),terrainSHA256=ref(output)['sha256'],completeCandidateTerrainFaces=result['completeCandidateTerrainFaces'],publication=False)),flush=True)
if __name__=='__main__':main()
