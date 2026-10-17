"""Account for every original face nominated by the existing 10m identity extent test."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-long-ping-current-physical-v1-20261017';BATCH='government-xl-long-ping-extent-account-v1-20261017';DOC=BASE/BATCH;RT=HERE/'local'/PRIOR.name/'runtime-geometry.json.gz'
def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for path,sha in {(x['path'],x['sha256']) for x in receipt['evidenceRefs']}:assert digest((ROOT/path).read_bytes())==sha,path
 g=read(RT)['rows'][0];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];row=read(PRIOR/'selection.json.gz')['rows'][0];b=row['source']['building'];target=Polygon(b['rings'][0]);dist=shapely.distance(shapely.points(t[:,:,[0,2]].reshape(-1,2)),target).reshape(-1,3);far=dist.max(axis=1)>10
 final=module('long_ping_extent_components',HERE/'xl-final-script-pass.py');components=final.connected_components(t,far);account=[]
 for ids in components:
  faces=t[ids];points=faces[dist[ids]>10];account.append(dict(faceIndices=[int(i)for i in ids],faceCount=len(ids),wholeFaceBounds=[faces.min(axis=(0,1)).tolist(),faces.max(axis=(0,1)).tolist()],outsideVertexBounds=[points.min(axis=0).tolist(),points.max(axis=0).tolist()],maximumDistanceM=float(dist[ids].max())))
 assert sum(x['faceCount']for x in account)==int(far.sum())==408 and sorted(i for x in account for i in x['faceIndices'])==np.flatnonzero(far).tolist()
 summary=dict(uid=g['uid'],sourceSHA256=g['sourceSHA256'],allSourceFaces=len(t),nominatedFaces=int(far.sum()),remainingFaces=int((~far).sum()),maximumRemainingVertexDistanceM=float(dist[~far].max()),components=account,identityAccepted=False,installationApproved=False,qualification='Diagnostic face nomination uses the unchanged existing 10m threshold. No buffer changes, face omission, inferred source ownership or acceptance override.')
 save(DOC/'account.json',summary)
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.collections import PolyCollection
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 fig=plt.figure(figsize=(15,9),dpi=160);ax=fig.add_subplot(211)
 for mask,color in [(~far,'#98a6b5'),(far,'#d65050')]:
  coords=t[mask][:,:,[0,2]].copy();coords[:,:,0]+=834500;coords[:,:,1]=816500-coords[:,:,1];ax.add_collection(PolyCollection(coords,facecolors=color,edgecolors=color,linewidths=.15,alpha=.6))
 xy=np.asarray(target.exterior.coords);ax.plot(xy[:,0]+834500,816500-xy[:,1],color='#15874d');ax.autoscale_view();ax.set_aspect('equal');ax.ticklabel_format(style='plain',useOffset=False);ax.set_title('All original faces; every face beyond existing extent threshold red');ax.set_xlabel('HK1980 east (m)');ax.set_ylabel('HK1980 north (m)')
 origin=t.min(axis=(0,1));west=t[:,:,0].min(axis=1)<-13990
 for n,azim in [(223,-55),(224,125)]:
  ax=fig.add_subplot(n,projection='3d')
  for mask,color in [(west&~far,'#98a6b5'),(west&far,'#d65050')]:
   v=(t[mask]-origin)[:,:,[0,2,1]];ax.add_collection3d(Poly3DCollection(v,facecolors=color,edgecolors='none',alpha=.7))
  ax.set(xlim=(-2,35),ylim=(20,60),zlim=(0,32),xlabel='East offset (m)',ylabel='South offset (m)',zlabel='Height offset (m)',title='Western end - unchanged original faces');ax.view_init(elev=25,azim=azim);ax.set_box_aspect((37,40,32))
 fig.tight_layout();fig.savefig(DOC/'complete-extent-account.png');plt.close(fig)
 refs=[Path(__file__),PRIOR/'result.json',PRIOR/'selection.json.gz',RT,HERE/'xl-final-script-pass.py'];result=module('long_ping_extent_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'long-ping-complete-original-extent-face-account-v1',refs,dict(uids=[g['uid']],summary=summary,fullAcceptance=False,nextStep='Review every nominated component against original station geometry and primary plans; no identity clearance is inferred from this diagnostic.'))
 print(dict(jobId=result['jobId'],faces=int(far.sum()),components=[{k:v for k,v in x.items()if k!='faceIndices'}for x in account]),flush=True)
if __name__=='__main__':main()
