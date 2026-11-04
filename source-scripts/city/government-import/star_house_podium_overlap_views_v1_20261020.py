"""Exact source projection and foreign-footprint context; no approvals."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';SRC=BASE/'government-xl-star-house-podium-identity-v2-20261020';BATCH='government-xl-star-house-podium-overlap-views-v1-20261020';DOC=BASE/BATCH
assert not DOC.exists();receipt=read(SRC/'result.json')
with connect() as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
row=next(r for r in read(BASE/'government-xl-star-parkview-support-v1-20261020/selection.json.gz')['rows'] if r['uid']=='landsd/231484:0');tri=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());proof=read(SRC/'identity.json');assert digest(np.asarray(tri,dtype='<f8').tobytes())==proof['worldTrianglesSHA256'];context=read(SRC/'context.json')['identity'];forms={b['uid']:b for b in read(ROOT/'3d-viewer'/row['source']['tile'])['buildings']};polys=shapely.polygons(tri[:,:,[0,2]]);area=shapely.area(polys);target=Polygon(row['source']['building']['rings'][0],row['source']['building']['rings'][1:]);projection=shapely.union_all(polys[area>1e-10]);foreign=['landsd/211943:0','landsd/215934:0'];out=[];DOC.mkdir()
fig=plt.figure(figsize=(18,6));ax=fig.add_subplot(1,3,1)
for p in getattr(projection,'geoms',[projection]):x,z=p.exterior.xy;ax.fill(x,z,color='lightgrey')
x,z=target.exterior.xy;ax.plot(x,z,color='black',label='Star House podium footprint')
for n,u in enumerate(foreign,2):
 b=forms[u];polygon=Polygon(b['rings'][0],b['rings'][1:]);inter=shapely.intersection(polys,polygon);ids=np.flatnonzero(shapely.area(inter)>1e-10);x,z=polygon.exterior.xy;ax.plot(x,z,label=u);out.append(dict(uid=u,sourceFaceIds=ids.tolist(),positiveAreaSourceFaces=len(ids),intersectionAreaM2=float(projection.intersection(polygon).area),sourceFacesUnchanged=True))
 a=fig.add_subplot(1,3,n,projection='3d');d=tri[:,:,[0,2,1]];lo=d.min((0,1));hi=d.max((0,1));a.add_collection3d(Poly3DCollection(d,facecolor='grey',alpha=.12,edgecolor='none'));a.add_collection3d(Poly3DCollection(d[ids],facecolor='red',alpha=.8,edgecolor='none'));a.set_xlim(lo[0],hi[0]);a.set_ylim(lo[1],hi[1]);a.set_zlim(lo[2],hi[2]);a.set_box_aspect(hi-lo);a.view_init(30,-60);a.set_title('Source faces over '+u)
ax.set_aspect('equal');lo=tri.min((0,1));hi=tri.max((0,1));ax.set_xlim(lo[0]-10,hi[0]+10);ax.set_ylim(lo[2]-10,hi[2]+10);ax.legend(fontsize=7);ax.set_title('Original projection / current footprints');fig.tight_layout();fig.savefig(DOC/'overlap-context.png',dpi=150);plt.close(fig)
save(DOC/'overlaps.json',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],rows=out,installationApproved=False))
refs=[Path(__file__),SRC/'result.json',HERE/'exact_packed_world_geometry_20261009.py']
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
module('star_overlap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-source-foreign-footprint-context',list(dict.fromkeys(refs)),dict(uids=[row['uid']],rows=[{k:v for k,v in r.items() if k!='sourceFaceIds'} for r in out],installationApproved=False))
