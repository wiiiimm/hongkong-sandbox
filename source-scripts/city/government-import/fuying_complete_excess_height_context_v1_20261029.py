"""Report all original vertex heights by footprint distance; no admission threshold."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-fuying181489-complete-excess-height-context-v1-20261029';RUNTIME='government-xl-fuying181489-five-member-runtime-v2-20261029'
def main():
 out=BASE/BATCH;assert not out.exists();_,pins=authenticate(BASE/RUNTIME);selectionpath=BASE/RUNTIME/'selection.json.gz';assert digest(selectionpath.read_bytes())==pins[str(selectionpath.relative_to(ROOT))];row=next(r for r in read(selectionpath)['rows']if r['uid']=='landsd/181489:0');asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());points=tri.reshape(-1,3);building=row['source']['building'];polygon=shapely.Polygon(building['rings'][0],building['rings'][1:]);distance=shapely.distance(shapely.points(points[:,[0,2]]),polygon);rows=[]
 for low,high in zip([0,.5,1,2,5,10,20],[.5,1,2,5,10,20,float('inf')]):
  mask=(distance>low)&(distance<=high);values=points[mask];rows.append(dict(distanceGreaterThanM=low,distanceAtMostM=high if np.isfinite(high)else None,vertices=int(mask.sum()),completeSourceVertexYRange=[float(values[:,1].min()),float(values[:,1].max())]if len(values)else None))
 result=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],wholeOriginalFaces=len(tri),allOriginalIndexedVertices=len(points),allVerticesAccounted=sum(r['vertices']for r in rows)+int((distance==0).sum())==len(points),verticesOnOrWithinTarget=int((distance==0).sum()),rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='All original indexed vertices measured against exact current footprint, with diagnostic distance bands only. This is not a full facet-piece bound or an identity/physical/role/visual approval; no sparse sample or new acceptance threshold.')
 save(out/'summary.json',result);refs=[Path(__file__),BASE/RUNTIME/'result.json',selectionpath,asset,ROOT/'3d-viewer'/row['source']['tile'],HERE/'exact_packed_world_geometry_20261009.py'];module('fuying_excess_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-vertex-distance-height-context-no-acceptance',refs,result);print(rows,flush=True)
if __name__=='__main__':main()
