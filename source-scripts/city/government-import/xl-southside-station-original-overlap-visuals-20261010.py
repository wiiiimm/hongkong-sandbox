"""Complete original surfaces/parts for the exact current foreign overlap; no edits."""
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from source_closed_components import components
BATCH='government-xl-southside-station-original-relationship-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
def main():
 assert not (DOC/'result.json').exists();x=read(DOC/'diagnostic.json.gz')
 for p,h in x['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p
 paths=[next(ROOT/k for k in x['inputHashes'] if k.endswith(model['model']['asset']['sha256']+'.glb.gz')) for model in x['native']];a,b=[decode_original_world_triangles(p.read_bytes()) for p in paths];assert [len(a),len(b)]==x['completeSourceFaceCounts'];parts=components(a)['components'];ids=set(x['allOverlapOriginalFaceIds']);involved=[{'component':i,'completeOriginalFaceIds':p['faceIndices'],'overlapOriginalFaceIds':sorted(ids&set(p['faceIndices'])),'completeTopology':{k:v for k,v in p.items() if k!='faceIndices'},'completeBounds':[a[p['faceIndices']].min(axis=(0,1)).tolist(),a[p['faceIndices']].max(axis=(0,1)).tolist()]} for i,p in enumerate(parts) if ids&set(p['faceIndices'])];outputs=[]
 # Every original triangle is shown; only plotting coordinates reorder X/Z/Y.
 fig=plt.figure(figsize=(16,12),dpi=150);ax=fig.add_subplot(111,projection='3d');
 for t,color,alpha in [(a,'#bab8b0',.22),(b,'#2c6dba',.55),(a[sorted(ids)],'#d4512c',.95)]:ax.add_collection3d(Poly3DCollection(t[:,:,[0,2,1]],facecolors=color,edgecolors=color,linewidths=.16,alpha=alpha))
 both=np.concatenate([a,b]);lo,hi=both.min(axis=(0,1)),both.max(axis=(0,1));ax.set_xlim(lo[0]-1,hi[0]+1);ax.set_ylim(lo[2]-1,hi[2]+1);ax.set_zlim(lo[1]-1,hi[1]+1);ax.set_box_aspect([hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]]);ax.view_init(elev=22,azim=-55);ax.set_xlabel('Original world X / m');ax.set_ylabel('Original world Z / m');ax.set_zlabel('HKPD height / m');ax.set_title('Complete unchanged Southside + Wong Chuk Hang station originals\nOrange: all34 source faces involved in raw current foreign overlap; blue: complete1191-face original station');fig.tight_layout();p=DOC/'complete-original-pair-2400x1800.png';fig.savefig(p);plt.close(fig);outputs.append({'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes()),'width':2400,'height':1800,'allOriginalFacesShown':True})
 fig,ax=plt.subplots(figsize=(16,12),dpi=150)
 for t,color in [(b,'#2c6dba'),(a,'#77766e'),(a[sorted(ids)],'#d4512c')]:
  for face in t:ax.plot(np.r_[face[:,0],face[0,0]],np.r_[face[:,2],face[0,2]],color=color,lw=.15)
 for form in x['completeCurrentForms']:
  if form['uid'] not in x['uids']:continue
  for ring in form['rings']:v=np.asarray(ring);ax.plot(v[:,0],v[:,1],color='black',lw=1)
 ax.invert_yaxis();ax.set_aspect('equal');ax.set_title('Exact original source surfaces with retained current target outlines\nNo source edits, source omissions, footprint expansion, actor removal or acceptance');ax.set_xlabel('Original world X / m');ax.set_ylabel('Original world Z / m (north upward)');fig.tight_layout();p=DOC/'exact-original-overlap-top-2400x1800.png';fig.savefig(p);plt.close(fig);outputs.append({'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes()),'width':2400,'height':1800,'allOriginalFacesShown':True})
 save(DOC/'overlap-component-visual-context.json.gz',{'completeOriginalSourceComponents':len(parts),'completeInvolvedOriginalComponents':involved,'rawOverlapOriginalFaceCount':len(ids),'completeOriginalSourceFaceCount':len(a),'plots':outputs,'sourceGeometryChanges':0,'identityAccepted':False,'physicalAccepted':False,'qualification':'All original source faces/component topology retained. Full raw overlap surfaces may occur on distant upper roof/envelope above the adjacent podium; that is not automatically podium support or real collision. Independently interpreted source relationship and full physical/runtime gates remain required.'});print({'originalComponents':len(parts),'overlapComponents':len(involved),'plots':len(outputs)},flush=True)
if __name__=='__main__':main()
