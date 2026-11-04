"""Source-bound orthographic and oblique contact context, no geometry modification."""
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
BASE=ROOT/'docs/astra-city/government-import';SRC=BASE/'government-xl-grandiose-clubhouse-original-contact-v1-20261021';BATCH='government-xl-grandiose-clubhouse-contact-view-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists()
r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json'];pins={e['path']:e['sha256'] for e in r['evidenceRefs']}
with connect() as db:
 db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
def take(p):
 assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return p.read_bytes()
p=SRC/'contacts.json.gz';take(p);contacts=read(p)['contacts'];tri=[]
for sha in ['205606ffc6076f33d504f33878067b7e2aa72d62baa9e22f712b1e80e8db99e5','0f061357cde3fd4e582f2544986eb4a5a8b52e9dd4d0f29cc66077135c71f4e5']:
 tri.append(decode_original_world_triangles(take(HERE/'local/government-xl-thirty-spatial-original-closures-20261008/assets'/(sha+'.glb.gz'))))
ids=[sorted({c[k] for c in contacts}) for k in ['sourceFaceA','sourceFaceB']];selected=[a[i] for a,i in zip(tri,ids)];vertices=np.concatenate(selected).reshape(-1,3);lo=vertices.min(0);hi=vertices.max(0);center=(lo+hi)/2
save(DOC/'context.json',dict(uids=r['uids'],contactFaceIds=ids,contactFaceBounds=[lo.tolist(),hi.tolist()],installationApproved=False))
fig=plt.figure(figsize=(16,11))
for n,(coords,title) in enumerate([((0,2),'Plan'),((0,1),'X elevation'),((2,1),'Z elevation')],1):
 ax=fig.add_subplot(2,2,n)
 for a,color in zip(tri,['#0891b2','#d97706']):ax.add_collection(PolyCollection(a[:,:,coords],facecolors=color,alpha=.18,edgecolors='none'))
 for a,color in zip(selected,['#0369a1','#c2410c']):ax.add_collection(PolyCollection(a[:,:,coords],facecolors=color,alpha=.7,edgecolors=color,linewidths=.4))
 ax.set_xlim(lo[coords[0]]-4,hi[coords[0]]+4);ax.set_ylim(lo[coords[1]]-4,hi[coords[1]]+4);ax.set_aspect('equal');ax.set_title(title);ax.ticklabel_format(useOffset=False)
ax=fig.add_subplot(224,projection='3d')
for a,color in zip(selected,['#0369a1','#c2410c']):ax.add_collection3d(Poly3DCollection((a-center)[:,:,[0,2,1]],facecolors=color,alpha=.7,edgecolors=color,linewidths=.3))
span=np.maximum(hi-lo,1)
ax.set_xlim(-span[0]/2,span[0]/2);ax.set_ylim(-span[2]/2,span[2]/2);ax.set_zlim(-span[1]/2,span[1]/2);ax.set_box_aspect(span[[0,2,1]]);ax.view_init(25,35);ax.set_title('Oblique contact faces only; context omitted')
fig.suptitle('PopCorn 2 blue / clubhouse orange — original source diagnostic; not clearance proof');fig.tight_layout();fig.savefig(DOC/'contact-context.png',dpi=150);plt.close(fig)
refs.append(HERE/'exact_packed_world_geometry_20261009.py')
module('contact_view_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-contact-visual-context',refs,dict(uids=r['uids'],contactFaceCounts=list(map(len,ids)),installationApproved=False,geometryChanges=0))
print(ids)
