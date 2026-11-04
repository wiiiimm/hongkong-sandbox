"""Render unchanged source context for the unresolved podium/unnamed overlap."""
from pathlib import Path
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sol-city-overlap-view-v1-20261021';DOC=BASE/BATCH
refs=[Path(__file__)];pins={}
for n in ['neighbour-recovery-v1','assembly-capture-v2','neighbour-contacts-v1']:
 f=BASE/('government-xl-sol-city-'+n+'-20261021');_,p=authenticate(f);refs.append(f/'result.json')
 for k,h in p.items():assert k not in pins or pins[k]==h;pins[k]=h
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
row=read(BASE/'government-xl-sol-city-neighbour-recovery-v1-20261021/recovery.json')['rows'][0];a=ROOT/row['assetPath'];neighbour=decode_original_world_triangles(a.read_bytes());r=next(r for r in read(BASE/'government-xl-sol-city-assembly-capture-v2-20261021/selection.json.gz')['rows']if r['uid']=='landsd/273271:0');b=ROOT/r['candidate']['path'];podium=decode_original_world_triangles(b.read_bytes())
lo,hi=neighbour.min((0,1)),neighbour.max((0,1));centre=(lo+hi)/2;keep=np.all(podium.max(1)[:,[0,2]]>=lo[[0,2]]-5,axis=1)&np.all(podium.min(1)[:,[0,2]]<=hi[[0,2]]+5,axis=1)
fig=plt.figure(figsize=(16,8))
for i,az in enumerate([35,215]):
 ax=fig.add_subplot(1,2,i+1,projection='3d')
 for tri,color,alpha in [(podium[keep],'#d68c2c',.35),(neighbour,'#2478ca',.85)]:
  q=(tri-centre)[:,:,[0,2,1]];ax.add_collection3d(Poly3DCollection(q,facecolor=color,edgecolor=color,linewidth=.15,alpha=alpha))
 ax.set_xlim(lo[0]-centre[0]-5,hi[0]-centre[0]+5);ax.set_ylim(lo[2]-centre[2]-5,hi[2]-centre[2]+5);ax.set_zlim(lo[1]-centre[1]-2,hi[1]-centre[1]+2);ax.view_init(25,az);ax.set_xlabel('east metres');ax.set_ylabel('south metres');ax.set_zlabel('height metres');ax.set_box_aspect((1,1,1));ax.set_title('Blue: unnamed 170270 · Amber: original podium crop')
fig.suptitle('Unchanged government source overlap — diagnostic crop, not acceptance');DOC.mkdir(parents=True);fig.savefig(DOC/'source-overlap.png',dpi=160);plt.close(fig)
save(DOC/'summary.json',dict(uids=['landsd/273271:0','landsd/170270:0'],podiumCropFaces=int(keep.sum()),neighbourFaces=len(neighbour),sourceGeometryChanges=0,installationApproved=False))
refs.extend(ROOT/p for p in pins);refs.extend([a,b,HERE/'exact_packed_world_geometry_20261009.py']);module('sol_overlap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-original-overlap-context-render',refs,read(DOC/'summary.json'))
