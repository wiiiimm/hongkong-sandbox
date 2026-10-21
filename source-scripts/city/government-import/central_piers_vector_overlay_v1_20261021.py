"""Compare exact pier extent geometry with independent official approach vectors."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import shape
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-piers-vector-overlay-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__)];pins={}
def take(n,p):
 _,ps=authenticate(BASE/n);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/n/'result.json',p]);return read(p)
vn='government-xl-central-piers-primary-vectors-v1-20261021';rows=take(vn,BASE/vn/'pier-approach-government-vector-context.json.gz')['rows']
styles=[('10_CartoHydroLine_1K',6,'seawall','#2563eb'),('8_CartoPedLine_1K',1,'footbridge','#16a34a'),('8_CartoPedLine_1K',5,'pedestrian area','#9333ea'),('8_CartoPedLine_1K',8,'steps','#d97706')]
fig,axes=plt.subplots(1,2,figsize=(14,8));out=[]
def lines(g):
 if g.geom_type in ['LineString','LinearRing']:yield g
 elif g.geom_type=='Polygon':yield g.exterior;yield from g.interiors
 elif hasattr(g,'geoms'):
  for child in g.geoms:yield from lines(child)
for ax,key in zip(axes,['213352:0','285475:0']):
 fn='government-xl-six-far-faces-v1-20261021';r=take(fn,BASE/fn/(key+'.json.gz'));tri=np.asarray(r['farFaceVertices']);xz=tri[:,:,[0,2]];points=shapely.points(xz.reshape(-1,2));projection=shapely.union_all(shapely.polygons(xz));lo=xz.min((0,1));hi=xz.max((0,1))
 ax.add_collection(PolyCollection(xz,facecolors='#fca5a5',edgecolors='#ef4444',linewidth=.15,alpha=.6));measures=[]
 for layer,symbol,label,color in styles:
  matching=[shape(x['geometry'])for x in rows if x['layer']==layer and x['properties']=={'_symbol':symbol}];g=shapely.union_all(matching)
  first=True
  for line in lines(g):ax.plot(*line.xy,color=color,linewidth=1.1,label=label if first else None);first=False
  distances=shapely.distance(points,g)
  measures.append(dict(layer=layer,symbol=symbol,label=label,maximumVertexDistanceM=float(distances.max()),minimumVertexDistanceM=float(distances.min())))
 ax.set_xlim(lo[0]-5,hi[0]+5);ax.set_ylim(lo[1]-5,hi[1]+5);ax.set_aspect('equal');ax.legend();ax.set_title(r['name']);ax.ticklabel_format(useOffset=False)
 out.append(dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],farFaceIds=r['farFaceIds'],measurements=measures))
DOC.mkdir(parents=True);fig.tight_layout();fig.savefig(DOC/'approach-overlay.png',dpi=160);plt.close(fig)
summary=dict(uids=[r['uid']for r in out],rows=out,installationApproved=False,identityApproved=False,sourceGeometryChanges=0,qualification='Independent provider vectors share HK80 world coordinates. Distances are diagnostic; no buffer or threshold exception is applied.')
save(DOC/'summary.json',summary)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
r=module('pier_overlay_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-pier-approach-official-vector-comparison',refs,summary);print(r['jobId'],flush=True)
