"""Exact source/terrain context for all Murray buried faces; no acceptance or geometry edits."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-murray-original-terrain-foundation-v3-20261017'
PHYSICAL=BASE/'government-xl-murray-current-pair-physical-v1-20261017'
BATCH='government-xl-murray-original-buried-surface-context-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in {(e['path'],e['sha256'])for e in r['evidenceRefs']}:assert digest((ROOT/p).read_bytes())==h,p
 comparison=read(PRIOR/'flagged-face-comparison.json');files=[f for part in comparison['source'].values()for f in part['sourceFiles']]
 second=module('murray_context_decoder',HERE/'xl-second-pass.py');second.LOCAL=HERE/'local'/BATCH
 terrain=np.concatenate([second.terrain_triangles(ROOT/e['path'])for e in files if e['path'].endswith('.gltf')]);assert len(terrain)==611436
 rtpath=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';g=next(x for x in read(rtpath)['rows']if x['uid']=='landsd/248655:0')
 t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 lo,hi=t.min(axis=(0,1))-2,t.max(axis=(0,1))+2;ground=terrain[(terrain[:,:,0].max(axis=1)>=lo[0])&(terrain[:,:,0].min(axis=1)<=hi[0])&(terrain[:,:,2].max(axis=1)>=lo[2])&(terrain[:,:,2].min(axis=1)<=hi[2])]
 final=module('murray_context_foundation',HERE/'xl-final-script-pass.py');points=np.concatenate([t,t.mean(axis=1)[:,None,:]],axis=1)
 polygons=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10
 heights=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),ground[valid],shapely.STRtree(polygons[valid])).reshape(-1,4)
 assert np.isfinite(heights).all();gaps=points[:,:,1]-heights;buried=(gaps<-.5).all(axis=1);assert int(buried.sum())==10
 cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(cross,axis=1)/2;normals=np.divide(cross,2*area[:,None],out=np.zeros_like(cross),where=area[:,None]>0)
 assert abs(float(area[buried].sum())-read(PRIOR/'foundation.json')['fullyBuriedAreaM2'])<1e-9
 # Exact position adjacency is context, never a structural-root requirement.
 incidence={}
 for i,face in enumerate(t):
  for v in face:incidence.setdefault(tuple(v),set()).add(i)
 rows=[]
 for i in np.flatnonzero(buried):
  adjacent=sorted(set.union(*(incidence[tuple(v)]for v in t[i]))-{int(i)})
  rows.append(dict(faceIndex=int(i),vertices=t[i].tolist(),normal=normals[i].tolist(),areaM2=float(area[i]),sampleGaps=gaps[i].tolist(),adjacentFaces=[dict(faceIndex=j,normal=normals[j].tolist(),buried=bool(buried[j]),gapRange=[float(gaps[j].min()),float(gaps[j].max())])for j in adjacent]))
 groups=final.connected_components(t,buried);save(DOC/'exact-face-context.json',dict(uid=g['uid'],sourceSHA256=g['sourceSHA256'],rows=rows,groups=[[int(i)for i in ids]for ids in groups],geometryModified=False,installationApproved=False))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 for n,ids in enumerate(groups):
  core=t[ids];lower=core.min(axis=(0,1))-3;upper=core.max(axis=(0,1))+3
  def nearby(mesh):return mesh[(mesh[:,:,0].max(axis=1)>=lower[0])&(mesh[:,:,0].min(axis=1)<=upper[0])&(mesh[:,:,2].max(axis=1)>=lower[2])&(mesh[:,:,2].min(axis=1)<=upper[2])&(mesh[:,:,1].max(axis=1)>=lower[1])&(mesh[:,:,1].min(axis=1)<=upper[1])]
  fig=plt.figure(figsize=(13,6),dpi=150)
  for view,azim in enumerate([-65,115],1):
   ax=fig.add_subplot(1,2,view,projection='3d')
   for mesh,color,alpha in [(nearby(ground),'#8c9b72',.28),(nearby(t),'#3984b8',.16),(core,'#d52e32',1)]:
    ax.add_collection3d(Poly3DCollection((mesh-lower)[:,:,[0,2,1]],facecolors=color,edgecolors=color,linewidths=.3,alpha=alpha))
   span=upper-lower;ax.set(xlim=(0,span[0]),ylim=(0,span[2]),zlim=(0,span[1]),xlabel='East (m)',ylabel='South (m)',zlabel='Height (m)',title=f'Original group {n+1}: faces '+','.join(map(str,ids)));ax.set_box_aspect(span[[0,2,1]]);ax.view_init(elev=22,azim=azim)
  fig.tight_layout();fig.savefig(DOC/f'group-{n+1}.png');plt.close(fig)
 refs=[Path(__file__),PRIOR/'result.json',PRIOR/'flagged-face-comparison.json',PRIOR/'foundation.json',rtpath,HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py']+[ROOT/e['path']for e in files]
 refs.extend(p for p in (HERE/'local'/BATCH).rglob('*')if p.is_file())
 out=module('murray_context_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'murray-original-buried-surface-context-v1',refs,dict(uids=[g['uid']],sourceSHA256=g['sourceSHA256'],faceIndices=[x['faceIndex']for x in rows],groups=len(groups),fullAcceptance=False,nextStep='Review exact source-authored surface roles using these unchanged source/terrain views; preserve all strict failures and current physical checks.'))
 print(dict(jobId=out['jobId'],faces=[x['faceIndex']for x in rows],groups=len(groups)),flush=True)
if __name__=='__main__':main()
