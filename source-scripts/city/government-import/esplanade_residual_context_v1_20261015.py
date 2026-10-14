"""Locate residuals on unchanged Esplanade sources; no acceptance or edits."""
import importlib.util
import numpy as np
import shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PREV=BASE/'government-xl-esplanade-original-support-ground-v1-20261015';PHYSICAL=BASE/'government-xl-esplanade-pair-current-physical-v3-20261015';DOC=BASE/'government-xl-esplanade-residual-context-v1-20261015'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();DOC.mkdir();prior=read(PREV/'result.json')
 for r in prior['evidenceRefs']:assert ref(ROOT/r['path'])==r
 rows=read(PHYSICAL/'selection.json.gz')['rows'];tri={r['uid']:decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes())for r in rows};tower=tri['landsd/268828:0'];podium=tri['landsd/309385:0'];support=read(PREV/'support-checks.json.gz')['rows'][0];failed=read(PREV/'podium-ground.json.gz');ids=failed['summary']['belowHalfMetreFaces'];groundFile=next(ROOT/r['path']for r in read(PHYSICAL/'terrain.json')['sourceFiles']if r['path'].endswith('.gltf'))
 spec=importlib.util.spec_from_file_location('esplanade_context_final',HERE/'xl-final-script-pass.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);ground=f.s.terrain_triangles(groundFile);polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>1e-10
 points=np.asarray([failed['faces'][i]['minimum']['position']for i in ids]);heights=f.s.context.shared.samples(points[:,[0,2]],ground[valid],shapely.STRtree(polys[valid]));native=[dict(face=i,position=p.tolist(),originalTerrainHeight=float(h),originalTerrainGap=float(p[1]-h))for i,p,h in zip(ids,points,heights)]
 fig=plt.figure(figsize=(15,7));origin=podium.min(axis=(0,1));origin[1]=0
 ax=fig.add_subplot(121,projection='3d');low=tower[:,:,1].min(axis=1)<31
 for a,c,alpha in [(podium,'#d1b892',.4),(tower[low],'#9fbacb',.3)]:ax.add_collection3d(Poly3DCollection((a-origin)[:,:,[0,2,1]],facecolors=c,edgecolors='#555',linewidths=.1,alpha=alpha))
 pts=np.asarray([r['position']for r in support['unresolved']])-origin;ax.scatter(pts[:,0],pts[:,2],pts[:,1],color='red',s=14,depthshade=False);hi=podium.max(axis=(0,1))-origin;ax.set_xlim(0,hi[0]);ax.set_ylim(0,hi[2]);ax.set_zlim(15,35);ax.set_box_aspect([hi[0],hi[2],30]);ax.view_init(35,-60);ax.set_title('Tower rim failures red; unchanged podium tan\nDisplay cropped vertically at 35 m')
 ax=fig.add_subplot(122,projection='3d');a=podium[ids];lo,hi=a.min(axis=(0,1)),a.max(axis=(0,1));o=np.array([lo[0],0,lo[2]]);mask=(podium[:,:,0].max(axis=1)>=lo[0]-2)&(podium[:,:,0].min(axis=1)<=hi[0]+2)&(podium[:,:,2].max(axis=1)>=lo[2]-2)&(podium[:,:,2].min(axis=1)<=hi[2]+2);g=(ground[:,:,0].max(axis=1)>=lo[0]-2)&(ground[:,:,0].min(axis=1)<=hi[0]+2)&(ground[:,:,2].max(axis=1)>=lo[2]-2)&(ground[:,:,2].min(axis=1)<=hi[2]+2)
 for t,c,alpha in [(ground[g],'#a4bb8b',.4),(podium[mask],'#b7cad9',.4),(a,'#de3333',.9)]:ax.add_collection3d(Poly3DCollection((t-o)[:,:,[0,2,1]],facecolors=c,edgecolors='#555',linewidths=.3,alpha=alpha))
 ax.set_xlim(-2,hi[0]-lo[0]+2);ax.set_ylim(-2,hi[2]-lo[2]+2);ax.set_zlim(2,13);ax.set_box_aspect([hi[0]-lo[0]+4,hi[2]-lo[2]+4,11]);ax.view_init(25,120);ax.set_title('Four podium crossing faces red\nAuthentic source terrain green');fig.tight_layout();fig.savefig(DOC/'residuals.png',dpi=140);plt.close(fig)
 save(DOC/'context.json',dict(originalTerrainWitnesses=native,inputRefs=[ref(__import__('pathlib').Path(__file__)),ref(PREV/'result.json'),ref(groundFile),ref(DOC/'residuals.png')],installationApproved=False,geometryChanges=0));print(native)
if __name__=='__main__':main()
