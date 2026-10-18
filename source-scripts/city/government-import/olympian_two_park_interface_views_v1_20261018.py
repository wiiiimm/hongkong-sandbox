"""Original lower-assembly views for source-specific contact interpretation."""
from pathlib import Path
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-olympian-two-park-four-world-contacts-v1-20261018';BATCH='government-xl-olympian-two-park-interface-views-v1-20261018';DOC=BASE/BATCH
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 inputs=read(PRIOR/'inputs.json.gz');world=inputs['worlds']['original'];podium=np.concatenate([np.asarray(world[u])for u in inputs['supportUIDs']]);reports={r['uid']:r for r in read(PRIOR/'contacts.json.gz')['rows']if r['mode']=='original'};DOC.mkdir();summary=[]
 for uid in inputs['targetUIDs']:
  t=np.asarray(world[uid]);lo=t.min((0,1));hi=t.max((0,1));top=lo[1]+7;low=t[t[:,:,1].min(1)<=top];local=podium[(podium[:,:,0].max(1)>=lo[0]-2)&(podium[:,:,0].min(1)<=hi[0]+2)&(podium[:,:,2].max(1)>=lo[2]-2)&(podium[:,:,2].min(1)<=hi[2]+2)];details=reports[uid]['details'];points=np.asarray([d['position']for d in details]);fig=plt.figure(figsize=(16,7));ax=fig.add_subplot(1,2,1);origin=lo[[0,2]]
  for tris,color,alpha in [(local,'#c5a650',.25),(low,'#3783bb',.3)]:ax.add_collection(PolyCollection(tris[:,:,[0,2]]-origin,facecolors=color,edgecolors=color,linewidths=.2,alpha=alpha))
  ax.scatter(*(points[:,[0,2]]-origin).T,c='#ad174b',s=15);ax.set(xlim=(-2,hi[0]-lo[0]+2),ylim=(-2,hi[2]-lo[2]+2),xlabel='X metres',ylabel='Z metres',title='Original plan; retained canonical failure points');ax.set_aspect('equal')
  ax=fig.add_subplot(1,2,2,projection='3d')
  for tris,color,alpha in [(local,'#c5a650',.3),(low,'#3783bb',.35)]:ax.add_collection3d(Poly3DCollection((tris-lo)[:,:,[0,2,1]],facecolors=color,edgecolors=color,linewidths=.2,alpha=alpha))
  q=points-lo;ax.scatter(q[:,0],q[:,2],q[:,1],c='#ad174b',s=15)
  for d in details:
   if d['path']:
    q=np.asarray(d['path']['original']['witness']['continuousLowPath'])-lo;ax.plot(q[:,0],q[:,2],q[:,1],color='#ed2045',linewidth=2)
  ax.set(xlim=(-2,hi[0]-lo[0]+2),ylim=(-2,hi[2]-lo[2]+2),zlim=(-2,7),xlabel='X metres',ylabel='Z metres',zlabel='Height above original minimum');ax.set_box_aspect([hi[0]-lo[0],hi[2]-lo[2],9]);ax.view_init(elev=28,azim=-60)
  fig.suptitle(uid+' original building blue / original podiums tan / same-face paths red\nLower context cropped; no geometry edits or inferred structure.');fig.tight_layout();name=uid.replace('/','-').replace(':','-')+'.png';fig.savefig(DOC/name,dpi=140);plt.close(fig);summary.append(dict(uid=uid,image=name,originalFaces=len(t),shownLowerFaces=len(low),localSupportFaces=len(local)))
 save(DOC/'summary.json',dict(rows=summary,fullAcceptance=False));refs=[Path(__file__),PRIOR/'result.json',*[ROOT/p for p in pins]];out=module('park_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-park-original-interface-views-v1',refs,dict(uids=inputs['targetUIDs'],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
