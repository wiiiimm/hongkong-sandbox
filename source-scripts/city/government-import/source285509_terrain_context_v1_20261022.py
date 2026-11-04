"""Export source-bound orthographic terrain conflict diagrams; no edits or acceptance."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-source-285509-terrain-context-v1-20261022';DOC=BASE/BATCH;UID='landsd/285509:0'
def main():
 assert not DOC.exists();refs=[Path(__file__)]
 def take(batch,path):
  _,pins=authenticate(BASE/batch);assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.extend([BASE/batch/'result.json',path]);return read(path)
 cap='government-xl-next-three-terrain-runtime-v1-20261021';g=next(r for r in take(cap,HERE/'local'/cap/'runtime-geometry.json.gz')['rows']if r['uid']==UID);tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 loc='government-xl-source-285509-failure-locations-v1-20261022';d=take(loc,BASE/loc/'failure-locations.json.gz');assert d['sourceSHA256']==g['sourceSHA256'];ids=np.asarray([i for group in d['groups']for i in group['canonicalRuntimeFaceIds']]);assert len(ids)==len(set(ids))==1020
 for group in d['groups']:assert np.array_equal(tri[group['canonicalRuntimeFaceIds']],np.asarray(group['triangles']))
 ground='government-xl-source-285509-adjacent-ground-v1-20261022';t=np.asarray(take(ground,HERE/'local'/ground/'combined-original-terrain.json.gz')['triangles']);flagged=tri[ids];DOC.mkdir(parents=True)
 for terrain_visible in [False,True]:
  fig,axes=plt.subplots(1,3,figsize=(18,6))
  for ax,coords,label in zip(axes,[(0,2),(0,1),(2,1)],['Plan X/Z','Elevation X/Y','Elevation Z/Y']):
   if terrain_visible:ax.add_collection(PolyCollection(t[:,:,coords],facecolors='#c4a484',edgecolors='#82664b',linewidths=.15,alpha=.3))
   ax.add_collection(PolyCollection(tri[:,:,coords],facecolors='#94a3b8',edgecolors='none',alpha=.4))
   ax.add_collection(PolyCollection(flagged[:,:,coords],facecolors='#dc2626',edgecolors='#b91c1c',linewidths=.15,alpha=.8))
   ax.autoscale_view();ax.set_aspect('equal');ax.set_title(label);ax.ticklabel_format(useOffset=False)
  fig.suptitle('285509 original runtime model (grey), 1020 failed faces (red)'+('; original government terrain (brown)'if terrain_visible else''));fig.tight_layout();fig.savefig(DOC/('with-terrain.png'if terrain_visible else'source-only.png'),dpi=160);plt.close(fig)
 summary=dict(uids=[UID],sourceSHA256=g['sourceSHA256'],runtimeTriangles=len(tri),failedFaces=len(ids),sourceGeometryChanges=0,installationApproved=False,qualification='Orthographic diagnostic of complete model and terrain. Draw order and transparency are not occlusion/placement acceptance. No inferred architectural identity.')
 save(DOC/'summary.json',summary);module('285509_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-bound-original-terrain-conflict-diagrams',refs,summary)
if __name__=='__main__':main()
