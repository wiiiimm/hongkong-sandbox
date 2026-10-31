"""Account for original podium extensions and foreign overlap, without approval."""
from pathlib import Path
import numpy as np, shapely
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho300857-podium-extent-diagnostic-v3-20261020';DOC=BASE/BATCH;SRC=BASE/'government-xl-yoho300857-podium-identity-v1-20261020';CAP=BASE/'government-xl-next-twenty-current-terrain-v2-20261020'
assert not DOC.exists()
r=read(SRC/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
sel=CAP/'selection.json.gz';assert digest(sel.read_bytes())==pins[str(sel.relative_to(ROOT))];row=next(x for x in read(sel)['rows']if x['uid']=='landsd/301636:0');asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];t=decode_original_world_triangles(asset.read_bytes())
final=module('yoho_extent_forms',HERE/'xl-final-script-pass.py');lo,hi=t.min((0,1)),t.max((0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])
def polygon(b):
 p=shapely.Polygon()
 for ring in b['rings']:p=p.symmetric_difference(shapely.Polygon(ring))
 return p
own=polygon(row['source']['building']);polys=shapely.polygons(t[:,:,[0,2]]);dist=shapely.distance(shapely.points(t[:,:,[0,2]].reshape(-1,2)),own).reshape(-1,3).max(1)
ids=np.where(dist>1)[0];extensions=[dict(faceId=int(i),maximumVertexDistanceM=float(dist[i]),vertices=t[i].tolist())for i in ids]
foreign=next(b for b,_,_ in forms if b['uid']=='landsd/300868:0');fp=polygon(foreign);hits=np.where(shapely.intersects(polys,fp))[0];details=[]
# Evaluate linear face height at every vertex of each clipped finite polygon.
for i in hits:
 clip=polys[i].intersection(fp);coords=shapely.get_coordinates(clip)
 if not len(coords):continue
 tri=t[i];a=np.column_stack([tri[:,0],tri[:,2],np.ones(3)]);det=np.linalg.det(a)
 if abs(det)<1e-12:
  details.append(dict(faceId=int(i),projectedVertical=True,yRange=tri[:,1].tolist()));continue
 coeff=np.linalg.solve(a,tri[:,1]);ys=np.column_stack([coords,np.ones(len(coords))])@coeff
 details.append(dict(faceId=int(i),projectedVertical=False,intersectionAreaM2=float(clip.area),minY=float(min(ys)),maxY=float(max(ys)),clearanceAboveRecordedTopM=float(min(ys)-(foreign['base']+foreign['height']))))
save(DOC/'extensions.json.gz',dict(rows=extensions,totalFaces=len(t),sourceSHA256=row['sourceSHA256'],installationApproved=False))
save(DOC/'foreign-overlap.json',dict(foreignForm=foreign,rows=details,installationApproved=False,limitation='Finite source-face comparison to recorded form top; not a replacement for current rendered neighbour checks.'))
summary=dict(uid=row['uid'],sourceFaces=len(t),extensionFacesBeyond1M=len(ids),maximumExtentM=float(dist.max()),foreignFaces=len(details),minimumFiniteClearanceM=min(x['clearanceAboveRecordedTopM']for x in details if not x['projectedVertical']),verticalFaces=sum(x['projectedVertical']for x in details),installationApproved=False)
refs=[Path(__file__),SRC/'result.json',sel,asset,HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-final-script-pass.py']+[ROOT/'3d-viewer'/tile for _,_,tile in forms]
module('yoho_extent_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-podium-finite-extent-accounting',list(dict.fromkeys(refs)),dict(uids=[row['uid']],**summary));print(summary,flush=True)
