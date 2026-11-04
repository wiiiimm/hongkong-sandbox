"""Review every Pier8 source-ground failure in full-source plan and elevations."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-pier8-grade-views-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__)];pins={}
def take(n,p):
 _,ps=authenticate(BASE/n);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/n/'result.json',p]);return read(p)
sn='government-xl-next-twenty-current-terrain-v6-20261021';row=next(r for r in take(sn,BASE/sn/'selection.json.gz')['rows']if r['uid']=='landsd/213352:0');ap=ROOT/row['candidate']['path'];assert digest(ap.read_bytes())==row['sourceSHA256'];refs.append(ap);tri=decode_original_world_triangles(ap.read_bytes())
cn='government-xl-central-pier8-original-grade-v1-20261021';c=take(cn,BASE/cn/'213352:0-original.json.gz');assert c['sourceSHA256']==row['sourceSHA256']
ids=c['continuousNegativeFaceIds'];up=c['negativeUpwardFaceIds'];DOC.mkdir(parents=True)
fig,axes=plt.subplots(2,3,figsize=(18,10))
for line,chosen in enumerate([ids,up]):
 part=tri[chosen];lo=part.min((0,1))-2;hi=part.max((0,1))+2
 for ax,coords in zip(axes[line],[(0,2),(0,1),(2,1)]):
  ax.add_collection(PolyCollection(tri[:,:,coords],facecolors='#94a3b8',edgecolors='none',alpha=.25))
  ax.add_collection(PolyCollection(part[:,:,coords],facecolors='#ef4444',edgecolors='#b91c1c',linewidth=.2,alpha=.8))
  ax.set_xlim(lo[coords[0]],hi[coords[0]]);ax.set_ylim(lo[coords[1]],hi[coords[1]]);ax.set_aspect('equal');ax.set_title(('All failed faces'if line==0 else'Upward failed faces')+' '+str(coords));ax.ticklabel_format(useOffset=False)
fig.tight_layout();fig.savefig(DOC/'grade-context.png',dpi=150);plt.close(fig)
out=[]
for i in ids:
 t=tri[i];f=c['faces'][i];out.append(dict(face=i,vertices=t.tolist(),bounds=[t.min(0).tolist(),t.max(0).tolist()],areaM2=float(np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))/2),minimumGapM=f['minimum']['minimumGapM'],maximumObservedGapM=f['maximumObservedGapM'],normalYRatio=f['normalYRatio'],upward=i in up))
result=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],rows=out,sourceGeometryChanges=0,installationApproved=False,qualification='Complete failed-face context; orientation is not a semantic or physical exemption.')
save(DOC/'face-context.json',result)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
r=module('pier_grade_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-grade-failure-views',refs,result);print(r['jobId'],flush=True)
