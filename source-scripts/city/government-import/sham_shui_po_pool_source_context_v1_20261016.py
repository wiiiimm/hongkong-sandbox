"""Render unchanged original source context; no generated model geometry."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-sham-shui-po-pool-source-context-v1-20261016';DOC=ROOT/'docs/astra-city/government-import'/BATCH;PRIOR=DOC.parent/'government-xl-sham-shui-po-pool-original-terrain-v1-20261016'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256'];refs.append(ROOT/q['path'])
 x=read(PRIOR/'buried-source-context.json.gz');floor=np.asarray(x['triangles']);near=np.asarray(x['neighbourTriangles']);g=read(HERE/'local/government-xl-sham-shui-po-pool-current-ground-v1-20261016/runtime-geometry.json.gz')['rows'][0];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];DOC.mkdir()
 fig=plt.figure(figsize=(16,8));ax=fig.add_subplot(121);ax.add_collection(PolyCollection(t[:,:,[0,2]],facecolor='#cbd5e1',edgecolor='#64748b',linewidth=.2));ax.add_collection(PolyCollection(floor[:,:,[0,2]],facecolor='#ef4444',edgecolor='#991b1b',linewidth=.3));ax.autoscale();ax.set_aspect('equal');ax.set_xlabel('World X (m)');ax.set_ylabel('World Z (m)');ax.set_title('Whole original source; buried component red')
 ax=fig.add_subplot(122,projection='3d');reorder=lambda a:a[:,:,[0,2,1]];ax.add_collection3d(Poly3DCollection(reorder(near),facecolor='#cbd5e1',edgecolor='#64748b',linewidth=.25,alpha=.65));ax.add_collection3d(Poly3DCollection(reorder(floor),facecolor='#ef4444',edgecolor='#991b1b',linewidth=.4));lo=near.min(axis=(0,1));hi=near.max(axis=(0,1));ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[2],hi[2]);ax.set_zlim(lo[1]-.2,hi[1]+.2);ax.set_box_aspect([hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]+.4]);ax.view_init(elev=32,azim=-65);ax.set_xlabel('World X');ax.set_ylabel('World Z');ax.set_zlabel('Height (m)');ax.set_title('Original nearby faces, unchanged coordinates')
 fig.tight_layout();fig.savefig(DOC/'source-context.png',dpi=140);plt.close(fig)
 save(DOC/'context.json',dict(uid='landsd/265480:0',sourceSHA256=x['sourceSHA256'],sourceFaces=len(t),buriedFaces=len(floor),nearbySourceFaces=len(near),nearbyBounds=[lo.tolist(),hi.tolist()],classificationPending=True,geometryEdits=0,publication=False))
 out=module('pool_context_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-pool-flat-region-source-context-v1',list(dict.fromkeys(refs)),dict(uids=['landsd/265480:0'],fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId']),flush=True)
if __name__=='__main__':main()
