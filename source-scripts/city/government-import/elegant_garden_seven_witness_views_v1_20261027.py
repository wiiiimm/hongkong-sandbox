"""Display exact original wall/podium context and saved attachment paths only."""
import argparse
from fractions import Fraction
from pathlib import Path
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_assembly_context_plot_v3_20261023 import clipped_faces
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-elegant-garden-seven-witness-views-v1-20261027'
OLD='government-xl-elegant-garden-block2-four-world-support-v1-20261027';CONTACT='government-xl-elegant-garden-seven-witness-contacts-v1-20261027';PATHS='government-xl-elegant-garden-seven-witness-paths-v1-20261027'
def main():
 p=argparse.ArgumentParser();p.add_argument('--lease',required=True);a=p.parse_args();lease=read(Path(a.lease));assert reservations.owns(lease)and {'building:landsd/173532:0','building:landsd/236170:0'}<=set(lease['resources'])
 out=BASE/BATCH;assert not out.exists();pins={};refs=[Path(__file__)]
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 source=take(OLD,'summary.json');metrics=[];worlds={}
 for mode in ['original','literal','leftF32','balancedF32']:
  data=take(OLD,mode+'/input.json.gz');g=data['rows'][0];tri=np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];podium=np.asarray(data['podium'],dtype='<f8');contact=take(CONTACT,mode+'.json.gz');paths=take(PATHS,mode+'.json.gz')
  ids=contact['incidentSourceFaces'];assert ids==[10385,10388,10389,10506]and len(paths['rows'])==7
  f=tri[ids];n=np.cross(f[:,1]-f[:,0],f[:,2]-f[:,0]);n=n/np.linalg.norm(n,axis=1)[:,None]
  metrics.append(dict(mode=mode,sourceFaces=ids,unitNormals=n.tolist(),minimumY=float(f[:,:,1].min()),maximumY=float(f[:,:,1].max()),sourceWorldSHA256=digest(tri.tobytes()),pathsWithinExistingEndpointHeight=paths['pathsWithinExistingEndpointHeight']))
  worlds[mode]=(tri,podium,contact,paths)
 tri,podium,contact,paths=worlds['original'];focus=tri[contact['incidentSourceFaces']];lo=focus.min(axis=(0,1))-[2,1,2];hi=focus.max(axis=(0,1))+[2,3,2];planes=[(i,float(lo[i]),True)for i in range(3)]+[(i,float(hi[i]),False)for i in range(3)];size=(hi-lo)[[0,2,1]]
 fig=plt.figure(figsize=(18,7),layout='constrained')
 for i,angle in enumerate([35,125,215]):
  ax=fig.add_subplot(1,3,i+1,projection='3d')
  for mesh,color,alpha in [(tri,'#aab2bc',.12),(podium,'#267ac0',.32),(focus,'#ce3c21',.8)]:
   near=np.all(mesh.max(1)>=lo,axis=1)&np.all(mesh.min(1)<=hi,axis=1);poly=clipped_faces(mesh[near],planes)
   if len(poly):ax.add_collection3d(Poly3DCollection((poly-lo)[:,:,[0,2,1]],facecolors=color,edgecolors=color,alpha=alpha,linewidth=.3))
  for row in paths['rows']:
   points=np.asarray(row['continuousPath'])-lo;ax.plot(points[:,0],points[:,2],points[:,1],color='black',linewidth=1.2);ax.scatter(points[0,0],points[0,2],points[0,1],color='#e9a414',s=12)
  ax.set(xlim=(0,size[0]),ylim=(0,size[1]),zlim=(0,size[2]),xlabel='X offset m',ylabel='Z offset m',zlabel='Y offset m');ax.set_box_aspect(size);ax.view_init(24,angle)
 fig.suptitle('Elegant Garden Block2 original lower-wall/podium interface\nRed: four original incident wall facets; blue: original podium; grey: other Block2 facets; black: exact saved paths; orange: failed rim witnesses. Display crop only.',fontsize=10)
 image=out/'original-wall-podium-paths.png';image.parent.mkdir();fig.savefig(image,dpi=140);plt.close(fig);refs.append(image)
 result=dict(uids=source['uids'],sourceSHA256ByUid=source['sourceSHA256ByUid'],rows=metrics,image=dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes())),sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,qualification='Three-angle display crop of unchanged source facets and exact saved paths. No ground/solid-clearance/source-role approval or changed support threshold.')
 save(out/'summary.json',result);assert reservations.owns(lease);refs.append(HERE/'original_assembly_context_plot_v3_20261023.py')
 module('elegant_wall_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-four-original-wall-facet-podium-path-display',refs,result)
if __name__=='__main__':main()
