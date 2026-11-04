"""Original roof detail context only; no geometric changes or role approval."""
import numpy as np,json,gzip,struct
from pathlib import Path
from run import ROOT,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
D=ROOT/'docs/astra-city/government-import/government-xl-parkview-block6-bounded-eligible-native-route-v2-20261011';OLD=ROOT/'docs/astra-city/government-import/government-xl-parkview-block6-bounded-original-clear-cap-probe-v1-20261011';G=ROOT/'docs/astra-city/government-import/government-xl-parkview-block6-complete-original-support-paths-v1-20261011'
def main():
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 r=read(OLD/'diagnostic.json.gz');p=ROOT/r['evidenceRefs'][2]['path'];raw=p.read_bytes();original=decode_original_world_triangles(raw);t=original[:,:,[0,2,1]];cs=read(G/'diagnostic.json.gz')['completeSourceEdgeBodyFaces'];visible=np.flatnonzero(t[:,:,2].max(1)>371);fig=plt.figure(figsize=(13,6),dpi=180)
 for pos,elev,azim in [(121,90,-90),(122,20,-60)]:
  ax=fig.add_subplot(pos,projection='3d');ax.add_collection3d(Poly3DCollection(t[visible],facecolors='#cccccc',edgecolors='#555555',linewidths=.15,alpha=.45))
  for i,color in zip([78,79,80,83],['red','blue','green','orange']):
   ax.add_collection3d(Poly3DCollection(t[cs[i]],facecolors=color,edgecolors='black',linewidths=.5));v=t[cs[i]].mean((0,1));ax.text(v[0],v[1],v[2]+.5,str(i),color=color)
  ax.set_xlim(4204,4228);ax.set_ylim(3288,3310);ax.set_zlim(370,377);ax.set_box_aspect((24,22,7));ax.view_init(elev=elev,azim=azim);ax.set_xlabel('original world X');ax.set_ylabel('original world Z');ax.set_zlabel('original world Y');ax.set_title('Unchanged original source; roof bodies highlighted')
 fig.tight_layout();fig.savefig(D/'original-roof-context.png');plt.close(fig)
 b=gzip.decompress(raw)if raw[:2]==b'\x1f\x8b'else raw;length,kind=struct.unpack_from('<II',b,12);gl=json.loads(b[20:20+length]);save(D/'original-node-context.json',dict(originalSourceSHA256=digest(raw),completeOriginalNodes=gl['nodes'],completeOriginalMeshes=[dict(name=m.get('name'),primitives=[dict(material=x.get('material'),attributes=x.get('attributes'),indices=x.get('indices'))for x in m['primitives']])for m in gl['meshes']],sourceOnly=True,roleApproval=False))
if __name__=='__main__':main()
