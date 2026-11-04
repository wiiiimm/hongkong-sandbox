"""Paired terrain contact evidence and whole-original oblique context; no acceptance."""
from pathlib import Path
from collections import Counter
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-wave-verdant-contact-context-v1-20261017';DOC=BASE/BATCH
NAMES=['government-xl-wave-verdant-original-support-v1-20261017','government-xl-wave-verdant-source-tin-support-v1-20261017']
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};checks=[]
 for name in NAMES:
  d=BASE/name;r=read(d/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(d/'result.json')
  for e in r['evidenceRefs']:
   assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
  checks.append(read(d/'support.json.gz')['rows'][0]['proof'])
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 data=read(BASE/NAMES[0]/'input.json.gz');row=data['rows'][0];t=np.asarray(row['position']).reshape(-1,3)[np.asarray(row['index']).reshape(-1,3)];lo=t.min((0,1));hi=t.max((0,1));origin=(lo+hi)/2
 before={tuple(x['position']):x for x in checks[1]['unresolved']};after={tuple(x['position']):x for x in checks[0]['unresolved']}
 summary=dict(uid=row['uid'],completeOriginalFaces=len(t),candidateReasons=dict(Counter(x['reason']for x in after.values())),sourceTinReasons=dict(Counter(x['reason']for x in before.values())),unresolvedOnBoth=len(before.keys()&after.keys()),candidateOnlyUnresolved=len(after.keys()-before.keys()),sourceTinOnlyUnresolved=len(before.keys()-after.keys()),fullAcceptance=False)
 save(DOC/'summary.json',summary);save(DOC/'candidate-only-failures.json',[after[k]for k in after.keys()-before.keys()])
 for n,name in enumerate(NAMES):
  ground=np.asarray(read(BASE/name/'input.json.gz')['podium']);keep=np.all(ground.max(1)[:,[0,2]]>=lo[[0,2]]-5,axis=1)&np.all(ground.min(1)[:,[0,2]]<=hi[[0,2]]+5,axis=1);g=ground[keep];points=np.asarray([x['position']for x in checks[n]['unresolved']]);fig=plt.figure(figsize=(15,12),dpi=120)
  for j,az in enumerate([-45,45,135,225],1):
   ax=fig.add_subplot(2,2,j,projection='3d');ax.add_collection3d(Poly3DCollection((g-origin)[:,:,[0,2,1]],facecolors='#c4b78d',edgecolors='#777777',linewidths=.05,alpha=1));ax.add_collection3d(Poly3DCollection((t-origin)[:,:,[0,2,1]],facecolors='#6e9fbd',edgecolors='#333333',linewidths=.06,alpha=1));q=points-origin;ax.scatter(q[:,0],q[:,2],q[:,1],color='red',s=8,depthshade=False);b=np.array([lo,hi])-origin;ax.set(xlim=[b[0,0]-5,b[1,0]+5],ylim=[b[0,2]-5,b[1,2]+5],zlim=[min(g[:,:,1].min(),lo[1])-origin[1]-1,b[1,1]+1],title=('Candidate terrain'if n==0 else 'Authenticated source TIN')+f' / azimuth {az}');ax.set_box_aspect((hi-lo)[[0,2,1]]+[10,10,1]);ax.view_init(22,az)
  fig.suptitle('Complete unchanged Verdant Villa original; red unresolved samples. Terrain shown only around building bounds.');fig.tight_layout();fig.savefig(DOC/('candidate.png'if n==0 else 'source-tin.png'));plt.close(fig)
 save(DOC/'qualification.json',dict(fullAcceptance=False,geometryEdited=False,notes='Opaque whole original retained; terrain context bounds cropped, not full-domain clearance proof. Contact delta compares identical captured source positions.'))
 out=module('verdant_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'verdant-paired-terrain-contact-context-v1',list(set(refs)),dict(uids=[row['uid']],summary=summary,fullAcceptance=False,newlyInstalled=0));print(summary,flush=True);print(out['jobId'],flush=True)
if __name__=='__main__':main()
