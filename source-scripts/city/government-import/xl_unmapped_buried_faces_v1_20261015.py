"""Exact face indices and views of current terrain conflicts; no geometry changes."""
from pathlib import Path
import importlib.util
import numpy as np
import shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PREV=BASE/'government-xl-unmapped-whole-context-v1-20261015';OUT=BASE/'government-xl-unmapped-buried-face-context-v1-20261015'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not OUT.exists();OUT.mkdir();prior=read(PREV/'result.json');ground=read(PREV/'ground.json.gz');recovery=read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows']
 for r in prior['evidenceRefs']:assert ref(ROOT/r['path'])==r
 spec=importlib.util.spec_from_file_location('original_final_context',HERE/'xl-final-script-pass.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);rows=[]
 for region in ground['regions']:
  model=region['modelId'];r=next(r for r in recovery if r['modelId']==model);tri=decode_original_world_triangles((ROOT/r['asset']['path']).read_bytes());terrain=np.asarray(region['position']).reshape(-1,3,3);polys=shapely.polygons(terrain[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;points=np.concatenate([tri,tri.mean(axis=1)[:,None,:]],axis=1);heights=f.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),terrain[valid],shapely.STRtree(polys[valid])).reshape(-1,4);gaps=points[:,:,1]-heights;mask=np.isfinite(heights).all(axis=1)&(gaps<-.5).all(axis=1);ids=np.flatnonzero(mask);assert len(ids)==next(r['foundationDiagnostic']['fullyBuriedTriangles']for r in prior['rows']if r['modelId']==model)
  components=f.connected_components(tri,mask);details=[]
  for c in components:
   a=tri[c];details.append({'faceIds':[int(i)for i in c],'bounds':[a.min(axis=(0,1)).tolist(),a.max(axis=(0,1)).tolist()],'gapRange':[float(gaps[c].min()),float(gaps[c].max())]})
  fig=plt.figure(figsize=(15,8));ax=fig.add_subplot(121);ax.add_collection(PolyCollection(tri[:,:,[0,2]],facecolors='#cad5dd',edgecolors='none'));ax.add_collection(PolyCollection(tri[mask][:,:,[0,2]],facecolors='#d62728',edgecolors='#a00',linewidths=.2));ax.autoscale();ax.set_aspect('equal');ax.invert_yaxis();ax.set_title('Whole source: red = all four samples buried')
  ax=fig.add_subplot(122,projection='3d');lo=tri.min(axis=(0,1));hi=tri.max(axis=(0,1));origin=np.array([lo[0],0,lo[2]]);low=tri[:,:,1].min(axis=1)<10;b=(tri[low]-origin)[:,:,[0,2,1]];ax.add_collection3d(Poly3DCollection(b,facecolors='#bbcbd8',edgecolors='#637080',linewidths=.08,alpha=.55));ax.add_collection3d(Poly3DCollection((tri[mask]-origin)[:,:,[0,2,1]],facecolors='#e32b2b',edgecolors='#8b0000',linewidths=.2));ax.set_xlim(0,hi[0]-lo[0]);ax.set_ylim(0,hi[2]-lo[2]);ax.set_zlim(2,10);ax.set_box_aspect([hi[0]-lo[0],hi[2]-lo[2],25]);ax.view_init(elev=30,azim=-60);ax.set_title('Lower source context (display clipped at 10 m HKPD)');fig.suptitle(model+' — unchanged source, no acceptance');fig.tight_layout();p=OUT/(model+'.png');fig.savefig(p,dpi=140);plt.close(fig)
  rows.append({'modelId':model,'sourceKey':r['sourceKey'],'sourceSHA256':r['sourceSHA256'],'worldSHA256':digest(np.asarray(tri,dtype='<f8').tobytes()),'buriedFaceIds':ids.tolist(),'components':details,'image':ref(p),'installationApproved':False})
 save(OUT/'context.json',{'rows':rows,'inputRefs':[ref(Path(__file__)),ref(PREV/'result.json'),ref(PREV/'ground.json.gz')],'sourceGeometryChanges':0,'newlyInstalled':0});print([(r['modelId'],len(r['buriedFaceIds']))for r in rows])
if __name__=='__main__':main()
