"""Read-only exact-source identity views; never grants installation approval."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
SRC=BASE/'government-xl-star-house-podium-identity-v2-20261020'
BATCH='government-xl-star-house-podium-source-views-v1-20261020'
DOC=BASE/BATCH
assert not DOC.exists()
r=read(SRC/'result.json')
with connect() as db:
 db.execute('SET TRANSACTION READ ONLY')
 assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
pins={e['path']:e['sha256'] for e in r['evidenceRefs']}
refs=[Path(__file__),SRC/'result.json']
def pin(p):
 assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))],p
 refs.append(p)
pin(BASE/'government-xl-star-parkview-support-v1-20261020/selection.json.gz')
row=next(x for x in read(BASE/'government-xl-star-parkview-support-v1-20261020/selection.json.gz')['rows'] if x['uid']=='landsd/231484:0')
pin(SRC/'identity.json');pin(ROOT/row['candidate']['path'])
t=np.asarray(decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes()),dtype='<f8')
assert digest(t.tobytes())==read(SRC/'identity.json')['worldTrianglesSHA256']
d=t[:,:,[0,2,1]];lo=d.min((0,1));hi=d.max((0,1))
n=np.cross(d[:,1]-d[:,0],d[:,2]-d[:,0]);norm=np.linalg.norm(n,axis=1);n=n/np.maximum(norm[:,None],1e-30)
light=np.array([.4,-.6,.7]);light/=np.linalg.norm(light)
shade=.3+.6*np.abs(n@light);colors=np.column_stack([shade*.85,shade*.91,shade,np.ones(len(t))])
DOC.mkdir()
fig=plt.figure(figsize=(15,10))
for i,az in enumerate([-65,25,115,205]):
 ax=fig.add_subplot(2,2,i+1,projection='3d');ax.add_collection3d(Poly3DCollection(d,facecolors=colors,edgecolors='none'))
 ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_zlim(lo[2],hi[2]);ax.set_box_aspect(np.maximum(hi-lo,.1));ax.view_init(20,az);ax.set_title(f'Unchanged source, azimuth {az}°');ax.set_xlabel('X');ax.set_ylabel('Z');ax.set_zlabel('Height HKPD')
fig.suptitle('landsd/231484:0 · complete original geometry · diagnostic only');fig.tight_layout();fig.savefig(DOC/'complete-source-four-views.png',dpi=160);plt.close(fig)
save(DOC/'summary.json',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],faces=len(t),worldBounds=dict(min=t.min((0,1)).tolist(),max=t.max((0,1)).tolist()),installationApproved=False,geometryChanges=0))
for p in refs[2:]:pinsha=pins[str(p.relative_to(ROOT))];assert digest(p.read_bytes())==pinsha
result=module('source_views_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-original-four-view-identity-diagnostic',refs,dict(uids=[row['uid']],installationApproved=False,geometryChanges=0))
print(result['jobId'],flush=True)
