"""View unchanged residual face groups with original native terrain witnesses."""
from pathlib import Path
import importlib.util
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PREV=BASE/'government-xl-unmapped-continuous-native-ground-v1-20261015';OUT=BASE/'government-xl-unmapped-residual-views-v1-20261015'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not OUT.exists();OUT.mkdir();prior=read(PREV/'result.json')
 for q in prior['evidenceRefs']:assert ref(ROOT/q['path'])==q
 spec=importlib.util.spec_from_file_location('residual_original_decode',HERE/'xl-final-script-pass.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);recovery=read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows'];rows=[]
 for summary in prior['rows']:
  model=summary['modelId'];data=read(PREV/(model+'.json.gz'));source=next(r for r in recovery if r['modelId']==model);tri=decode_original_world_triangles((ROOT/source['asset']['path']).read_bytes());terrain=np.concatenate([f.s.terrain_triangles(ROOT/p)for p in data['terrainPaths']]);failed=summary['continuousBelowHalfMetreFaces'];up=summary['upwardBelowHalfMetreFaces'];mask=np.zeros(len(tri),dtype=bool);mask[up]=True;groups=f.connected_components(tri,mask)
  for number,group in enumerate(groups):
   a=tri[group];lo,hi=a.min(axis=(0,1)),a.max(axis=(0,1));bounds=[lo[0]-3,lo[2]-3,hi[0]+3,hi[2]+3];selected=(tri[:,:,0].max(axis=1)>=bounds[0])&(tri[:,:,0].min(axis=1)<=bounds[2])&(tri[:,:,2].max(axis=1)>=bounds[1])&(tri[:,:,2].min(axis=1)<=bounds[3])&(tri[:,:,1].min(axis=1)<=hi[1]+5);g=(terrain[:,:,0].max(axis=1)>=bounds[0])&(terrain[:,:,0].min(axis=1)<=bounds[2])&(terrain[:,:,2].max(axis=1)>=bounds[1])&(terrain[:,:,2].min(axis=1)<=bounds[3]);origin=np.array([lo[0],0,lo[2]]);fig=plt.figure(figsize=(15,7))
   for j,angle in enumerate([-60,120]):
    ax=fig.add_subplot(1,2,j+1,projection='3d');ax.add_collection3d(Poly3DCollection((tri[selected]-origin)[:,:,[0,2,1]],facecolors='#bbcbd8',edgecolors='#53616b',linewidths=.3,alpha=.45));ax.add_collection3d(Poly3DCollection((terrain[g]-origin)[:,:,[0,2,1]],facecolors='#b1bf8d',edgecolors='#638048',linewidths=.4,alpha=.3));ax.add_collection3d(Poly3DCollection((a-origin)[:,:,[0,2,1]],facecolors='#e52b2b',edgecolors='#8b0000',linewidths=.5));ax.set_xlim(-3,hi[0]-lo[0]+3);ax.set_ylim(-3,hi[2]-lo[2]+3);ax.set_zlim(lo[1]-1,hi[1]+5);ax.set_box_aspect([hi[0]-lo[0]+6,hi[2]-lo[2]+6,6]);ax.view_init(elev=30,azim=angle);ax.set_title('Original source blue; terrain green; failed upward faces red')
   fig.suptitle(model+' residual group '+str(number)+' (display crop only)');fig.tight_layout();p=OUT/(model+'-'+str(number)+'.png');fig.savefig(p,dpi=125);plt.close(fig);rows.append({'modelId':model,'group':number,'sourceSHA256':source['sourceSHA256'],'faceIds':[int(i)for i in group],'triangles':a.tolist(),'bounds':[lo.tolist(),hi.tolist()],'witnesses':[data['faces'][int(i)]for i in group],'image':ref(p)})
 save(OUT/'groups.json',{'rows':rows,'inputRefs':[ref(Path(__file__)),ref(PREV/'result.json')],'sourceGeometryChanges':0,'installationApproved':False});print([(r['modelId'],r['group'],r['faceIds'])for r in rows])
if __name__=='__main__':main()
