from pathlib import Path
import json,gzip,hashlib,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
base=Path('docs/astra-city/government-import')
b=base/'government-xl-citywalk-saved294-source-layer-attribution-v1-20261014'
out=base/'government-xl-citywalk-saved294-combined-junction-review-v1-20261015';out.mkdir(exist_ok=True)
paths=[b/'input.json.gz',b/'complete-saved294-source-layer-attribution.json.gz']
refs=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in paths]
d=json.loads(gzip.decompress(paths[0].read_bytes()));r=json.loads(gzip.decompress(paths[1].read_bytes()))
faces=np.asarray(d['sourceWorlds'][0]['position']).reshape(-1,3,3)
global_path=base/'government-xl-complete-current-native-actual-position-matrix-bounds-v4-20261012/input.json.gz'
global_rows={q['uid']:q for q in json.loads(gzip.decompress(global_path.read_bytes()))['rows']}
rebound={q['uid']:q for q in d['currentRelevantTupleRebind']['towerTuples']}
refs.append(dict(path=str(global_path),sha256=hashlib.sha256(global_path.read_bytes()).hexdigest()))
rows=r['sourceWorldRows'][0]['rows'];uids=sorted(set(x['uid']for x in rows));fig=plt.figure(figsize=(18,15))
summary=[]
for i,uid in enumerate(uids):
 rr=[x for x in rows if x['uid']==uid];p=np.asarray([x['failure']['position']for x in rr]);ids=sorted(set(h['faceIndex']for x in rr for h in x['EPSModelGeometry']['highestSourceHits']))
 binding=global_rows[uid];asset=Path(binding['source']['path']);raw=asset.read_bytes();assert hashlib.sha256(raw).hexdigest()==binding['source']['sha256']==rr[0]['originalTowerSourceSHA256'];tower=decode_original_world_triangles(raw)
 assert hashlib.sha256(np.asarray(tower,dtype='<f8').tobytes()).hexdigest()==binding['completeOriginalPOSITIONProof']['worldTrianglesSHA256'];assert binding['rawCurrentEntry']==rebound[uid]['rawCurrentEntry']
 refs.append(binding['source']);lo=p.min(axis=0);hi=p.max(axis=0);tower_ids=np.flatnonzero(tower[:,:,1].min(axis=1)<=hi[1]+5)
 mask=(faces[:,:,0].max(axis=1)>=lo[0]-3)&(faces[:,:,0].min(axis=1)<=hi[0]+3)&(faces[:,:,2].max(axis=1)>=lo[2]-3)&(faces[:,:,2].min(axis=1)<=hi[2]+3)&(faces[:,:,1].max(axis=1)>=lo[1]-3)&(faces[:,:,1].min(axis=1)<=hi[1]+3)
 origin=np.array([lo[0],0,lo[2]])
 for j,(elev,azim) in enumerate([(80,-60),(18,-60)]):
  ax=fig.add_subplot(5,2,i*2+j+1,projection='3d')
  def xyz(a):return (a-origin)[:,:,[0,2,1]]
  ax.add_collection3d(Poly3DCollection(xyz(faces[mask]),facecolors='#acc6ca',edgecolors='#526c74',linewidths=.12,alpha=.18))
  ax.add_collection3d(Poly3DCollection(xyz(tower[tower_ids]),facecolors='#6388d6',edgecolors='#234776',linewidths=.2,alpha=.35))
  ax.add_collection3d(Poly3DCollection(xyz(faces[ids]),facecolors='#eaa53a',edgecolors='#67481b',linewidths=.5,alpha=.85))
  pp=p-origin;ax.scatter(pp[:,0],pp[:,2],pp[:,1],c='#d22f43',s=4,depthshade=False)
  ax.set_xlim(-3,hi[0]-lo[0]+3);ax.set_ylim(-3,hi[2]-lo[2]+3);ax.set_zlim(lo[1]-1,hi[1]+5);ax.view_init(elev=elev,azim=azim);ax.set_box_aspect((max(hi[0]-lo[0],1),max(hi[2]-lo[2],1),6));ax.set_title(uid+' — '+str(len(rr))+' fixed points');ax.set_zlabel('HKPD m')
 summary.append(dict(uid=uid,points=len(rr),highestFaceIDs=ids,contextFaceIDs=np.flatnonzero(mask).tolist(),towerOriginalFaceIDs=tower_ids.tolist(),completeTowerFaces=len(tower),originalWorldHashVerified=True))
fig.suptitle('Citywalk original podium: amber highest hit faces; red saved tower-bottom points\nBlue original tower walls; contextual display crop only; no acceptance',fontsize=14);fig.tight_layout(rect=[0,0,1,.96]);fig.savefig(out/'combined-junction-context-2160x1800.png',dpi=120);plt.close(fig)
(out/'review-inputs.json').write_text(json.dumps(dict(inputs=refs,sourceOnly=True,acceptance=False,geometryEdited=False,contextSelection='Podium closed XYZ AABB within3m; tower faces with minimumY<=rim+5m; whole selected faces retained; axes cropped for display only',rows=summary),indent=2)+'\n')
print(out)
