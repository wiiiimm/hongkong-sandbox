"""Plot every compound-negative Twin source facet against the unchanged podium.
Diagnostic only: no source role, physical or publication approval.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_assembly_context_plot_v3_20261023 import clipped_faces
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-twin-after-aqua-';BATCH=P+'complete-low-joint-views-v1-20261101';UID='landsd/223207:0';PARENT='landsd/223206:0'
def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 selection=take(P+'current-original-checks-v1-20261101-runtime','selection.json.gz');source=next(r for r in selection['rows']if r['uid']==UID)
 compound=take(P+'complete-compound-context-v1-20261101','summary.json');ids=next(r for r in compound['rows']if r['mode']=='original')['exactAffectedFaces'];assert len(ids)==len(set(ids))==12
 native=next(r for r in take(P+'installed-native-contacts-v1-20261101','native-input.json.gz')['rows']if r['uid']==PARENT)
 src=ROOT/source['candidate']['path'];peer=ROOT/native['path'];assert digest(src.read_bytes())==source['sourceSHA256']==compound['sourceSHA256'];assert digest(peer.read_bytes())==native['entry']['sha256']==compound['supportSHA256'];refs.extend([src,peer])
 tri=decode_original_world_triangles(src.read_bytes());podium=decode_original_world_triangles(peer.read_bytes());out.mkdir();records=[];images=[]
 for subset in [ids,*[[i]for i in ids]]:
  points=tri[subset].reshape(-1,3);lo=points.min(0)-[1,1,1];hi=points.max(0)+[1,2,1];planes=[(axis,float(lo[axis]),True)for axis in range(3)]+[(axis,float(hi[axis]),False)for axis in range(3)]
  fig=plt.figure(figsize=(16,7),layout='constrained')
  for k,angle in enumerate([35,215]):
   ax=fig.add_subplot(1,2,k+1,projection='3d')
   for mesh,col,alpha in [(podium,'#169a9a',.25),(tri,'#64748b',.10),(tri[subset],'#d04729',1)]:
    ix=np.all(mesh.max(1)>=lo,axis=1)&np.all(mesh.min(1)<=hi,axis=1);polys=clipped_faces(mesh[ix],planes)
    if len(polys):ax.add_collection3d(Poly3DCollection((polys-lo)[:,:,[0,2,1]],facecolors=col,edgecolors=col,alpha=alpha,linewidth=.25))
   for i in subset:
    c=tri[i].mean(0)-lo;ax.text(c[0],c[2],c[1],str(i),fontsize=8)
   size=(hi-lo)[[0,2,1]];ax.set_xlim(0,size[0]);ax.set_ylim(0,size[1]);ax.set_zlim(0,size[2]);ax.set_box_aspect(size);ax.view_init(elev=25,azim=angle);ax.set_xlabel('local east m');ax.set_ylabel('local viewer z m');ax.set_zlabel('local height m')
  fig.suptitle('Exact original source facets red; unchanged installed podium teal. Display crop only.')
  path=out/('all-negative-faces.png'if len(subset)>1 else 'source-face-'+str(subset[0])+'.png');fig.savefig(path,dpi=140);plt.close(fig);refs.append(path);images.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),sourceFaces=subset))
 for i in ids:
  face=tri[i];n=np.cross(face[1]-face[0],face[2]-face[0]);size=float(np.linalg.norm(n));records.append(dict(sourceFace=i,vertices=face.tolist(),areaM2=size/2,signedNormalYRatio=float(n[1]/size),minimumHKPD=float(face[:,1].min()),maximumHKPD=float(face[:,1].max())))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 result=dict(uids=[UID,PARENT],sourceSHA256=source['sourceSHA256'],supportSHA256=native['entry']['sha256'],completeNegativeSourceFaces=ids,rows=records,images=images,currentManifestSHA256=selection['manifestSHA256'],sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification=__doc__)
 save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'original_assembly_context_plot_v3_20261023.py']);module('twin_all_low_joint_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-twin-complete-compound-negative-source-face-views',refs,result)
if __name__=='__main__':main()
