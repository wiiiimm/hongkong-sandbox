"""Render immutable Illumination source wall and original ground for physical review."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-illumination-wall-context-view-v1-20261021';DOC=BASE/BATCH

def main():
 assert not DOC.exists();refs=[Path(__file__)]
 def take(n,p):
  _,pins=authenticate(BASE/n);assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([BASE/n/'result.json',p]);return read(p)
 c='government-xl-illumination-low-edge-context-v1-20261021';ctx=take(c,BASE/c/'context.json')
 n='government-xl-illumination-inset-runtime-v1-20261021';runtime=take(n,HERE/'local'/n/'runtime-geometry.json.gz');r=next(r for r in runtime['rows']if r['uid']=='landsd/258737:0');assert r['sourceSHA256']==ctx['sourceSHA256']
 t=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];assert np.array_equal(t[1044],ctx['vertices'])
 n='government-xl-illumination-original-ground-v1-20261021';ground=np.asarray(take(n,HERE/'local'/n/'original-terrain.json.gz')['triangles'])
 n='government-xl-illumination-wall-profile-v1-20261021';profile=take(n,BASE/n/'profile.json')
 lo=t[1044].min(0)-3;hi=t[1044].max(0)+3
 def near(a):return a[(a[:,:,0].max(1)>=lo[0])&(a[:,:,0].min(1)<=hi[0])&(a[:,:,2].max(1)>=lo[2])&(a[:,:,2].min(1)<=hi[2])]
 DOC.mkdir();fig=plt.figure(figsize=(16,7))
 for k,az in enumerate([-60,120],1):
  ax=fig.add_subplot(1,2,k,projection='3d')
  for a,color,alpha in [(near(t),'grey',.12),(near(ground),'seagreen',.5),(t[[1044]],'orange',.85)]:
   ax.add_collection3d(Poly3DCollection(a[:,:,[0,2,1]],facecolor=color,edgecolor=color,linewidth=.25,alpha=alpha))
  p=np.asarray([x['position']for x in ctx['samples']]);ax.scatter(p[:,0],p[:,2],p[:,1],color='red',s=15)
  ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[2],hi[2]);ax.set_zlim(lo[1],hi[1]);ax.set_box_aspect((hi-lo)[[0,2,1]]);ax.view_init(20,az)
  ax.set_title('Original facade 1044 (orange), government terrain (green)\nRaw failed bottom-edge samples (red); adjacent original faces (grey)')
 fig.tight_layout();fig.savefig(DOC/'source-context.png',dpi=150);plt.close(fig)
 fig,ax=plt.subplots(figsize=(12,4));rows=profile['rows'];x=[p['fraction']for p in rows]
 for key,label in [('bottom','Original wall bottom'),('originalGround','Original ground'),('wallTop','Actual triangular face upper edge')]:ax.plot(x,[p[key]for p in rows],label=label)
 ax.set_xlabel('Fraction along original bottom edge');ax.set_ylabel('Height in viewer coordinates (m)');ax.legend();fig.tight_layout();fig.savefig(DOC/'wall-profile.png',dpi=150);plt.close(fig)
 summary=dict(uids=[r['uid']],sourceSHA256=r['sourceSHA256'],faceIndex=1044,sourceGeometryChanges=0,physicalReviewApproved=False,installationApproved=False,rawFailuresPreserved=True)
 save(DOC/'summary.json',summary);module('illumination_wall_view_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-wall-terrain-context-views',refs,summary);print(summary,flush=True)
if __name__=='__main__':main()
