"""Original source extent context with official footprint; no acceptance."""
from pathlib import Path
import numpy as np,shapely,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho300857-extent-views-v1-20261020';DOC=BASE/BATCH;SRC=BASE/'government-xl-yoho300857-podium-extent-diagnostic-v3-20261020';CAP=BASE/'government-xl-next-twenty-current-terrain-v2-20261020'
assert not DOC.exists();r=read(SRC/'result.json');pins={x['path']:x['sha256']for x in r['evidenceRefs']}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
sel=CAP/'selection.json.gz';assert digest(sel.read_bytes())==pins[str(sel.relative_to(ROOT))];row=next(x for x in read(sel)['rows']if x['uid']=='landsd/301636:0');asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];t=decode_original_world_triangles(asset.read_bytes());ext=SRC/'extensions.json.gz';assert digest(ext.read_bytes())==pins[str(ext.relative_to(ROOT))];ids=np.array([x['faceId']for x in read(ext)['rows']]);origin=t.reshape(-1,3).mean(0);v=t-origin;DOC.mkdir()
fig,ax=plt.subplots(figsize=(12,10));ax.add_collection(PolyCollection(v[:,:,[0,2]],facecolors='#abc8d8',edgecolors='none'));ax.add_collection(PolyCollection(v[ids][:,:,[0,2]],facecolors='#d65d48',edgecolors='none'))
for ring in row['source']['building']['rings']:
 q=np.array(ring)-origin[[0,2]];ax.plot(q[:,0],q[:,1],color='black',linewidth=1)
ax.autoscale_view();ax.set_aspect('equal');ax.set(xlabel='East offset (m)',ylabel='South offset (m)',title='Original podium projection; black = official footprint\nRed = faces with a vertex >1m outside footprint (diagnostic selection)');fig.savefig(DOC/'plan.png',dpi=130);plt.close(fig)
fig=plt.figure(figsize=(15,7))
for j,az in enumerate([35,215]):
 ax=fig.add_subplot(1,2,j+1,projection='3d');ax.add_collection3d(Poly3DCollection(v[:,:,[0,2,1]],facecolors='#abc8d8',edgecolors='none',alpha=.5));ax.add_collection3d(Poly3DCollection(v[ids][:,:,[0,2,1]],facecolors='#d65d48',edgecolors='none',alpha=.9));lo=v.min((0,1));hi=v.max((0,1));ax.set(xlim=(lo[0],hi[0]),ylim=(lo[2],hi[2]),zlim=(lo[1],hi[1]));ax.set_box_aspect((hi-lo)[[0,2,1]]);ax.view_init(elev=25,azim=az)
fig.suptitle('Unchanged original podium, extent-selected faces red; transparent context is not visibility proof');fig.savefig(DOC/'oblique.png',dpi=130);plt.close(fig)
module('yoho_extent_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-podium-extent-visual-context',[Path(__file__),SRC/'result.json',sel,asset,ext,HERE/'exact_packed_world_geometry_20261009.py'],dict(uids=[row['uid']],installationApproved=False,sourceFaces=len(t),selectedFaces=len(ids)))
