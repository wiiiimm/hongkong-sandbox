"""Original horizontal sections through the two flagged vertical junction faces."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PHYS=BASE/'government-xl-oi-sin-four-originals-physical-v2-20261017';RT=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';BATCH='government-xl-oi-sin-carpark-junction-sections-v1-20261017';DOC=BASE/BATCH

def section(mesh,y):
 rows=[]
 for i,t in enumerate(mesh):
  pts=[]
  for a,b in zip(t,np.roll(t,-1,axis=0)):
   if (a[1]<y<b[1])or(b[1]<y<a[1]):pts.append(a+(b-a)*((y-a[1])/(b[1]-a[1])))
   elif a[1]==y:pts.append(a)
  unique=np.unique(pts,axis=0)if pts else []
  if len(unique)==2:rows.append(dict(face=i,segment=unique[:,[0,2]].tolist()))
 return rows

def main():
 assert not DOC.exists();r=read(PHYS/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pin=next(e['sha256']for e in r['evidenceRefs']if ROOT/e['path']==RT);assert digest(RT.read_bytes())==pin
 geo={g['uid']:np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]for g in read(RT)['rows']};source=geo['landsd/256457:0'];host=geo['landsd/91128:0'];rows=[]
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.collections import LineCollection
 fig,axes=plt.subplots(2,3,figsize=(15,9),dpi=160)
 origin=source[[68,69]].mean(axis=(0,1))[[0,2]]
 for row,fi in enumerate([68,69]):
  lo,hi=source[fi,:,1].min(),source[fi,:,1].max()
  for col,f in enumerate([.125,.5,.875]):
   y=lo+(hi-lo)*f;ss=section(source,y);hs=section(host,y);target=[x for x in ss if x['face']==fi];assert target
   ax=axes[row,col]
   for ls,color,width in [(hs,'#666666',1.2),(ss,'#1686be',1.8),(target,'#e32636',3.8)]:
    ax.add_collection(LineCollection([np.asarray(x['segment'])-origin for x in ls],colors=color,linewidths=width))
   ax.set(xlim=(-1.3,1.3),ylim=(-1.3,1.3),aspect='equal',xlabel='East offset (m)',ylabel='South offset (m)',title=f'Face {fi}; height {y:.6f}m');ax.grid(alpha=.2)
   rows.append(dict(face=fi,height=float(y),fraction=f,sourceSections=ss,hostSections=hs))
 DOC.mkdir();fig.suptitle('Unchanged original sections: carpark blue, podium grey, flagged face red');fig.tight_layout();fig.savefig(DOC/'sections.png');plt.close(fig)
 save(DOC/'sections.json.gz',dict(rows=rows,originXZ=origin.tolist(),qualification='Three diagnostic sections per flagged face; not a complete volume or physical acceptance proof.',fullAcceptance=False))
 out=module('oi_junction_sections_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-original-junction-horizontal-sections-v1',[Path(__file__),RT,PHYS/'result.json'],dict(uids=['landsd/256457:0','landsd/91128:0'],faces=[68,69],fullAcceptance=False,nextStep='Review exact source junction function using original cross-sections; no geometry edits or approval waiver.'))
 print(out['jobId'],flush=True)
if __name__=='__main__':main()
