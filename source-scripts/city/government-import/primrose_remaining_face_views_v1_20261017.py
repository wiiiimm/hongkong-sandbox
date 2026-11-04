"""Bound exact remaining wall/underside evidence to inspectable source views."""
from pathlib import Path
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import BASE,SOURCE,GROUND,PODIUM,module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='government-xl-primrose-remaining-face-views-v1-20261017';DOC=BASE/BATCH
ROLES=BASE/'government-xl-primrose-podium-remaining-roles-v1-20261015'
def main():
 assert not DOC.exists();r=read(ROLES/'result.json');pins={x['path']:x['sha256']for x in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 source=next(r for r in read(SOURCE/'selection.json.gz')['rows']if r['uid']==PODIUM);asset=ROOT/source['candidate']['path'];paths=[SOURCE/'selection.json.gz',asset,GROUND/'after-ground.json.gz',ROLES/'original.json.gz']
 for p in paths:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))],p
 t=decode_original_world_triangles(asset.read_bytes());roles=read(ROLES/'original.json.gz');assert roles['worldSHA256']==digest(t.tobytes())
 ground=np.asarray(read(GROUND/'after-ground.json.gz')['completeRelevantDrawnTriplets']).reshape(-1,3,3);assert roles['groundSHA256']==digest(ground.tobytes())
 walls=[r['sourceFace']for r in roles['wallPaths']];undersides=[r['sourceFace']for r in roles['undersidePaths']];assert len(walls)==15 and len(undersides)==7
 ids=walls+undersides;centre=t[ids].mean(axis=(0,1));lo=t[ids].min(axis=(0,1))-3;hi=t[ids].max(axis=(0,1))+3;near=np.all(t.max(axis=1)>=lo,axis=1)&np.all(t.min(axis=1)<=hi,axis=1);ng=(ground[:,:,0].max(axis=1)>=lo[0])&(ground[:,:,0].min(axis=1)<=hi[0])&(ground[:,:,2].max(axis=1)>=lo[2])&(ground[:,:,2].min(axis=1)<=hi[2]);DOC.mkdir()
 for label,withground in [('source',False),('ground',True)]:
  fig=plt.figure(figsize=(16,8))
  for j,az in enumerate([-60,120]):
   ax=fig.add_subplot(1,2,j+1,projection='3d')
   for faces,color,alpha in [(t[near],'#bac5d1',.15),(t[walls],'#d95038',.8),(t[undersides],'#7f50c4',.85)]+([(ground[ng],'#51984b',.25)]if withground else[]):
    ax.add_collection3d(Poly3DCollection((faces-centre)[:,:,[0,2,1]],facecolor=color,edgecolor='#303030',alpha=alpha,linewidths=.35))
   for i in ids:
    c=t[i].mean(axis=0)-centre;ax.text(c[0],c[2],c[1],str(i),fontsize=7)
   ax.set(xlim=(lo[0]-centre[0],hi[0]-centre[0]),ylim=(lo[2]-centre[2],hi[2]-centre[2]),zlim=(lo[1]-centre[1],hi[1]-centre[1]),xlabel='X metres',ylabel='Z metres',zlabel='Height metres');ax.set_box_aspect((hi-lo)[[0,2,1]]);ax.view_init(elev=23,azim=az)
  fig.suptitle('Primrose exact remaining faces: red walls, purple lower closure'+(' with corrected ground'if withground else''));fig.tight_layout();fig.savefig(DOC/(label+'.png'),dpi=160);plt.close(fig)
 save(DOC/'context.json',dict(uid=PODIUM,sourceSHA256=source['sourceSHA256'],wallFaces=walls,undersideFaces=undersides,sourceVertices={str(i):t[i].tolist()for i in ids},worldSHA256=roles['worldSHA256'],groundSHA256=roles['groundSHA256'],fullAcceptance=False))
 refs=[Path(__file__),ROLES/'result.json',*paths,HERE/'exact_packed_world_geometry_20261009.py']
 out=module('primrose_view_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-remaining-wall-and-lower-closure-source-views-v1',refs,dict(uids=[PODIUM],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
