"""Measure complete original podium against exact current individual/group footprints."""
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-siu-hong-footprint-extent-v1-20261021';DOC=BASE/BATCH;SRC=BASE/'government-xl-siu-hong-companion-sources-v1-20261021';ASSEMBLY=BASE/'government-xl-siu-hong-original-assembly-v1-20261021'
def main():
 assert not DOC.exists();receipt,pins=authenticate(SRC);p=SRC/'nominations.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];data=read(p);refs=[Path(__file__),SRC/'result.json',p,HERE/'exact_packed_world_geometry_20261009.py',HERE/'china_ferry_current_foundations_v1_20261020.py'];used={}
 polygons={}
 for uid,s in data['forms'].items():
  tile=ROOT/'3d-viewer'/s['tile'];assert next(b for b in read(tile)['buildings']if b['uid']==uid)==s['building'];used[str(tile.relative_to(ROOT))]=digest(tile.read_bytes());refs.append(tile);b=s['building'];polygons[uid]=Polygon(b['rings'][0],b['rings'][1:])
 group=shapely.union_all(list(polygons.values()));nominee=next(n for n in data['rows']if n['uid']=='landsd/233417:0');uid=nominee['uid'];asset=HERE/'local/government-xl-eight-further-original-closures-20261008/assets'/(nominee['model']['asset']['sha256']+'.glb.gz');assert digest(asset.read_bytes())==nominee['model']['asset']['sha256'];refs.append(asset);used[str(asset.relative_to(ROOT))]=digest(asset.read_bytes());tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==595
 projected=shapely.polygons(tri[:,:,[0,2]]);source=shapely.union_all(projected[shapely.area(projected)>0]);points=shapely.points(tri.reshape(-1,3)[:,[0,2]]);rows=[]
 for name,target in [('own',polygons[uid]),('allThreeCurrentParentForms',group)]:
  outside=source.difference(target);rows.append(dict(scope=name,sourceAreaM2=source.area,targetAreaM2=target.area,sourceOutsideM2=outside.area,sourceCoverageFraction=source.intersection(target).area/source.area,maximumSourceVertexOutsideM=float(np.max(shapely.distance(points,target)))))
 save(DOC/'geometry.json.gz',dict(uid=uid,sourceSHA256=nominee['model']['asset']['sha256'],sourceProjectionWKT=source.wkt,groupWKT=group.wkt,forms=data['forms'],rows=rows))
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 result=dict(uids=[uid],rows=rows,installationApproved=False,sourceGeometryChanges=0,qualification='Diagnostic complete original projection only. Same parent and footprint overlap alone do not prove source identity or authorise footprint scope.')
 save(DOC/'summary.json',result);module('siu_extent_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-podium-current-footprint-extent',list(dict.fromkeys(refs)),result);print(rows,flush=True)
if __name__=='__main__':main()
