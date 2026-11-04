"""Trace complete model-projection holes to original terrain or construction."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sol-city-source-gap-v1-20261021';DOC=BASE/BATCH
refs=[Path(__file__)];pins={}
for name in ['adjoining-ground-v1','shaped-ground-v2','assembly-capture-v2']:
 folder=BASE/('government-xl-sol-city-'+name+'-20261021');_,p=authenticate(folder);refs.append(folder/'result.json')
 for k,h in p.items():assert k not in pins or pins[k]==h;pins[k]=h
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
row=next(r for r in read(BASE/'government-xl-sol-city-assembly-capture-v2-20261021/selection.json.gz')['rows']if r['uid']=='landsd/273271:0')
model=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());projection=shapely.union_all(shapely.polygons(model[:,:,[0,2]]))
ground=np.asarray(read(HERE/'local/government-xl-sol-city-adjoining-ground-v1-20261021/273271:0-ground.json.gz')['completeAdjoiningTerrain']);sourcePolys=shapely.polygons(ground[:,:,[0,2]]);sourceUnion=shapely.union_all(sourcePolys);tree=shapely.STRtree(sourcePolys)
sourceMissing=projection.difference(sourceUnion)
shaped=np.asarray(read(HERE/'local/government-xl-sol-city-shaped-ground-v2-20261021/diagnostic-height-surfaces.json.gz')['triangles']);shapeUnion=shapely.union_all(shapely.polygons(shaped[:,:,[0,2]]));shapeMissing=projection.difference(shapeUnion)
parts=[]
for part in shapely.get_parts(sourceMissing):
 if part.area<=1e-8:continue
 boundary=np.asarray(part.exterior.coords);ids=tree.query(part,predicate='dwithin',distance=.002)
 parts.append(dict(areaM2=part.area,bounds=part.bounds,wkt=part.wkt,nearOriginalFaceIds=[int(i)for i in ids],boundaryVertices=boundary.tolist()))
result=dict(uids=[row['uid']],sourceMissingAreaM2=sourceMissing.area,shapedMissingAreaM2=shapeMissing.area,constructionIntroducedAreaM2=shapeMissing.difference(sourceMissing).area,sourceParts=len(parts),sourceSHA256=row['sourceSHA256'],installationApproved=False)
save(DOC/'gaps.json',dict(rows=parts));save(DOC/'summary.json',result)
refs.extend(ROOT/p for p in pins);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'china_ferry_current_foundations_v1_20261020.py'])
module('sol_gap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-terrain-source-gap-attribution',refs,result);print(result)
