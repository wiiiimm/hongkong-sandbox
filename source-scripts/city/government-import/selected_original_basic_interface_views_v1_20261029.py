"""Plot an exact original/BASIC interface, retaining complete source arrays."""
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_assembly_context_plot_v3_20261023 import clipped_faces

def main():
 ap=argparse.ArgumentParser()
 for k in ['batch','runtime','foreign','uid','basic']:ap.add_argument('--'+k,required=True)
 a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists();pins={};refs=[Path(__file__)]
 def take(batch,path):
  if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
  assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid);source=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
 b=next(r for r in take(a.foreign,base/a.foreign/'basic.json')['rows']if r['uid']==a.basic);basic=np.asarray(b['position']).reshape(-1,3)[np.asarray(b['index']).reshape(-1,3)]
 lo,hi=basic.min((0,1)),basic.max((0,1));center=(lo+hi)/2;native_near=source[np.all(source[:,:,[0,2]].max(1)>=lo[[0,2]]-3,axis=1)&np.all(source[:,:,[0,2]].min(1)<=hi[[0,2]]+3,axis=1)]
 assert len(native_near);out.mkdir();images=[]
 for label,upper in [('full-height',float(max(hi[1],source[:,:,1].max())+1)),('original-height',float(source[:,:,1].max()+1))]:
  low=lo-[3,2,3];high=hi+[3,1,3];high[1]=upper;planes=[(i,float(v),side)for i in range(3)for v,side in [(low[i],True),(high[i],False)]]
  def shown(t):
   selected=t[np.all(t.max(1)>=low,axis=1)&np.all(t.min(1)<=high,axis=1)];v=clipped_faces(selected,planes);v[:,:,[0,2]]-=center[[0,2]];return v[:,:,[0,2,1]]
  fig=plt.figure(figsize=(14,7),layout='constrained')
  for i,angle in enumerate([35,215]):
   ax=fig.add_subplot(1,2,i+1,projection='3d')
   for triangles,color,alpha,edge in [(ground,'#a99b85',.35,'none'),(source,'#35966e',.9,'none'),(basic,'#c96d53',.12,'#a34331')]:
    ax.add_collection3d(Poly3DCollection(shown(triangles),facecolor=color,alpha=alpha,edgecolor=edge,linewidth=.5))
   ax.set(xlim=(low[0]-center[0],high[0]-center[0]),ylim=(low[2]-center[2],high[2]-center[2]),zlim=(low[1],high[1]),xlabel='Local east (m)',ylabel='Local viewer Z (m)',zlabel='HKPD height (m)');ax.set_box_aspect((high-low)[[0,2,1]]);ax.view_init(elev=25,azim=angle)
  fig.suptitle(a.uid+' green original; '+a.basic+' red BASIC; current ground grey. Display crop only: '+label)
  image=out/(label+'.png');fig.savefig(image,dpi=150);plt.close(fig);refs.append(image);images.append(dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes())))
 result=dict(uids=[a.uid],sourceSHA256=g['sourceSHA256'],sourceWorldSHA256=digest(source.astype('<f8').tobytes()),basicUid=a.basic,basicWorldSHA256=digest(basic.astype('<f8').tobytes()),basicBounds=[lo.tolist(),hi.tolist()],nativeFacesNearBasic=len(native_near),images=images,sourceGeometryChanges=0,identityAccepted=False,counterpartSuppressionApproved=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Exact captured original, actual complete BASIC geometry and drawn ground. Display crops only, separate full-BASIC-height and native-height scales. Neither projected overlap nor finite contacts alone authorize suppression or support. ROOT must inspect images.')
 save(out/'summary.json',result);refs.append(HERE/'original_assembly_context_plot_v3_20261023.py');module('original_basic_interface_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-original-and-retained-basic-interface-views-without-approval',refs,result)
 print(dict(batch=a.batch,images=2,sourceGeometryChanges=0),flush=True)

if __name__=='__main__':main()
