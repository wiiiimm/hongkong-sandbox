"""Inspect unchanged podium lower interfaces and actual corrected terrain."""
from pathlib import Path
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-olympian-two-three-podium-terrain-v2-20261018';LOC=BASE/'government-xl-olympian-two-podium-clearance-locations-v2-20261018';BATCH='government-xl-olympian-two-grade-views-v1-20261018';DOC=BASE/BATCH
r=read(LOC/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
DOC.mkdir();summaries=[]
for g in read(HERE/'local'/CAP.name/'runtime-geometry.json.gz')['rows']:
 uid=g['uid'];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);loc=read(LOC/(uid.split('/')[1]+'-locations.json.gz'));ids=sorted({i for p in loc['rows']for i in p['incidentIndexedFaces']});f=t[ids];lo=f.min((0,1))-2;hi=f.max((0,1))+2;centre=(lo+hi)/2
 near=np.all(t.max(1)>=lo,axis=1)&np.all(t.min(1)<=hi,axis=1);ng=(ground[:,:,0].max(1)>=lo[0])&(ground[:,:,0].min(1)<=hi[0])&(ground[:,:,2].max(1)>=lo[2])&(ground[:,:,2].min(1)<=hi[2]);fig=plt.figure(figsize=(18,9))
 for j,az in enumerate([-60,120]):
  ax=fig.add_subplot(1,2,j+1,projection='3d')
  for faces,color,alpha in [(t[near],'#bac5d1',.12),(ground[ng],'#51984b',.25),(f,'#d95038',.8)]:ax.add_collection3d(Poly3DCollection((faces-centre)[:,:,[0,2,1]],facecolor=color,edgecolor='#303030',alpha=alpha,linewidths=.2))
  ax.set(xlim=(lo[0]-centre[0],hi[0]-centre[0]),ylim=(lo[2]-centre[2],hi[2]-centre[2]),zlim=(lo[1]-centre[1],hi[1]-centre[1]),xlabel='X metres',ylabel='Z metres',zlabel='Height metres');ax.set_box_aspect(np.maximum((hi-lo)[[0,2,1]],1));ax.view_init(elev=18,azim=az)
 fig.suptitle(uid+' original lower source faces (red), candidate ground (green)\nExact geometry; local interface crop only');fig.tight_layout();name=uid.replace('/','-').replace(':','-')+'.png';fig.savefig(DOC/name,dpi=160);plt.close(fig);summaries.append(dict(uid=uid,sourceSHA256=g['sourceSHA256'],faces=ids,filename=name,bounds=[lo.tolist(),hi.tolist()],groundSHA256=digest(ground.tobytes())))
save(DOC/'context.json',dict(rows=summaries,fullAcceptance=False))
module('views_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-original-lower-interface-views-v1',[Path(__file__),LOC/'result.json',*[ROOT/p for p in pins]],dict(uids=[x['uid']for x in summaries],fullAcceptance=False))
