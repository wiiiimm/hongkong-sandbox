"""Export source-only views of all four flagged lower-wall facets."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-14-four-face-views-v1-20261021';DOC=BASE/BATCH;CAP=BASE/'government-xl-parkview-13-14-current-runtime-v2-20261021';FACE=BASE/'government-xl-parkview-14-four-faces-v1-20261021'
assert not DOC.exists();_,pins=authenticate(CAP);_,fp=authenticate(FACE);p=HERE/'local'/CAP.name/'runtime-geometry.json.gz';f=FACE/'faces.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]and digest(f.read_bytes())==fp[str(f.relative_to(ROOT))];g={r['uid']:r for r in read(p)['rows']}
def world(r):return np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]
t=world(g['landsd/253980:0']);s=world(g['landsd/254491:0']);rows=read(f)['rows'];ids=[r['faceId']for r in rows];selected=t[ids]
assert np.array_equal(selected,np.asarray([r['vertices']for r in rows]));lo=selected.min((0,1))-4;hi=selected.max((0,1))+4
near=lambda a:a[(a[:,:,0].max(1)>=lo[0])&(a[:,:,0].min(1)<=hi[0])&(a[:,:,2].max(1)>=lo[2])&(a[:,:,2].min(1)<=hi[2])&(a[:,:,1].min(1)<=hi[1])&(a[:,:,1].max(1)>=lo[1])]
DOC.mkdir();fig=plt.figure(figsize=(14,8))
for n,az in enumerate([-45,135],1):
 ax=fig.add_subplot(1,2,n,projection='3d')
 for arr,color,alpha in [(near(s),'steelblue',.25),(near(t),'grey',.15),(selected,'red',1)]:ax.add_collection3d(Poly3DCollection(arr[:,:,[0,2,1]],facecolor=color,edgecolor='none',alpha=alpha))
 ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[2],hi[2]);ax.set_zlim(lo[1],hi[1]);ax.set_box_aspect((hi-lo)[[0,2,1]]);ax.view_init(20,az);ax.set_title('Block14 four original wall facets (red); podium (blue)')
fig.tight_layout();fig.savefig(DOC/'wall-context.png',dpi=140);plt.close(fig)
module('park14_face_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-original-wall-facet-source-views',[Path(__file__),p,f,CAP/'result.json',FACE/'result.json'],dict(uids=['landsd/253980:0'],faceIds=ids,sourceOnly=True,installationApproved=False))
