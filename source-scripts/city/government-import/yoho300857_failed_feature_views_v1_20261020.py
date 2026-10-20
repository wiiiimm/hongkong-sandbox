"""Cropped original geometry around actual failed facets; diagnostic only."""
from pathlib import Path
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho300857-failed-feature-views-v1-20261020';DOC=BASE/BATCH;SRC=BASE/'government-xl-yoho300857-buried-faces-v1-20261020';CAP=BASE/'government-xl-yoho300857-private-terrain-capture-v2-20261020'
assert not DOC.exists();r=read(SRC/'result.json');pins={x['path']:x['sha256']for x in r['evidenceRefs']};refs=[Path(__file__),SRC/'result.json']
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
p=HERE/'local'/CAP.name/'runtime-geometry.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);rows=read(p)['rows'];worlds={r['uid']:np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]for r in rows};DOC.mkdir();notes=[]
for row in rows:
 uid=row['uid'];p=SRC/(uid.split('/')[1]+'.json');assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);f=read(p);ids=[x['faceId']for x in f['rows']];t=worlds[uid];origin=t[ids].reshape(-1,3).mean(0);radius=5;ground=np.asarray(row['drawnGroundGeometry']).reshape(-1,3,3);fig=plt.figure(figsize=(14,7))
 def crop(v):return v[((v.max(1)>=origin-radius)&(v.min(1)<=origin+radius)).all(1)]
 for j,az in enumerate([35,215]):
  ax=fig.add_subplot(1,2,j+1,projection='3d',computed_zorder=False)
  for v,color in [(worlds['landsd/301636:0'],'#b28a35'),(worlds['landsd/300857:0'],'#287dad'),(ground,'#3c9958')]:ax.add_collection3d(Poly3DCollection((crop(v)-origin)[:,:,[0,2,1]],facecolors='none',edgecolors=color,linewidths=.6,alpha=.6,zorder=1))
  ax.add_collection3d(Poly3DCollection((t[ids]-origin)[:,:,[0,2,1]],facecolors='red',edgecolors='darkred',alpha=.8,zorder=5));ax.set(xlim=(-radius,radius),ylim=(-radius,radius),zlim=(-radius,radius));ax.set_box_aspect([1,1,1]);ax.view_init(elev=20,azim=az)
 fig.suptitle(uid+' flagged facets red; podium gold, tower blue, drawn terrain green\nHighlight drawn on top; no visibility or structural proof');fig.savefig(DOC/(uid.split('/')[1]+'.png'),dpi=140);plt.close(fig);notes.append(dict(uid=uid,faceIds=ids,origin=origin.tolist(),radiusM=radius))
save(DOC/'context.json',dict(rows=notes,installationApproved=False));module('yoho_features_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'actual-failed-source-feature-context',refs,dict(uids=list(worlds),installationApproved=False))
