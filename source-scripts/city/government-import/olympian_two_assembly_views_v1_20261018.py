"""Inspect unchanged original tower/podium interfaces and retained failed samples."""
from pathlib import Path
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-olympian-two-original-tower-contacts-v1-20261018';RESTORE=BASE/'government-xl-olympian-two-restored-components-v2-20261018';CAP=BASE/'government-xl-olympian-two-source-local-terrain-20261008';BATCH='government-xl-olympian-two-assembly-views-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=read(CAP/'selection.json.gz')['rows'][0];podium=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());DOC.mkdir();summary=[]
 for row in read(RESTORE/'restored.json')['rows']:
  uid=row['uid'];t=decode_original_world_triangles((ROOT/row['assetPath']).read_bytes());lo=t.min((0,1));hi=t.max((0,1));top=lo[1]+6;low=t[t[:,:,1].min(1)<=top];local=podium[(podium[:,:,0].max(1)>=lo[0]-2)&(podium[:,:,0].min(1)<=hi[0]+2)&(podium[:,:,2].max(1)>=lo[2]-2)&(podium[:,:,2].min(1)<=hi[2]+2)];samples=read(PRIOR/(uid.split('/')[1]+'-samples.json.gz'))['points'];points=np.asarray([x['point']for x in samples]);colors=['#d82d2d'if x['gap']is None or x['gap']>.1 else '#8e39bc'if x['gap']<-.1 else '#19783e'for x in samples]
  fig=plt.figure(figsize=(17,7));ax=fig.add_subplot(1,2,1);origin=lo[[0,2]]
  for tris,color,alpha in [(local,'#cfb26b',.25),(low,'#3783bb',.22)]:ax.add_collection(PolyCollection(tris[:,:,[0,2]]-origin,facecolors=color,edgecolors=color,linewidths=.2,alpha=alpha))
  ax.scatter(*(points[:,[0,2]]-origin).T,c=colors,s=9);ax.set(xlim=(-2,hi[0]-lo[0]+2),ylim=(-2,hi[2]-lo[2]+2),xlabel='X metres from source min',ylabel='Z metres from source min',title='Plan: failed samples red; penetration purple; contact green');ax.set_aspect('equal');ax.grid(alpha=.2)
  ax=fig.add_subplot(1,2,2,projection='3d');centre=lo.copy();centre[1]=23.2
  for tris,color,alpha in [(local,'#cfb26b',.3),(low,'#3783bb',.35)]:ax.add_collection3d(Poly3DCollection((tris-centre)[:,:,[0,2,1]],facecolors=color,edgecolors=color,linewidths=.25,alpha=alpha))
  q=points-centre;ax.scatter(q[:,0],q[:,2],q[:,1],c=colors,s=8);ax.set(xlim=(-2,hi[0]-lo[0]+2),ylim=(-2,hi[2]-lo[2]+2),zlim=(-3,top-23.2),xlabel='X metres',ylabel='Z metres',zlabel='Height above23.2m');ax.set_box_aspect([hi[0]-lo[0],hi[2]-lo[2],top-20.2]);ax.view_init(elev=30,azim=-60)
  fig.suptitle(uid+' original lower tower blue / original podium tan\nLocal geometric context only; top cropped. No acceptance, moved geometry or inferred support.');fig.tight_layout();name=uid.replace('/','-').replace(':','-')+'.png';fig.savefig(DOC/name,dpi=150);plt.close(fig);summary.append(dict(uid=uid,image=name,originalSHA256=row['sourceSHA256'],localPodiumFaces=len(local),lowerTowerFaces=len(low),samples=len(samples)))
 save(DOC/'summary.json',dict(rows=summary,fullAcceptance=False));out=module('olympian_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-four-original-tower-podium-interface-views-v1',[Path(__file__),PRIOR/'result.json',*[ROOT/p for p in pins],HERE/'exact_packed_world_geometry_20261009.py'],dict(uids=[x['uid']for x in summary],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
