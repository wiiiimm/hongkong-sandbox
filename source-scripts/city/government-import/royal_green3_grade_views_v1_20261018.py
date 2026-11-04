"""Exact flagged Royal Green source wall views; diagnostic, no geometry edits."""
from pathlib import Path
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-royal-green3-grade-face-context-v1-20261018';CAP=BASE/'government-xl-royal-green3-retained-terrain-v1-20261017';BATCH='government-xl-royal-green3-grade-views-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=read(CAP/'selection.json.gz')['rows'][0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];t=decode_original_world_triangles(asset.read_bytes());rt=HERE/'local'/CAP.name/'runtime-geometry.json.gz';g=read(rt)['rows'][0];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);ctx=read(PRIOR/'original-candidate.json.gz');ids=[8310]+ctx['exactEdgeNeighbours'];assert ids==[8310,6631,8311]
 centre=t[ids].mean((0,1));lo=t[ids].min((0,1))-2;hi=t[ids].max((0,1))+2;near=np.all(t.max(1)>=lo,axis=1)&np.all(t.min(1)<=hi,axis=1);ng=(ground[:,:,0].max(1)>=lo[0])&(ground[:,:,0].min(1)<=hi[0])&(ground[:,:,2].max(1)>=lo[2])&(ground[:,:,2].min(1)<=hi[2]);DOC.mkdir()
 for label,withground in [('source',False),('ground',True)]:
  fig=plt.figure(figsize=(16,8))
  for j,az in enumerate([-60,120]):
   ax=fig.add_subplot(1,2,j+1,projection='3d')
   layers=[(t[near],'#bac5d1',.15),(t[[8310]],'#d95038',.9),(t[ids[1:]],'#7f50c4',.7)]+([(ground[ng],'#51984b',.25)]if withground else[])
   for faces,color,alpha in layers:ax.add_collection3d(Poly3DCollection((faces-centre)[:,:,[0,2,1]],facecolor=color,edgecolor='#303030',alpha=alpha,linewidths=.35))
   for i in ids:
    v=t[i].mean(0)-centre;ax.text(v[0],v[2],v[1],str(i),fontsize=8)
   ax.set(xlim=(lo[0]-centre[0],hi[0]-centre[0]),ylim=(lo[2]-centre[2],hi[2]-centre[2]),zlim=(lo[1]-centre[1],hi[1]-centre[1]),xlabel='X metres',ylabel='Z metres',zlabel='Height metres');ax.set_box_aspect((hi-lo)[[0,2,1]]);ax.view_init(elev=23,azim=az)
  fig.suptitle('Royal Green original: flagged face red, exact edge neighbours purple'+(' / candidate ground green'if withground else'')+'\nLocal diagnostic crop; not whole-source acceptance');fig.tight_layout();fig.savefig(DOC/(label+'.png'),dpi=160);plt.close(fig)
 save(DOC/'context.json',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],sourceFaces=ids,sourceVertices={str(i):t[i].tolist()for i in ids},nearbySourceFaces=np.flatnonzero(near).tolist(),groundSHA256=digest(ground.tobytes()),fullAcceptance=False,geometryChanges=0))
 out=module('royal_grade_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'royal-green3-exact-source-grade-views-v1',[Path(__file__),PRIOR/'result.json',*[ROOT/p for p in pins],asset,rt,HERE/'exact_packed_world_geometry_20261009.py'],dict(uids=[row['uid']],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
