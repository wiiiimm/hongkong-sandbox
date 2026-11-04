"""Locate remaining buried original faces; diagnostic only, no acceptance overrides."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-murray-current-pair-physical-v1-20261017'
BATCH='government-xl-murray-buried-faces-v1-20261017';DOC=BASE/BATCH
RT=HERE/'local'/PRIOR.name/'runtime-geometry.json.gz'
def main():
 assert not DOC.exists()
 receipt=read(PRIOR/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for path,sha in {(r['path'],r['sha256']) for r in receipt['evidenceRefs']}:assert digest((ROOT/path).read_bytes())==sha
 final=module('oi_buried_final',HERE/'xl-final-script-pass.py')
 geo={r['uid']:r for r in read(RT)['rows']}
 def triangles(g):return np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 uid='landsd/248655:0';g=geo[uid];t=triangles(g);ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);podium=ground
 points=np.concatenate([t,t.mean(axis=1)[:,None,:]],axis=1)
 def sample(mesh):
  polygons=shapely.polygons(mesh[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10
  return final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),mesh[valid],shapely.STRtree(polygons[valid])).reshape(-1,4)
 gh=sample(ground);ph=sample(podium);highest=np.fmax(gh,ph);gaps=points[:,:,1]-highest;buried=np.isfinite(highest).all(axis=1)&(gaps<-.5).all(axis=1)
 expected=next(x['foundation'] for x in read(PRIOR/'foundations.json')['rows'] if x['uid']==uid)
 assert int(buried.sum())==expected['fullyBuriedTriangles']==13
 rows=[]
 for i in np.flatnonzero(buried):
  p=t[i];cross=np.cross(p[1]-p[0],p[2]-p[0]);rows.append(dict(faceIndex=int(i),vertices=p.tolist(),samplePoints=points[i].tolist(),groundHeights=gh[i].tolist(),podiumHeights=ph[i].tolist(),highestGaps=gaps[i].tolist(),groundOnlyGaps=(points[i,:,1]-gh[i]).tolist(),areaM2=float(np.linalg.norm(cross)/2),normal=(cross/np.linalg.norm(cross)).tolist(),allSamplesHigherOnPodium=bool((ph[i]>gh[i]).all())))
 assert abs(sum(r['areaM2'] for r in rows)-expected['fullyBuriedAreaM2'])<1e-10
 save(DOC/'faces.json',dict(uid=uid,sourceSHA256=g['sourceSHA256'],rows=rows,strictAcceptanceUnchanged=True,installationApproved=False))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 fig=plt.figure(figsize=(12,6),dpi=160)
 for n,azim in enumerate([-55,125],1):
  ax=fig.add_subplot(1,2,n,projection='3d');origin=t.min(axis=(0,1));lo=t.min(axis=(0,1))-1;hi=t.max(axis=(0,1))+1
  nearby=podium[(podium[:,:,0].max(axis=1)>=lo[0])&(podium[:,:,0].min(axis=1)<=hi[0])&(podium[:,:,2].max(axis=1)>=lo[2])&(podium[:,:,2].min(axis=1)<=hi[2])&(podium[:,:,1].max(axis=1)>=lo[1])]
  for mesh,color,alpha in [(nearby,'#a7adb5',.12),(t,'#287bb5',.25),(t[buried],'#d62728',1)]:
   v=(mesh-origin)[:,:,[0,2,1]];ax.add_collection3d(Poly3DCollection(v,facecolors=color,edgecolors=color,linewidths=.3,alpha=alpha))
  span=hi-lo;ax.set(xlim=(-1,span[0]-1),ylim=(-1,span[2]-1),zlim=(-1,span[1]-1),xlabel='East offset (m)',ylabel='South offset (m)',zlabel='Height offset (m)',title='Original Murray podium; buried faces red');ax.view_init(elev=22,azim=azim);ax.set_box_aspect(span[[0,2,1]])
 fig.tight_layout();fig.savefig(DOC/'buried-original-faces.png');plt.close(fig)
 out=module('oi_faces_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'murray-exact-original-buried-face-location-v1',[Path(__file__),RT,PRIOR/'result.json',PRIOR/'foundations.json',HERE/'xl-final-script-pass.py'],dict(uids=[uid],rows=rows,fullAcceptance=False,nextStep='Thirteen exact podium faces remain subject to current terrain acceptance; investigate authenticated original terrain without modifying building geometry.'))
 print(dict(jobId=out['jobId'],rows=rows),flush=True)
if __name__=='__main__':main()
