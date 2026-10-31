"""Compare unchanged original projections with all current nearby official forms."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-spatial-matrix-v1-20261020';DOC=BASE/BATCH;REC=BASE/'government-xl-plaza-ascot-assembly-original-recovery-v1-20261020'
def main():
 assert not DOC.exists();receipt=read(REC/'result.json');refs=[Path(__file__),REC/'result.json',HERE/'exact_packed_world_geometry_20261009.py']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};p=REC/'recovery.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);rows=read(p)['rows']
 tile=ROOT/'3d-viewer/city/data/tiles/2_-7.json';refs.append(tile);tilehash=digest(tile.read_bytes());forms=read(tile)['buildings'];polys=[shapely.Polygon(b['rings'][0],b['rings'][1:])for b in forms];tree=shapely.STRtree(polys);out=[]
 for row in rows:
  p=ROOT/row['assetPath'];assert digest(p.read_bytes())==row['sourceSHA256'];refs.append(p);t=decode_original_world_triangles(p.read_bytes());tri=shapely.polygons(t[:,:,[0,2]]);projection=shapely.union_all(tri[shapely.area(tri)>1e-10]);target=next(i for i,b in enumerate(forms)if b['uid']==row['uid']);candidates=set(map(int,tree.query(projection,predicate='intersects')))|{target};matches=[]
  for i in candidates:
   b=forms[i];area=projection.intersection(polys[i]).area;matches.append(dict(uid=b['uid'],name=b.get('name'),parent=b.get('parent'),buildingCSUID=b.get('buildingCSUID'),recordedBase=b.get('baseHeightHKPD'),recordedTop=b.get('topHeightHKPD'),intersectionAreaM2=area,formCoverage=area/polys[i].area if polys[i].area else 0,sourceCoverage=area/projection.area,centroidDistanceM=projection.centroid.distance(polys[i].centroid),recordedIdentity=i==target))
  matches.sort(key=lambda x:-x['intersectionAreaM2']);out.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],sourceBounds=[t.min((0,1)).tolist(),t.max((0,1)).tolist()],projectionAreaM2=projection.area,recordedTarget=next(x for x in matches if x['recordedIdentity']),intersectingForms=matches,installationApproved=False));print(row['uid'],out[-1]['recordedTarget']['formCoverage'],flush=True)
 assert digest(tile.read_bytes())==tilehash;save(DOC/'matrix.json',dict(rows=out,installationApproved=False,qualification='Current tile footprint overlap diagnostic only; overlap alone does not authorize changing government identity, pose, or acceptance.'))
 summary=dict(uids=[r['uid']for r in rows],rows=[dict(uid=r['uid'],recordedTarget=r['recordedTarget'],bestOverlaps=r['intersectingForms'][:3])for r in out],installationApproved=False);save(DOC/'summary.json',summary);module('ascot_matrix_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-original-to-nearby-official-footprint-matrix',refs,summary)
if __name__=='__main__':main()
