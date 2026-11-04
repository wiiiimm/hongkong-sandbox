"""Display every nonempty original/source native junction; never source acceptance."""
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection,Line3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_assembly_context_plot_v3_20261023 import clipped_faces
from primrose_compound_foundation_v2_20261015 import module

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','runtime','contacts','roles']:p.add_argument('--'+k,required=True)
 a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
 assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists()
 refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py',HERE/'original_assembly_context_plot_v3_20261023.py'];pins={}
 def take(name,path):
  if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
  assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection={r['uid']:r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']}
 runtime={r['uid']:r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']}
 native={r['uid']:r for r in take(a.contacts,base/a.contacts/'native-input.json.gz')['rows']}
 roles=take(a.roles,base/a.roles/'summary.json');exports=[];out.mkdir()
 for row in roles['rows']:
  if row['mode']!='original' or not row['contactCount']:continue
  uid,nuid=row['uid'],row['nativeUid'];source=selection[uid];other=native[nuid]
  assert source['sourceSHA256']==row['sourceSHA256']and other['entry']['sha256']==row['nativeSHA256']
  triangles=[]
  for path,sha in [(ROOT/source['candidate']['path'],source['sourceSHA256']),(ROOT/other['path'],other['entry']['sha256'])]:
   assert digest(path.read_bytes())==sha;refs.append(path);triangles.append(decode_original_world_triangles(path.read_bytes()))
  for tri,key in zip(triangles,['sourceWorldSHA256','nativeWorldSHA256']):assert digest(tri.astype('<f8').tobytes())==row[key]
  bounds=np.asarray(row['contactBounds']);lo=bounds[0]-[2,1,2];hi=bounds[1]+[2,3,2];size=np.maximum((hi-lo)[[0,2,1]],.1)
  planes=[(axis,float(lo[axis]),True)for axis in range(3)]+[(axis,float(hi[axis]),False)for axis in range(3)]
  fig=plt.figure(figsize=(15,7),layout='constrained')
  ground=np.asarray(runtime[uid]['drawnGroundGeometry'],float).reshape(-1,3,3)
  for k,angle in enumerate([35,215]):
   ax=fig.add_subplot(1,2,k+1,projection='3d')
   for tri,color in zip(triangles,['#d04729','#2368b6']):
    keep=np.all(tri.max(1)>=lo,axis=1)&np.all(tri.min(1)<=hi,axis=1);polys=clipped_faces(tri[keep],planes)
    if len(polys):ax.add_collection3d(Poly3DCollection((polys-lo)[:,:,[0,2,1]],facecolors=color,edgecolors=color,alpha=.3,linewidth=.3))
   keep=np.all(ground.max(1)>=lo,axis=1)&np.all(ground.min(1)<=hi,axis=1);polys=clipped_faces(ground[keep],planes)
   if len(polys):ax.add_collection3d(Line3DCollection([np.vstack([v,v[:1]])for v in(polys-lo)[:,:,[0,2,1]]],colors='#16834a',linewidth=.5))
   ax.set(xlim=(0,size[0]),ylim=(0,size[1]),zlim=(0,size[2]),xlabel='X offset m',ylabel='Z offset m',zlabel='HKPD offset m');ax.set_box_aspect(size.copy());ax.view_init(24,angle)
  fig.suptitle(f'{uid} / {nuid}: exact original contact context\nRed source; blue unchanged installed neighbour; green drawn terrain. Display crop only.',fontsize=11)
  path=out/(uid.split('/')[1].replace(':','-')+'--'+nuid.split('/')[1].replace(':','-')+'.png');fig.savefig(path,dpi=140);plt.close(fig);refs.append(path)
  exports.append(dict(uid=uid,nativeUid=nuid,image=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())),originalContactCount=row['contactCount'],originalRoles=row['roles'],bounds=row['contactBounds']))
 assert len(exports)==sum(r['mode']=='original'and bool(r['contactCount'])for r in roles['rows'])
 for bound in pins.values():
  for name,sha in bound.items():assert digest((ROOT/name).read_bytes())==sha
 result=dict(uids=list(selection),exports=exports,allNonemptyOriginalNativePairsDisplayed=True,sourceGeometryChanges=0,nativeMetadataChanges=0,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,qualification='Complete original source and unchanged installed-neighbour triangles are clipped only for diagnostic display around the entire saved contact bounds. All nonempty original pair interfaces included. No hidden triangles in runtime assets, pose edits, architectural interpretation, collision exemption or browser acceptance.')
 save(out/'summary.json',result);module('native_junction_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-original-native-junction-visual-context',list(dict.fromkeys(refs)),result)
 print(dict(exports=len(exports),installationApproved=False),flush=True)
if __name__=='__main__':main()
