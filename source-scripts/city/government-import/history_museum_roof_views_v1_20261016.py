"""Render unchanged source triangles and exact roof-form differences for review."""
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-history-museum-roof-views-v1-20261016';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-history-museum-roof-context-v1-20261016'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:
  p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];refs.append(p)
 context=read(PRIOR/'context.json.gz');geometry=HERE/'local/government-xl-history-museum-preserved-neighbours-v1-20261016/runtime-geometry.json.gz';g=read(geometry)['rows'][0];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];roof=context['roofForm'];foot=Polygon(roof['rings'][0],roof['rings'][1:]);polys=shapely.polygons(tri[:,:,[0,2]]);projection=shapely.union_all(polys[shapely.area(polys)>1e-10]);missing=foot.difference(projection);parts=list(missing.geoms)if hasattr(missing,'geoms')else[missing];touch=np.array(context['sourceFaceIdsIntersectingRoof']);colors=np.tile([.65,.7,.75,1.],(len(tri),1));colors[touch]=[.9,.42,.12,1.];DOC.mkdir()
 fig=plt.figure(figsize=(16,8),layout='constrained');ax=fig.add_subplot(121,projection='3d');ax.add_collection3d(Poly3DCollection(tri[:,:,[0,2,1]],facecolors=colors,edgecolor='none',shade=True));lo=tri.reshape(-1,3).min(0);hi=tri.reshape(-1,3).max(0);ax.set(xlim=(lo[0],hi[0]),ylim=(hi[2],lo[2]),zlim=(lo[1]-1,hi[1]+1),xlabel='X metres',ylabel='Z metres',zlabel='Height HKPD');ax.set_box_aspect((hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]));ax.view_init(elev=35,azim=-60);ax.set_title('Unchanged original; orange faces intersect roof footprint')
 ax=fig.add_subplot(122);ax.add_collection(PolyCollection(tri[:,:,[0,2]],facecolors=colors,edgecolors='none'));x,z=foot.exterior.xy;ax.plot(x,z,color='blue',linewidth=1.2,label='Recorded roof footprint')
 for i,part in enumerate(parts):
  if part.area>0:x,z=part.exterior.xy;ax.fill(x,z,color='red',label='Missing projected area'if i==0 else None)
 bx=foot.bounds;ax.set(xlim=(bx[0]-3,bx[2]+3),ylim=(bx[3]+3,bx[1]-3),xlabel='X metres',ylabel='Z metres');ax.set_aspect('equal');ax.legend();ax.set_title('Exact source projection versus low roof form');fig.savefig(DOC/'original-roof-review.png',dpi=150);plt.close(fig)
 summary=dict(uid=g['uid'],roofUid=roof['uid'],completeOriginalFaces=len(tri),intersectingFaces=len(touch),missingAreaM2=missing.area,missingParts=[dict(areaM2=p.area,bounds=list(p.bounds))for p in parts if p.area>0],image=dict(path=str((DOC/'original-roof-review.png').relative_to(ROOT)),width=2400,height=1200),sourceGeometryChanges=0,identityApproved=False,suppressionApproved=False,visualReviewPending=True)
 save(DOC/'summary.json',summary);save(DOC/'missing-roof-geometry.json',shapely.to_geojson(missing));refs += [geometry,PRIOR/'context.json.gz'];out=module('museum_roof_views_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'museum-complete-original-roof-visual-review-evidence-v1',list(dict.fromkeys(refs)),dict(uids=[g['uid'],roof['uid']],summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],missingParts=len(summary['missingParts']),intersectingFaces=len(touch)),flush=True)
if __name__=='__main__':main()
