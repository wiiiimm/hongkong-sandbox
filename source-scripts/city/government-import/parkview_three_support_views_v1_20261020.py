"""Targeted unchanged-source context for unresolved Parkview support samples."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-three-support-views-v1-20261020';DOC=BASE/BATCH;SRC=BASE/'government-xl-parkview-three-four-world-contacts-v2-20261020'
assert not DOC.exists();receipt=read(SRC/'result.json')
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};refs=[Path(__file__),SRC/'result.json']
for name in ['input.json.gz','contacts.json.gz']:
 p=SRC/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
inputs=read(SRC/'input.json.gz')['rows'];accounts=read(SRC/'contacts.json.gz')['rows'];DOC.mkdir();summaries=[]
for uid in ['landsd/256113:0','landsd/255917:0','landsd/255646:0']:
 r=next(x for x in inputs if x['uid']==uid and x['mode']=='literal');account=next(x for x in accounts if x['uid']==uid and x['mode']=='literal')
 world={k:np.asarray(r[k]['position']).reshape(-1,3)[np.asarray(r[k]['index']).reshape(-1,3)]for k in ['source','support']}
 unresolved=[p for p in account['mapped']if not p['supportFacesAtOriginalPoint']];points=np.asarray([p['position']for p in unresolved]);lo=points.min(0)-3;hi=points.max(0)+3;hi[1]=max(hi[1],lo[1]+15)
 def near(t):return t[(t[:,:,0].max(1)>=lo[0])&(t[:,:,0].min(1)<=hi[0])&(t[:,:,2].max(1)>=lo[2])&(t[:,:,2].min(1)<=hi[2])&(t[:,:,1].max(1)>=lo[1])&(t[:,:,1].min(1)<=hi[1])]
 fig=plt.figure(figsize=(18,8))
 for n,az in enumerate([-55,125],1):
  ax=fig.add_subplot(1,2,n,projection='3d')
  for k,color,alpha in [('source','grey',.22),('support','steelblue',.32)]:ax.add_collection3d(Poly3DCollection(near(world[k])[:,:,[0,2,1]],facecolor=color,alpha=alpha,edgecolor='none'))
  ax.scatter(points[:,0],points[:,2],points[:,1],color='red',s=14,depthshade=False);ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[2],hi[2]);ax.set_zlim(lo[1],hi[1]);ax.set_box_aspect((hi-lo)[[0,2,1]]);ax.view_init(20,az);ax.set_title(uid+' original tower grey / podium blue / unresolved red\nContext crop only; all source facets remain unchanged')
 fig.tight_layout();path=DOC/(uid.split('/')[1]+'-junctions.png');fig.savefig(path,dpi=150);plt.close(fig)
 summaries.append(dict(uid=uid,unresolved=len(points),contextBounds=[lo.tolist(),hi.tolist()],sourceWorldSHA256=r['sourceWorldSHA256'],supportWorldSHA256=r['supportWorldSHA256'],image=str(path.relative_to(ROOT))))
module('parkview_support_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-unresolved-support-context-views',refs,dict(uids=[r['uid']for r in summaries],rows=summaries,installationApproved=False,modelGeometryChanges=0))
