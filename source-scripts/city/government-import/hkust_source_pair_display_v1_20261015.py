"""Display complete unchanged HKUST pair and target gaps; no model edits."""
from pathlib import Path
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
from shapely.geometry import shape
from shapely.geometry.polygon import orient
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-hkust-uncovered-target-partition-v1-20261015';DOC=BASE/'government-xl-hkust-source-pair-display-v1-20261015'
def main():
 assert not DOC.exists();prior=read(OLD/'result.json');refs={r['path']:r['sha256'] for r in prior['evidenceRefs']};paths=[OLD/'result.json',OLD/'regions.geojson',Path(__file__)];triangles=[]
 for uid in ['309822','232155']:
  p=BASE/'government-xl-hkust309822-232155-target-provenance-draft-v1-20261014/cached-complete-original-arrays-v1'/f'landsd-{uid}-0.json.gz';assert digest(p.read_bytes())==refs[str(p.relative_to(ROOT))];a=read(p);triangles.append(np.array(a['completeOrderedOriginalTriangles']));paths.append(p)
 assert digest((OLD/'regions.geojson').read_bytes())==refs[str((OLD/'regions.geojson').relative_to(ROOT))];DOC.mkdir();fig=plt.figure(figsize=(18,10));colors=['#6997b8','#dfad62'];allv=np.concatenate(triangles).reshape(-1,3);origin=allv.mean(axis=0)
 for i,az in enumerate([-60,120]):
  ax=fig.add_subplot(1,3,i+1,projection='3d')
  for t,c in zip(triangles,colors):
   v=(t-origin)[:,:,[0,2,1]];ax.add_collection3d(Poly3DCollection(v,facecolor=c,edgecolor='#555555',linewidth=.08,alpha=1))
  pts=(allv-origin)[:,[0,2,1]];lo=pts.min(0);hi=pts.max(0);ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_zlim(lo[2],hi[2]);ax.set_box_aspect(hi-lo);ax.view_init(elev=23,azim=az);ax.set_title('All original faces: tower blue / podium ochre');ax.set_xlabel('X offset');ax.set_ylabel('Z offset');ax.set_zlabel('Elevation offset')
 ax=fig.add_subplot(1,3,3)
 for f in read(OLD/'regions.geojson')['features']:
  role=f['properties']['role']
  if role not in ['target','missing']:continue
  g=shape(f['geometry']);polys=[g] if g.geom_type=='Polygon' else list(g.geoms)
  for p in polys:
   if p.geom_type!='Polygon':continue
   p=orient(p,sign=1);vertices=[];codes=[]
   for ring in [p.exterior,*p.interiors]:
    v=np.array(ring.coords)-origin[[0,2]];vertices.extend(v);codes.extend([MPath.MOVETO]+[MPath.LINETO]*(len(v)-2)+[MPath.CLOSEPOLY])
   ax.add_patch(PathPatch(MPath(vertices,codes),facecolor='#ef6b55' if role=='missing' else '#e2e2e2',edgecolor='black',lw=.3))
 ax.autoscale();ax.set_aspect('equal');ax.invert_yaxis();ax.set_title('Red = target lacking either source projection\nHoles retained; diagnostic only');fig.tight_layout();fig.savefig(DOC/'complete-originals-and-gaps.png',dpi=150);plt.close(fig)
 save(DOC/'display.json',{'uids':prior['uids'],'completeFaces':[len(t) for t in triangles],'displayOrigin':origin.tolist(),'sourceGeometryChanges':0,'displayTranslationOnly':True,'acceptanceGranted':False})
 freezer=module('hkust_display_receipt',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');freezer.freeze(DOC.name,'hkust-complete-source-pair-display-v1',paths,{'uids':prior['uids'],'completeSourceFaces':[len(t) for t in triangles],'currentHeldReason':prior['currentHeldReason'],'nextStep':'Interpret complete unchanged pair and gap layout; if open ground/courtyard is proposed, corroborate its exact source role before changing identity applicability.'})
if __name__=='__main__':main()
