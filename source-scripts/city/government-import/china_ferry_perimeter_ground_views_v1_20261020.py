"""Source-face diagrams and geometry descriptors; no placement waiver."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-china-ferry-perimeter-ground-views-v1-20261020';DOC=BASE/BATCH
SRC=BASE/'government-xl-china-ferry-full-source-faces-v1-20261020';CAP=BASE/'government-xl-china-ferry-five-private-terrain-v1-20261020';RIM=BASE/'government-xl-china-ferry-podium-rim-v1-20261020'
assert not DOC.exists();refs=[Path(__file__)];pins={}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for folder in [SRC,CAP,RIM]:
  r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
row=next(r for r in read(CAP/'selection.json.gz')['rows']if r['uid']=='landsd/285642:0');t=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());buried=read(SRC/'complete-face-diagnostic.json.gz')['buriedFaces'];ids=[r['faceIndex']for r in buried];up=[r['faceIndex']for r in buried if r['upward']];rim=next(r for r in read(RIM/'rim.json')['rows']if r['mode']=='original');failed=np.array([r['position']for r in rim['proof']['failed']]);DOC.mkdir(parents=True)
runtime=next(x for x in read(HERE/'local'/CAP.name/'runtime-geometry.json.gz')['rows']if x['uid']==row['uid']);ground=np.asarray(runtime['drawnGroundGeometry']).reshape(-1,3,3)
regions={'north-low-edge':(730,815,-1320,-1280),'south-sloping-edge':(740,775,-1510,-1470)};region_stats=[]
for name,(x0,x1,z0,z1)in regions.items():
 def mask(a):return (a[:,:,0].max(1)>=x0)&(a[:,:,0].min(1)<=x1)&(a[:,:,2].max(1)>=z0)&(a[:,:,2].min(1)<=z1)
 selected=np.flatnonzero(mask(t));g=ground[mask(ground)];bad=[i for i in ids if i in set(selected)];origin=np.array([x0,z0,0])
 fig=plt.figure(figsize=(15,7))
 for j,az in enumerate([35,215]):
  ax=fig.add_subplot(1,2,j+1,projection='3d')
  for mesh,color,alpha in [(g,'#68a06a',.35),(t[selected],'#8594ac',.2),(t[bad],'#da462a',.9)]:
   ax.add_collection3d(Poly3DCollection(mesh[:,:,[0,2,1]]-origin,facecolor=color,edgecolor=color,alpha=alpha,linewidth=.2))
  ax.set_xlim(0,x1-x0);ax.set_ylim(0,z1-z0);ax.set_zlim(0,8);ax.set_box_aspect([x1-x0,z1-z0,15]);ax.view_init(25,az);ax.set_xlabel('X offset metres');ax.set_ylabel('Z offset metres');ax.set_zlabel('HKPD metres');ax.set_title(name+'; vertical axis expanded')
 fig.suptitle('Original source grey; buried source red; actual drawn terrain green\nViewport 0–8m; triangles retained whole, axes crop view. No acceptance waiver.');fig.tight_layout();fig.savefig(DOC/(name+'.png'),dpi=150);plt.close(fig)
 region_stats.append(dict(name=name,bounds=[x0,x1,z0,z1],originalFaces=selected.tolist(),buriedFaces=bad,groundFaces=len(g)))
save(DOC/'regions.json',dict(regions=region_stats,groundSHA256=digest(np.asarray(ground,dtype='<f8').tobytes()),installationApproved=False))
rows=[]
for i in ids:
 v=t[i];n=np.cross(v[1]-v[0],v[2]-v[0]);length=np.linalg.norm(n);edges=np.linalg.norm(v-np.roll(v,1,axis=0),axis=1);area=length/2
 rows.append(dict(face=i,upward=i in up,area=float(area),longestEdge=float(max(edges)),minimumAltitude=float(2*area/max(edges))if max(edges)>0 else 0,bounds=[v.min(0).tolist(),v.max(0).tolist()],unitNormal=(n/length).tolist()if length>0 else [0,0,0]))
save(DOC/'geometry-context.json',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],rows=rows,rimFailures=rim['proof']['failed'],installationApproved=False))
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
refs.append(HERE/'exact_packed_world_geometry_20261009.py')
module('china_lower_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-perimeter-source-and-drawn-ground-views',list(dict.fromkeys(refs)),dict(uids=[row['uid']],buriedFaces=len(ids),upwardFaces=len(up),rimFailures=len(failed),installationApproved=False,sourceGeometryChanges=0))
