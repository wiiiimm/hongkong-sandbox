"""Export complete original identity/base-interface views; no model edits or approval."""
import argparse,sys,uuid
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from original_assembly_context_plot_v3_20261023 import clipped_faces
BASE=ROOT/'docs/astra-city/government-import'
CURRENT='government-xl-elegant-garden-final-sixteen-composed-support-v1-20261028'
RUNTIME='government-xl-elegant-garden-sixteen-original-updated-runtime-v1-20261028'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--uid',required=True,action='append');p.add_argument('--owned',action='store_true');a=p.parse_args()
 assert a.batch.startswith('government-xl-')and '/'not in a.batch
 out=BASE/a.batch;local=HERE/'local'/a.batch;lp=local/'reservation.json';assert not out.exists()
 resourcepath=BASE/'government-xl-elegant-garden-sixteen-original-updated-terrain-plan-v1-20261028.json';resources=set(read(resourcepath)['resources'])
 assert {'building:'+u for u in a.uid}<=resources and len(set(a.uid))==len(a.uid)
 if not a.owned:
  assert not local.exists();claim=reservations.claim('current-original-identity-views-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),resourcepath];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 summary=take(CURRENT,'summary.json');inputs=take(CURRENT,'input.json.gz');sources={r['uid']:r for r in take(RUNTIME,'selection.json.gz')['rows']}
 def tri(g):return np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 out.mkdir();exports=[]
 for uid in a.uid:
  assert reservations.owns(lease);data=next(r for r in inputs['rows']if r['uid']==uid and r['mode']=='original');source=tri(data['source']);support=tri(data['support']);b=sources[uid]['source']['building']
  assert digest(source.tobytes())==data['sourceWorldSHA256']and digest(support.tobytes())==data['supportWorldSHA256']
  fig=plt.figure(figsize=(18,8),layout='constrained');ax=fig.add_subplot(1,3,1)
  ax.add_collection(PolyCollection(source[:,:,[0,2]],facecolors='#f2a65a',edgecolors='#bd6f20',alpha=.4,linewidth=.15))
  for ring in b['rings']:
   xy=np.asarray(ring);ax.plot(xy[:,0],xy[:,1],color='#111827',linewidth=1.4,label='Recorded footprint')
  ax.autoscale();ax.set_aspect('equal');ax.set_title('Complete original projection / recorded footprint');ax.set(xlabel='World X m',ylabel='World Z m');ax.grid(alpha=.2)
  whole=fig.add_subplot(1,3,2,projection='3d');lo=source.min((0,1));hi=source.max((0,1));size=np.maximum((hi-lo)[[0,2,1]],.1)
  whole.add_collection3d(Poly3DCollection((source-lo)[:,:,[0,2,1]],facecolors='#b5c1ce',edgecolors='#52637a',linewidth=.12,alpha=.95))
  whole.set(xlim=(0,size[0]),ylim=(0,size[1]),zlim=(0,size[2]),xlabel='X offset m',ylabel='Z offset m',zlabel='Y offset m');whole.set_box_aspect(size.copy());whole.view_init(22,40);whole.set_title('Complete immutable government source')
  low=lo-[3,1,3];high=np.array([hi[0]+3,lo[1]+4,hi[2]+3]);planes=[(i,float(low[i]),True)for i in range(3)]+[(i,float(high[i]),False)for i in range(3)];baseax=fig.add_subplot(1,3,3,projection='3d')
  def draw(mesh,color,alpha):
   ix=np.all(mesh.max(1)>=low,axis=1)&np.all(mesh.min(1)<=high,axis=1);clipped=clipped_faces(mesh[ix],planes)
   if len(clipped):baseax.add_collection3d(Poly3DCollection((clipped-low)[:,:,[0,2,1]],facecolors=color,edgecolors=color,alpha=alpha,linewidth=.2))
  for part in summary['supportRosters'][uid]:
   chunk=support[slice(*part['sourceFaceRange'])]
   draw(chunk,'#218a53'if part.get('kind')=='actual-drawn-terrain'else'#3975b8',.35)
  draw(source,'#de6b24',.9);limits=np.maximum((high-low)[[0,2,1]],.1)
  baseax.set(xlim=(0,limits[0]),ylim=(0,limits[1]),zlim=(0,limits[2]),xlabel='X offset m',ylabel='Z offset m',zlabel='Y offset m');baseax.set_box_aspect(limits.copy());baseax.view_init(23,225);baseax.set_title('Base close-up: source orange / supports blue / terrain green')
  fig.suptitle(f"{uid} · {b.get('name')or'unnamed'} · {b['buildingCSUID']}\nOriginal faces: {len(source)}; fixed 1× placement. Display clipping only; no identity or physical approval.",fontsize=12)
  path=out/(uid.split('/')[1].replace(':','-')+'.png');fig.savefig(path,dpi=140);plt.close(fig)
  exports.append(dict(uid=uid,path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),dimensions=[2520,1120],sourceWorldSHA256=data['sourceWorldSHA256']));refs.append(path)
 result=dict(uids=a.uid,exports=exports,sourceGeometryChanges=0,sourcePoseChanges=0,architectureReviewed=False,identityAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Complete source projection and complete original mesh, with a display-only base crop of every current support/terrain contributor. Current recorded footprint is context, not an approved geometry template. Exported images require actual inspection; no architectural inference, source coverage exception or collision approval is granted.')
 save(out/'summary.json',result);refs.append(HERE/'original_assembly_context_plot_v3_20261023.py');assert reservations.owns(lease)
 module('current_identity_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'current-complete-original-identity-and-base-interface-exports',refs,result)
 print(dict(exports=len(exports)),flush=True)
if __name__=='__main__':main()
