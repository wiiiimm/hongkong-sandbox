"""Complete original face/low-edge terrain sampling; no geometry edits or approval."""
from pathlib import Path
import numpy as np,shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-kadoorie-private-ground-samples-v1-20261021';DOC=BASE/BATCH
SRC=BASE/'government-xl-next-twenty-current-terrain-v6-20261021';GROUND=BASE/'government-xl-kadoorie-terrain-boundary-transition-v1-20261021'
assert not DOC.exists();refs=[Path(__file__)];pins={}
with connect()as db:
 db.execute('SET TRANSACTION READ ONLY')
 for folder in [SRC,GROUND]:
  r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
def take(p):
 assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
row=next(r for r in take(SRC/'selection.json.gz')['rows']if r['uid']=='landsd/115799:0');asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==17805
terrain=np.asarray(take(HERE/'local'/GROUND.name/'private-terrain.json.gz')['triangles']);lo,hi=tri.min((0,1)),tri.max((0,1));keep=(terrain[:,:,0].max(1)>=lo[0]-2)&(terrain[:,:,0].min(1)<=hi[0]+2)&(terrain[:,:,2].max(1)>=lo[2]-2)&(terrain[:,:,2].min(1)<=hi[2]+2);terrain=terrain[keep];polys=shapely.polygons(terrain[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;terrain,polys=terrain[valid],polys[valid]
points=[];origins=[];bottom=row['candidate']['entry']['worldBounds'][0][1]
for i,t in enumerate(tri):
 for j,p in enumerate(t):points.append(p);origins.append(dict(faceIndex=i,kind='vertex',vertex=j))
 points.append(t.mean(0));origins.append(dict(faceIndex=i,kind='centroid'))
 for e in range(3):
  a,b=t[e],t[(e+1)%3]
  if max(a[1],b[1])>bottom+.35:continue
  steps=int(np.ceil(np.linalg.norm((b-a)[[0,2]])))
  for j in range(1,steps):points.append(a+(b-a)*j/steps);origins.append(dict(faceIndex=i,kind='edge',edge=e,step=j,steps=steps))
points=np.asarray(points);helper=module('kadoorie_samples',HERE/'xl-final-script-pass.py');heights=helper.s.context.shared.samples(points[:,[0,2]],terrain,shapely.STRtree(polys));assert np.isfinite(heights).all();gaps=points[:,1]-heights;rows=[dict(**origins[i],position=points[i].tolist(),gapM=float(gaps[i]),vertices=tri[origins[i]['faceIndex']].tolist())for i in np.flatnonzero(gaps<-.5)]
save(DOC/'samples.json.gz',dict(rows=rows,sourceSHA256=row['sourceSHA256'],installationApproved=False));ids=sorted({r['faceIndex']for r in rows});flagged=tri[ids] if ids else np.empty((0,3,3));fig,axes=plt.subplots(1,3,figsize=(18,6))
for ax,coords,label in zip(axes,[(0,2),(0,1),(2,1)],['Plan','X elevation','Z elevation']):
 ax.add_collection(PolyCollection(tri[:,:,coords],facecolors='#cbd5e1',alpha=.4,edgecolors='none'));ax.add_collection(PolyCollection(flagged[:,:,coords],facecolors='#dc2626',edgecolors='#dc2626',linewidths=.4));ax.autoscale_view();ax.set_aspect('equal');ax.ticklabel_format(useOffset=False);ax.set_title(label)
fig.suptitle('Kadoorie private terrain check: grey whole source; red faces with terrain-depth samples beyond 0.5 m');fig.tight_layout();fig.savefig(DOC/'source-context.png',dpi=150);plt.close(fig)
summary=dict(uids=[row['uid']],sourceFaces=len(tri),checks=len(points),failedSamples=len(rows),failedFaces=len(ids),minimumGapM=float(gaps.min()),failureKinds={k:sum(r['kind']==k for r in rows)for k in ['vertex','centroid','edge']},installationApproved=False,newlyInstalled=0);save(DOC/'summary.json',summary);refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py']);module('kadoorie_samples_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-government-terrain-depth-samples',refs,summary);print(summary)
