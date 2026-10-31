"""Source-face diagrams and geometry descriptors; no placement waiver."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-china-ferry-lower-surface-context-v1-20261020';DOC=BASE/BATCH
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
fig,axes=plt.subplots(1,3,figsize=(18,8))
for ax,dims,label in zip(axes,[(0,2),(0,1),(2,1)],['Plan X/Z','Elevation X/Y','Elevation Z/Y']):
 ax.add_collection(PolyCollection(t[:,:,dims],facecolors='#ccd5dd',edgecolors='none',alpha=.2))
 ax.add_collection(PolyCollection(t[ids][:,:,dims],facecolors='#e86c23',edgecolors='#983200',linewidths=.3,alpha=.8))
 ax.add_collection(PolyCollection(t[up][:,:,dims],facecolors='#d32f4e',edgecolors='#8b102a',linewidths=.5))
 ax.scatter(failed[:,dims[0]],failed[:,dims[1]],s=6,c='#0050bd');ax.autoscale();ax.set_aspect('equal');ax.set_title(label);ax.set_xlabel('metres')
 if dims[1]==1:ax.set_ylim(0,5);ax.set_aspect('auto');ax.set_ylabel('HKPD metres (0–5m detail)')
fig.suptitle('China Ferry original source: orange 79 buried faces; red 8 upward; blue 61 rim failures\nGrey complete source projection. Diagnostic only; no physical acceptance.');fig.tight_layout();fig.savefig(DOC/'lower-context.png',dpi=160);plt.close(fig)
rows=[]
for i in ids:
 v=t[i];n=np.cross(v[1]-v[0],v[2]-v[0]);length=np.linalg.norm(n);edges=np.linalg.norm(v-np.roll(v,1,axis=0),axis=1);area=length/2
 rows.append(dict(face=i,upward=i in up,area=float(area),longestEdge=float(max(edges)),minimumAltitude=float(2*area/max(edges))if max(edges)>0 else 0,bounds=[v.min(0).tolist(),v.max(0).tolist()],unitNormal=(n/length).tolist()if length>0 else [0,0,0]))
save(DOC/'geometry-context.json',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],rows=rows,rimFailures=rim['proof']['failed'],installationApproved=False))
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
refs.append(HERE/'exact_packed_world_geometry_20261009.py')
module('china_lower_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-lower-source-face-context-diagrams',list(dict.fromkeys(refs)),dict(uids=[row['uid']],buriedFaces=len(ids),upwardFaces=len(up),rimFailures=len(failed),installationApproved=False,sourceGeometryChanges=0))
