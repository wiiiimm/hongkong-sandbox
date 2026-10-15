"""Render complete problematic originals and incident faces against source-native ground."""
from pathlib import Path
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-hkust-native-residual-inventory-v1-20261015';GROUND=B/'government-xl-hkust-adjoining-native-terrain-v1-20261015/native-ground.json.gz';P=B/'government-xl-hkust309822-232155-target-provenance-draft-v1-20261014/cached-complete-original-arrays-v1';DOC=B/'government-xl-hkust-ground-crossing-views-v1-20261015'
def main():
 assert not DOC.exists();old=read(OLD/'result.json');pins={r['path']:r['sha256'] for r in old['evidenceRefs']};inventory=read(OLD/'inventory.json.gz');assert digest((OLD/'inventory.json.gz').read_bytes())==pins[str((OLD/'inventory.json.gz').relative_to(ROOT))];gp=read(GROUND.parent/'result.json');assert digest(GROUND.read_bytes())==next(r['sha256'] for r in gp['evidenceRefs'] if r['path']==str(GROUND.relative_to(ROOT)));ground=np.array(read(GROUND)['completeOriginalTerrainTriangles']);paths=[Path(__file__),OLD/'result.json',OLD/'inventory.json.gz',GROUND,GROUND.parent/'result.json'];DOC.mkdir();bindings=[];fig=plt.figure(figsize=(16,14));slot=0
 for row in inventory['rows']:
  uid=row['uid'];p=P/(uid.replace('/','-').replace(':','-')+'.json.gz');assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];tri=np.array(read(p)['completeOrderedOriginalTriangles']);paths.append(p)
  for faceid in row['otherBelowFaces']:
   face=tri[faceid];shared=np.any(np.all(tri[:,: ,None,:]==face[None,None,:,:],axis=3),axis=(1,2));incident=np.flatnonzero(shared);lo,hi=face.min(0)-1,face.max(0)+1;gm=(ground[:,:,0].max(1)>=lo[0])&(ground[:,:,0].min(1)<=hi[0])&(ground[:,:,2].max(1)>=lo[2])&(ground[:,:,2].min(1)<=hi[2]);g=ground[gm];origin=np.array([face[:,0].mean(),0,face[:,2].mean()]);conv=lambda a:(a-origin)[:,:,[0,2,1]]
   for angle in [-55,125]:
    slot+=1;ax=fig.add_subplot(4,2,slot,projection='3d');ax.add_collection3d(Poly3DCollection(conv(g),facecolor='#d7bd81',edgecolor='#8f794d',alpha=.28,linewidth=.2));ax.add_collection3d(Poly3DCollection(conv(tri[incident]),facecolor='#6e9ec3',edgecolor='#42647d',alpha=.35,linewidth=.2));ax.add_collection3d(Poly3DCollection(conv(face[None]),facecolor='#d93025',edgecolor='#6f1010',alpha=1,linewidth=.6));shown=np.concatenate([tri[incident].reshape(-1,3),g.reshape(-1,3)]);bounds=[shown.min(0),shown.max(0)];ax.set_xlim(bounds[0][0]-origin[0],bounds[1][0]-origin[0]);ax.set_ylim(bounds[0][2]-origin[2],bounds[1][2]-origin[2]);ax.set_zlim(bounds[0][1],bounds[1][1]);ax.set_box_aspect((bounds[1]-bounds[0])[[0,2,1]]);ax.view_init(elev=20,azim=angle);ax.set_title(f'{uid} face{faceid}; full incident source facets');ax.set_zlabel('HKPD m')
   bindings.append({'uid':uid,'sourceFace':faceid,'wholeIncidentSourceFaces':incident.tolist(),'contextTerrainFaces':np.flatnonzero(gm).tolist(),'displayOnlyOrigin':origin.tolist(),'originalFaceVertices':face.tolist()})
 fig.suptitle('Unchanged source: red investigated face, blue incident faces, amber native terrain\nDisplay context only; no contact or source-role approval');fig.tight_layout(rect=[0,0,1,.96]);fig.savefig(DOC/'four-faces-opposing-context.png',dpi=150);plt.close(fig);save(DOC/'bindings.json',{'bindings':bindings,'sourceGeometryChanges':0,'acceptance':False})
 module('hkust_views_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(DOC.name,'hkust-original-ground-crossing-context-views-v1',paths,{'uids':old['uids'],'wholeInvestigatedFaces':4,'nextStep':'ROOT inspect exact wall continuity; source-ground intersections remain raw failures until precise functional applicability review, runtime proof and identity resolution.'})
if __name__=='__main__':main()
