"""Source-only exact topology and local original-surface context for two recorded conflicts."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-aqua272788-exact-foundation-conflicts-v1-20261017'
BATCH='government-xl-aqua272788-conflict-source-context-v1-20261017';DOC=BASE/BATCH
T='landsd/272788:0';P='landsd/193086:0'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={};refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:pins.setdefault(e['path'],set()).add(e['sha256'])
 def consume(p):
  assert digest(p.read_bytes())in pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 conflicts=consume(PRIOR/'conflicts.json.gz');runtime=consume(HERE/'local/government-xl-aqua272788-current-pair-v1-20261017/runtime-geometry.json.gz')
 tri={g['uid']:np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)] for g in runtime['rows']}
 assert len(tri[T])==11045 and len(tri[P])==22735
 topology_module=HERE/'opus_source_role_inventory_v1_20261017.py';topology=module('aqua_context_topology',topology_module).topology;refs.append(topology_module)
 adj,components,membership=topology(tri[T]);failed=conflicts['allCanonicalFailedFaces'];assert failed==[32,1836]
 rows=[]
 for record in conflicts['rows']:
  i=record['sourceFace'];assert digest(tri[T][i].tobytes())==record['sourceFaceSHA256']
  ring={i};front={i}
  for _ in range(3):front=set().union(*(adj[j]for j in front))-ring;ring.update(front)
  ids=components[membership[i]];cross=np.cross(tri[T][i,1]-tri[T][i,0],tri[T][i,2]-tri[T][i,0]);length=np.linalg.norm(cross)
  rows.append(dict(face=i,component=membership[i],componentFaceCount=len(ids),componentBounds=[tri[T][ids].min(axis=(0,1)).tolist(),tri[T][ids].max(axis=(0,1)).tolist()],directNeighbours=sorted(adj[i]),threeRingFaces=sorted(ring),normal=(cross/length).tolist(),areaM2=float(length/2)))
 centre=tri[T][failed].mean(axis=(0,1));radius=np.array([5.,6.,5.]);lo,hi=centre-radius,centre+radius;local={u:np.flatnonzero((t.max(1)>=lo).all(1)&(t.min(1)<=hi).all(1))for u,t in tri.items()};DOC.mkdir()
 save(DOC/'context.json.gz',dict(failedFaces=failed,rows=rows,sourceComponents=components,localBounds=[lo.tolist(),hi.tolist()],localOriginalFaces={u:[dict(index=int(i),vertices=tri[u][i].tolist())for i in ids]for u,ids in local.items()},geometryChanges=0,wholeModelAccepted=False,qualification='Exact shared-edge source topology and local bounding-box surface context only. Connectivity does not prove physical support or resolve the existing foundation failure.'))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 fig=plt.figure(figsize=(16,10));origin=centre
 for n,az in enumerate([30,120,210,300],1):
  ax=fig.add_subplot(2,2,n,projection='3d')
  for u,color in [(P,'#439cb1'),(T,'#dfbd64')]:
   t=tri[u][local[u]]-origin;ax.add_collection3d(Poly3DCollection(t[:,:,[0,2,1]],facecolor=color,edgecolor=color,alpha=.28,linewidths=.25))
  t=tri[T][failed]-origin;ax.add_collection3d(Poly3DCollection(t[:,:,[0,2,1]],facecolor='#ed2546',edgecolor='#b00020',alpha=1))
  ax.set(xlim=(-5,5),ylim=(-5,5),zlim=(-6,6),xlabel='East m',ylabel='South m',zlabel='Height m');ax.view_init(22,az);ax.set_title(f'Original facets, azimuth {az}°')
 fig.suptitle('Aqua Marine Block 2: two flagged source faces (red), tower (gold), original podium (blue)\nLocal surface context only; no acceptance or geometry edits')
 fig.tight_layout();fig.savefig(DOC/'original-junction-context.png',dpi=130);plt.close(fig)
 out=module('aqua_context_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'aqua272788-exact-source-topology-conflict-context-v1',refs,dict(uids=[T],failedFaces=failed,componentFaceCounts=[x['componentFaceCount']for x in rows],fullAcceptance=False,nextStep='Inspect original junction views and exact corresponding podium surfaces; source connectivity alone cannot resolve foundation failure.'))
 print(out['jobId'],flush=True)
if __name__=='__main__':main()
