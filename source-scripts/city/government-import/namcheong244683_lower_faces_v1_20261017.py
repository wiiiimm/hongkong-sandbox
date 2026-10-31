"""Locate source faces implicated by current strict terrain penetration warning."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-namcheong244683-current-capture-v1-20261017';BATCH='government-xl-namcheong244683-lower-faces-v1-20261017';DOC=BASE/BATCH;RT=HERE/'local'/CAP.name/'runtime-geometry.json.gz'
def main():
 assert not DOC.exists();r=read(CAP/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 g=read(RT)['rows'][0];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);assert len(t)==20645
 points=np.concatenate([t,t.mean(axis=1)[:,None,:]],axis=1);polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;final=module('nam_lower_sample',HERE/'xl-final-script-pass.py');heights=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),ground[valid],shapely.STRtree(polys[valid])).reshape(-1,4);gaps=points[:,:,1]-heights;failed=np.any(gaps<-.5,axis=1);rows=[]
 for i in np.flatnonzero(failed):
  p=t[i];n=np.cross(p[1]-p[0],p[2]-p[0]);length=np.linalg.norm(n);rows.append(dict(faceIndex=int(i),vertices=p.tolist(),samplePoints=points[i].tolist(),groundHeights=heights[i].tolist(),gaps=gaps[i].tolist(),areaM2=float(length/2),normal=(n/length).tolist()if length else None))
 save(DOC/'faces.json.gz',dict(uid=g['uid'],sourceSHA256=g['sourceSHA256'],sourceTriangles=len(t),rows=rows,minimumGap=float(np.nanmin(gaps)),fullAcceptance=False,qualification='Exact original faces implicated by vertex/centroid samples; not a full continuous penetration classification. No geometry edits or acceptance override.'))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 fig=plt.figure(figsize=(14,6),dpi=140);origin=t.min(axis=(0,1));span=t.max(axis=(0,1))-origin
 for i,az in enumerate([-45,135],1):
  ax=fig.add_subplot(1,2,i,projection='3d')
  for mesh,color,alpha in [(t,'#6c98ac',.12),(t[failed],'#d63333',.95)]:ax.add_collection3d(Poly3DCollection((mesh-origin)[:,:,[0,2,1]],facecolors=color,edgecolors=color,linewidths=.1,alpha=alpha))
  ax.set(xlim=(0,span[0]),ylim=(0,span[2]),zlim=(0,span[1]),xlabel='East offset m',ylabel='South offset m',zlabel='Height offset m',title='Original car park: warned faces red');ax.set_box_aspect(span[[0,2,1]]);ax.view_init(elev=22,azim=az)
 fig.tight_layout();fig.savefig(DOC/'lower-face-context.png');plt.close(fig)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 out=module('nam_lower_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'namcheong244683-current-lower-source-face-diagnostic-v1',[Path(__file__),CAP/'result.json',RT,HERE/'xl-final-script-pass.py',*[ROOT/p for p in pins]],dict(uids=[g['uid']],affectedFaces=len(rows),fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],affectedFaces=len(rows),normalYRange=[min(r['normal'][1]for r in rows if r['normal']),max(r['normal'][1]for r in rows if r['normal'])]),flush=True)
if __name__=='__main__':main()
