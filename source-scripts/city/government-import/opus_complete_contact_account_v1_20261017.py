"""Account for every actual rim sample; keep canonical failures and bounded witnesses."""
from pathlib import Path
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-opus-complete-contact-account-v1-20261017';DOC=BASE/BATCH;COMBINED=BASE/'government-xl-opus-combined-ground-interfaces-v1-20261017';WITNESS=BASE/'government-xl-opus-four-world-contacts-v1-20261017';GROUND=BASE/'government-xl-opus-companion-original-patch-v1-20261017'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [COMBINED,WITNESS,GROUND]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for x in r['evidenceRefs']:pins.setdefault(x['path'],set()).add(x['sha256'])
 def consume(p):
  assert digest(p.read_bytes()) in pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 actual=consume(COMBINED/'interfaces.json.gz');witness=consume(WITNESS/'contacts.json.gz');worlds=consume(WITNESS/'world-triangles.json.gz');cap=consume(GROUND/'drawn-patch.json.gz');rows=[]
 for row in actual['rows']:
  mode=row['mode'];uid=row['uid'];proof=row['proof'];saved=next(r['rows'] for r in witness['rows'] if r['mode']==mode);mapped=[]
  for failure in proof['unresolved']:
   matches=[r for r in saved if r['uid']==uid and r['originalPosition']==failure['position']];assert len(matches)==1
   w=matches[0];assert w.get('verified') and all(w['checks'].values()) and w['travelM']<=.5
   mapped.append(dict(rawFailure=failure,verifiedOriginalWallContact=w))
  assert proof['samples']==proof['strictContacts']+proof['wallIntersections']+len(mapped)
  rows.append(dict(mode=mode,uid=uid,samples=proof['samples'],strictGroundOrPodiumContacts=proof['strictContacts'],canonicalSameWallContacts=proof['wallIntersections'],boundedOriginalWallContacts=len(mapped),allSamplesAccounted=True,rawCanonicalPassed=proof['passed'],mapped=mapped))
 DOC.mkdir();save(DOC/'account.json.gz',dict(rows=rows,qualification='Every unchanged rim sample retains its canonical result or verified original-face intersection within 0.5m. Source-role review, full assembly foundation, identity, neighbours and runtime are still required.',fullAcceptance=False))
 world=worlds['original'];ground=np.array(cap['position']).reshape(-1,3)[np.array(cap['index']).reshape(-1,3)];lo=np.array([1466,230,1988]);hi=np.array([1520,247,2035]);centre=(lo+hi)/2
 fig=plt.figure(figsize=(16,8))
 for j,az in enumerate([-60,120]):
  ax=fig.add_subplot(1,2,j+1,projection='3d')
  for uid,col in [('landsd/248432:0','#4281bd'),('landsd/319559:0','#f09737'),('landsd/322573:0','#ce4646')]:
   t=np.array(world[uid]);mask=np.all(t.max(1)>=lo,axis=1)&np.all(t.min(1)<=hi,axis=1);ax.add_collection3d(Poly3DCollection((t[mask]-centre)[:,:,[0,2,1]],facecolor=col,alpha=.6,edgecolor='#333333',linewidth=.2))
  mask=np.all(ground.max(1)>=lo,axis=1)&np.all(ground.min(1)<=hi,axis=1);ax.add_collection3d(Poly3DCollection((ground[mask]-centre)[:,:,[0,2,1]],facecolor='#76a062',alpha=.12,linewidth=0))
  points=[m['verifiedOriginalWallContact']['contact'] for r in rows if r['mode']=='original' for m in r['mapped']];q=np.array(points)-centre;ax.scatter(q[:,0],q[:,2],q[:,1],c='#151515',s=8)
  ax.set(xlim=(lo[0]-centre[0],hi[0]-centre[0]),ylim=(lo[2]-centre[2],hi[2]-centre[2]),zlim=(lo[1]-centre[1],hi[1]-centre[1]),xlabel='X metres',ylabel='Z metres',zlabel='Height metres');ax.set_box_aspect((hi-lo)[[0,2,1]]);ax.view_init(elev=25,azim=az)
 fig.suptitle('Unchanged Opus source junctions: podium blue, companion orange, tower red; verified contacts black');fig.tight_layout();fig.savefig(DOC/'source-junctions.png',dpi=140);plt.close(fig)
 summary=[{k:v for k,v in r.items() if k!='mapped'} for r in rows];save(DOC/'summary.json',dict(rows=summary,fullAcceptance=False,newlyInstalled=0))
 result=module('opus_account_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-complete-rim-sample-account-with-ground-v1',refs,dict(uids=sorted(world),rows=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=result['jobId'],rows=summary),flush=True)
if __name__=='__main__':main()
