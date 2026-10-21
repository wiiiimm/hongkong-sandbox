"""Inspect the exact original elevated component in 3D; no reconstructed geometry."""
from pathlib import Path
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-stonecutters-component-shape-v1-20261021';DOC=BASE/BATCH;refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py'];assert not DOC.exists()
def take(n,f):
 _,pins=authenticate(BASE/n);p=BASE/n/f;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([BASE/n/'result.json',p]);return read(p)
c=take('government-xl-stonecutters-far-components-v1-20261021','components.json');row=next(r for r in take('government-xl-next-twenty-current-terrain-v6-20261021','selection.json.gz')['rows']if r['uid']==c['uids'][0]);p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==c['sourceSHA256'];refs.append(p);t=decode_original_world_triangles(p.read_bytes());assert digest(t.astype('<f8').tobytes())==c['worldTrianglesSHA256'];comp=c['components'][0];ids=comp['faceIds'];far=set(comp['farFaceIds']);v=t[ids][:,:,[0,2,1]];lo=v.min((0,1));hi=v.max((0,1));mid=(lo+hi)/2;v=v-mid
fig=plt.figure(figsize=(14,8))
for i,az in enumerate([30,120,210,300],1):
 ax=fig.add_subplot(2,2,i,projection='3d');ax.add_collection3d(Poly3DCollection(v,facecolors=['#d85b34'if j in far else'#779ba9'for j in ids],edgecolors='#27353a',linewidths=.25));span=hi-lo
 ax.set(xlim=(-span[0]/2,span[0]/2),ylim=(-span[1]/2,span[1]/2),zlim=(-span[2]/2,span[2]/2));ax.set_box_aspect(span);ax.view_init(elev=25,azim=az);ax.set_title(f'Original component · azimuth {az}°');ax.set_axis_off()
fig.suptitle('350 original faces; orange = 18 faces beyond the footprint check (display axes reordered only)');fig.tight_layout();DOC.mkdir();fig.savefig(DOC/'component-3d.png',dpi=150);plt.close(fig)
module('stone_shape',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-component-three-dimensional-views',refs,dict(uids=c['uids'],sourceGeometryChanges=0,installationApproved=False,reviewOnly=True))
