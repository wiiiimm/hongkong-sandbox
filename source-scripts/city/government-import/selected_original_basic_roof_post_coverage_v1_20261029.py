"""Measure complete original roof and actual BASIC post coverage; no approval."""
import argparse
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from component_roof_coverage import above_height_projection

def main():
    p=argparse.ArgumentParser()
    for key in ['batch','runtime','attributes','foreign','uid','basic']:p.add_argument('--'+key,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,p):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selection=take(a.runtime,base/a.runtime/'selection.json.gz');row=next(r for r in selection['rows']if r['uid']==a.uid)
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
    attr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.uid)
    assert attr['sourceSHA256']==row['sourceSHA256'];index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    basic=next(r for r in take(a.foreign,base/a.foreign/'basic.json')['rows']if r['uid']==a.basic)
    bt=np.asarray(basic['position']).reshape(-1,3)[np.asarray(basic['index']).reshape(-1,3)]
    top=float(bt[:,:,1].max());bottom=float(bt[:,:,1].min());caps=bt[(bt[:,:,1]==bottom).all(1)];roofs=bt[(bt[:,:,1]==top).all(1)]
    assert len(caps)>0 and len(roofs)>0 and top>bottom
    posts=shapely.union_all(shapely.polygons(caps[:,:,[0,2]]));roof=shapely.union_all(shapely.polygons(roofs[:,:,[0,2]]));assert posts.area>0 and roof.area>0
    worlds={'original':decode_original_world_triangles(asset.read_bytes())}
    for k,f in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[k]=np.asarray(attr[f]).reshape(-1,3)[index]
    rows=[]
    for mode,tri in worlds.items():
        n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);up=tri[n[:,1]>0]
        high=above_height_projection(tri,top);uphigh=above_height_projection(up,top);complete=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))
        result=dict(mode=mode,sourceWorldSHA256=digest(tri.astype('<f8').tobytes()),completeFaces=len(tri),upwardFaces=len(up))
        for label,target,projection in [('fullFootprint',roof,complete),('roofAboveBasicTop',roof,high),('upwardRoofAboveBasicTop',roof,uphigh),('postsUnderSourceAboveBasicTop',posts,high),('postsUnderUpwardSourceAboveBasicTop',posts,uphigh)]:
            gap=target.difference(projection);result[label]=dict(targetAreaM2=float(target.area),coveredAreaM2=float(target.intersection(projection).area),missingAreaM2=float(gap.area),missingSetEmpty=bool(gap.is_empty),covers=bool(projection.covers(target)))
            if not gap.is_empty:save(out/(mode+'-'+label+'-missing.json'),dict(wkt=gap.wkt))
        rows.append(result)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    result=dict(uids=[a.uid],basicUid=a.basic,sourceSHA256=row['sourceSHA256'],basicTopHKPD=top,basicBottomHKPD=bottom,basicBottomCapTriangles=len(caps),basicRoofTriangles=len(roofs),rows=rows,counterpartSuppressionApproved=False,supportAccepted=False,identityAccepted=False,installationApproved=False,publication=False,sourceGeometryChanges=0,basicGeometryChanges=0,qualification='Complete exact original and three current coordinate representations measured against actual captured BASIC roof and post-cap polygons. No buffers, area tolerance, corner sampling or suppression credit; height-plane projection is not architectural identity/support/collision evidence.')
    save(out/'summary.json',result);refs.extend([HERE/'component_roof_coverage.py',HERE/'exact_packed_world_geometry_20261009.py'])
    module('source_basic_roof_post_coverage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-four-world-original-actual-basic-roof-post-coverage-diagnostic',refs,result)
    print(result,flush=True)
if __name__=='__main__':main()
