"""Source-only oblique context for the one recorded buried podium facet."""
from pathlib import Path
import importlib.util
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-primrose-podium-current-physical-20261007';BATCH='government-xl-primrose-podium-buried-face-context-v1-20261015';DOC=BASE/BATCH

def main():
 assert not DOC.exists();receipt=read(OLD/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for q in receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 row=read(OLD/'selection.json.gz')['rows'][0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']
 tri=decode_original_world_triangles(asset.read_bytes());cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(cross,axis=1)/2
 stats=read(OLD/'foundation.json')['rows'][0]['foundation'];matches=np.flatnonzero((np.max(np.abs(tri[:,:,1]-stats['components'][0]['yRange'][0]),axis=1)<1e-8)&(np.abs(area-stats['fullyBuriedAreaM2'])<1e-8));assert len(matches)==1;i=int(matches[0]);face=tri[i];centre=face.mean(axis=0)
 runtime=HERE/'local'/OLD.name/'runtime-geometry.json.gz';rt=read(runtime)['rows'][0];assert rt['uid']==row['uid']and rt['sourceSHA256']==row['sourceSHA256'];ground=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3)
 target_edges={tuple(sorted((tuple(face[a]),tuple(face[(a+1)%3]))))for a in range(3)};adj=[]
 for j,t in enumerate(tri):
  if j==i:continue
  edges={tuple(sorted((tuple(t[a]),tuple(t[(a+1)%3]))))for a in range(3)};common=edges&target_edges
  if common:adj.append(dict(sourceFace=j,sharedWholeEdges=len(common),normal=cross[j].tolist(),vertices=t.tolist()))
 DOC.mkdir();save(DOC/'context.json',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],sourceFace=i,vertices=face.tolist(),unnormalisedNormal=cross[i].tolist(),areaM2=float(area[i]),exactSharedEdgeNeighbours=adj,rawFoundation=stats,qualification='Exact source facet identified by the saved unique area and height. Oblique diagrams are source context only; terrain is the historical captured candidate, not a current-map clearance approval.',installationApproved=False))
 near=np.all(tri.max(axis=1)>=centre-np.array([12,20,12]),axis=1)&np.all(tri.min(axis=1)<=centre+np.array([12,20,12]),axis=1)
 ng=(ground[:,:,0].max(axis=1)>=centre[0]-12)&(ground[:,:,0].min(axis=1)<=centre[0]+12)&(ground[:,:,2].max(axis=1)>=centre[2]-12)&(ground[:,:,2].min(axis=1)<=centre[2]+12)
 for title,azim in [('southeast',-55),('northwest',125)]:
  fig=plt.figure(figsize=(14,7));
  for n,with_ground in enumerate([False,True]):
   ax=fig.add_subplot(1,2,n+1,projection='3d');pieces=tri[near]-centre
   ax.add_collection3d(Poly3DCollection(pieces[:,:,[0,2,1]],facecolor='#a7b9c7',edgecolor='#657785',linewidths=.25,alpha=.35))
   ax.add_collection3d(Poly3DCollection((face[None]-centre)[:,:,[0,2,1]],facecolor='red',edgecolor='darkred',linewidths=2,alpha=1))
   if with_ground:ax.add_collection3d(Poly3DCollection((ground[ng]-centre)[:,:,[0,2,1]],facecolor='#86b879',edgecolor='#47713c',linewidths=.25,alpha=.35))
   ax.set(xlim=(-12,12),ylim=(-12,12),zlim=(-15,20),xlabel='X offset (m)',ylabel='Z offset (m)',zlabel='Height offset (m)',title=('Source only'if not with_ground else'Historical source-terrain context'));ax.view_init(elev=23,azim=azim)
  fig.suptitle(f'Primrose podium source face {i} — red; unchanged source, transparent diagnostic context');fig.tight_layout();fig.savefig(DOC/(title+'.png'),dpi=160);plt.close(fig)
 refs=[ROOT/q['path']for q in receipt['evidenceRefs']]+[OLD/'result.json',runtime,asset,Path(__file__),HERE/'exact_packed_world_geometry_20261009.py']
 spec=importlib.util.spec_from_file_location('checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'original-podium-buried-face-context-v1',refs,dict(uids=[row['uid']],sourceFace=i,exactSharedEdgeNeighbours=len(adj),fullAcceptance=False,qualification='Focused original facet context; raw foundation failure retained; current complete terrain/neighbour review remains required.'));print(dict(face=i,normal=cross[i].tolist(),neighbours=len(adj)),flush=True)
if __name__=='__main__':main()
