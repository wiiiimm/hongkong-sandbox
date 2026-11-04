"""Render source-bound neighbour interfaces for review; grants no acceptance."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-namcheong244683-interface-views-v1-20261017';DOC=BASE/BATCH
CAP=BASE/'government-xl-namcheong244683-current-capture-v1-20261017';AFTER=BASE/'government-xl-namcheong244683-neighbour-contacts-v1-20261017'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 for d in [CAP,AFTER,BASE/'government-xl-namcheong244683-baseline-contacts-v1-20261017']:
  r=read(d/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(d/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rt=HERE/'local'/CAP.name/'runtime-geometry.json.gz';g=read(rt)['rows'][0];tri=lambda g:np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];own=tri(g)
 foreignpath=BASE/'government-xl-namcheong244683-neighbour-geometry-v1-20261017/geometry.json.gz';foreign=read(foreignpath)['rows'];DOC.mkdir();summary=[]
 for uid in ['landsd/108916:0','landsd/233291:0']:
  other=tri(next(f for f in foreign if f['uid']==uid));cs=read(AFTER/(uid.replace('/','-').replace(':','-')+'.json.gz'))['contacts']['contacts'];ids=sorted({c['sourceFaceA']for c in cs});affected=own[ids];lo=affected.min(axis=(0,1));hi=affected.max(axis=(0,1));origin=(lo+hi)/2;span=np.maximum(hi-lo,4);pad=np.maximum(span*.3,4);bounds=np.array([lo-pad,hi+pad]);fig=plt.figure(figsize=(15,6),dpi=140)
  for j,az in enumerate([-45,135],1):
   ax=fig.add_subplot(1,2,j,projection='3d')
   for mesh,color,alpha in [(own,'#7399ad',.1),(other,'#e2ba51',.2),(affected,'#c52e35',.9)]:ax.add_collection3d(Poly3DCollection((mesh-origin)[:,:,[0,2,1]],facecolors=color,edgecolors=color,linewidths=.2,alpha=alpha))
   b=bounds-origin;ax.set(xlim=b[:,0],ylim=b[:,2],zlim=b[:,1],xlabel='East offset m',ylabel='South offset m',zlabel='Height offset m',title=uid+' | red: original contact faces');ax.set_box_aspect((bounds[1]-bounds[0])[[0,2,1]]);ax.view_init(22,az)
  fig.tight_layout();fig.savefig(DOC/(uid.replace('/','-').replace(':','-')+'.png'));plt.close(fig);summary.append(dict(uid=uid,sourceFaceIds=ids,contactCount=len(cs),contactFaceBounds=[lo.tolist(),hi.tolist()]))
 save(DOC/'interfaces.json',dict(rows=summary,fullAcceptance=False,qualification='Exact source/contact IDs; contextual cropped views, not containment or identity proof.'))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 out=module('nam_interface_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'namcheong-two-changed-interface-visual-context-v1',refs+[rt,foreignpath,*[ROOT/p for p in pins]],dict(uids=[g['uid']],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
