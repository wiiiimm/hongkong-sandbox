"""Render exact original component and footprint context; no geometry edits."""
from pathlib import Path
import numpy as np,shapely,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-stonecutters-component-views-v1-20261021';DOC=BASE/BATCH;refs=[Path(__file__)];assert not DOC.exists()
def take(n,f):
 _,pins=authenticate(BASE/n);p=BASE/n/f;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([BASE/n/'result.json',p]);return read(p)
c=take('government-xl-stonecutters-far-components-v1-20261021','components.json');g=next(r for r in take('government-xl-six-extent-review-views-v1-20261021','geometry.json.gz')['rows']if r['uid']==c['uids'][0]);row=next(r for r in take('government-xl-next-twenty-current-terrain-v6-20261021','selection.json.gz')['rows']if r['uid']==c['uids'][0]);p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==c['sourceSHA256'];refs.append(p);t=decode_original_world_triangles(p.read_bytes());assert digest(t.astype('<f8').tobytes())==c['worldTrianglesSHA256'];comp=c['components'][0];ids=comp['faceIds'];far=comp['farFaceIds'];foot=shapely.from_wkt(g['targetWKT'])
fig,axes=plt.subplots(1,3,figsize=(15,5))
for ax,dim,title in zip(axes,[(0,2),(0,1),(2,1)],['Plan (X,Z)','Elevation (X,Y)','Elevation (Z,Y)']):
 ax.add_collection(PolyCollection(t[:,:,dim],facecolor='#d7dce0',edgecolor='none',alpha=.3));ax.add_collection(PolyCollection(t[ids][:,:,dim],facecolor='#1976b5',edgecolor='#14517a',linewidth=.15));ax.add_collection(PolyCollection(t[far][:,:,dim],facecolor='#e45b32',edgecolor='#962e12',linewidth=.4));ax.autoscale();ax.set_aspect('equal');ax.set_title(title);ax.tick_params(labelsize=7)
 if dim==(0,2):
  for poly in getattr(foot,'geoms',[foot]):
   for ring in [poly.exterior,*poly.interiors]:xy=np.asarray(ring.coords);ax.plot(xy[:,0],xy[:,1],color='black',linewidth=.6)
fig.suptitle('Stonecutters: exact original grey; connected 350-face component blue; 18 flagged faces orange');fig.tight_layout();DOC.mkdir();fig.savefig(DOC/'component-context.png',dpi=150);plt.close(fig)
module('stone_views',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-component-context-render',refs,dict(uids=c['uids'],sourceGeometryChanges=0,installationApproved=False,reviewOnly=True))
