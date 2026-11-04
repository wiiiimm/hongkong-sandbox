"""Context views of original flagged walls, no geometry modifications."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-vertical-views-v1-20261019';DOC=BASE/BATCH;SRC=BASE/'government-xl-lai-chi-kok-vertical-context-v1-20261019'
def main():
 assert not DOC.exists();r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json'];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];pins[p]=e['sha256'];refs.append(p)
 p=HERE/'local/government-xl-lai-chi-kok-full-terrain-metrics-v3-20261019/runtime-geometry.json.gz';assert p in pins;g=read(p)['rows'][0];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert len(t)==37577
 records=read(SRC/'original.json')['faces'];ids=np.asarray([r['faceId']for r in records]);v=t[ids];assert np.max(np.abs(v-np.asarray([r['vertices']for r in records])))<1e-8
 centres=v.mean(1);pending=set(range(len(ids)));groups=[]
 while pending:
  seed=min(pending);pending.remove(seed);group={seed};todo=[seed]
  while todo:
   i=todo.pop();near={j for j in pending if np.linalg.norm(centres[i,[0,2]]-centres[j,[0,2]])<=20};pending-=near;group|=near;todo.extend(sorted(near))
  groups.append(sorted(group))
 DOC.mkdir(parents=True);outputs=[]
 for k,group in enumerate(groups):
  walls=v[group];lo=walls.min((0,1));hi=walls.max((0,1));low=lo[[0,2]]-10;high=hi[[0,2]]+10;mask=(t[:,:,0].max(1)>=low[0])&(t[:,:,0].min(1)<=high[0])&(t[:,:,2].max(1)>=low[1])&(t[:,:,2].min(1)<=high[1]);context=t[mask]
  fig=plt.figure(figsize=(14,6))
  for pane,az in enumerate([-60,120]):
   ax=fig.add_subplot(1,2,pane+1,projection='3d');ax.add_collection3d(Poly3DCollection(context[:,:,[0,2,1]],facecolor='#a8c3cb',edgecolor='none',alpha=.25));ax.add_collection3d(Poly3DCollection(walls[:,:,[0,2,1]],facecolor='crimson',edgecolor='black',linewidth=.5,alpha=1));ax.set(xlim=(low[0],high[0]),ylim=(low[1],high[1]),zlim=(min(context[:,:,1].min(),lo[1])-1,max(context[:,:,1].max(),hi[1])+1));ax.view_init(28,az);ax.set_box_aspect((high[0]-low[0],high[1]-low[1],max(12,np.ptp(context[:,:,1]))));ax.set_title('Opposite view '+str(pane+1))
  fig.suptitle('Original platform context: red flagged walls / translucent original source — group '+str(k+1));fig.tight_layout();image=DOC/('group-'+str(k+1)+'.png');fig.savefig(image,dpi=140);plt.close(fig);outputs.append(dict(group=k+1,faceIds=ids[group].tolist(),contextFaces=int(mask.sum()),image=str(image.relative_to(ROOT))))
 save(DOC/'summary.json',dict(groups=outputs,installationApproved=False));print(outputs,flush=True)
 module('vertical_view_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-vertical-wall-context-views',list(dict.fromkeys(refs)),dict(uids=['landsd/281463:0'],groups=outputs,installationApproved=False))
if __name__=='__main__':main()
