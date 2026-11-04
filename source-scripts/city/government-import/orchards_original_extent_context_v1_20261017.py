"""Locate complete Orchards Tower2 source extent by authored height; no acceptance."""
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-three-current-originals-v1-20261017';BATCH='government-xl-orchards-original-extent-context-v1-20261017';DOC=BASE/BATCH;UID='landsd/254629:0'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=next(x for x in read(PRIOR/'selection.json.gz')['rows']if x['uid']==UID);rt=HERE/'local'/PRIOR.name/'runtime-geometry.json.gz';g=next(x for x in read(rt)['rows']if x['uid']==UID);t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert len(t)==11517
 b=row['source']['building'];target=Polygon(b['rings'][0],b['rings'][1:]);level=b['base'];polys=shapely.polygons(t[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;outside=shapely.difference(polys[valid],target);validids=np.flatnonzero(valid);excessids=validids[shapely.area(outside)>1e-10]
 strata={'entirelyBelowTowerBase':t[:,:,1].max(axis=1)<=level,'entirelyAboveTowerBase':t[:,:,1].min(axis=1)>=level,'crossesTowerBase':(t[:,:,1].min(axis=1)<level)&(t[:,:,1].max(axis=1)>level)}
 output=[]
 for name,mask in strata.items():
  ids=np.flatnonzero(mask&valid);projection=shapely.union_all(polys[ids]);excess=projection.difference(target);coords=shapely.get_coordinates(excess);distance=float(shapely.distance(shapely.points(coords),target).max())if len(coords)else 0
  output.append(dict(stratum=name,sourceFaceCount=int(mask.sum()),projectedAreaM2=float(projection.area),excessAreaM2=float(excess.area),maximumExcessDistanceM=distance,excessSourceFaces=[int(i)for i in excessids if mask[i]]))
 save(DOC/'extent.json.gz',dict(uid=UID,sourceSHA256=row['sourceSHA256'],towerBaseM=level,rows=output,rawIdentity=next(x['identity']for x in read(PRIOR/'context.json.gz')['rows']if x['uid']==UID),qualification='Height groups describe unchanged source facets; thresholds are the recorded tower base, not modified identity tolerances. Cross-level faces retained separately. No source role or installation approval.'))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.collections import PolyCollection
 fig,ax=plt.subplots(figsize=(9,9),dpi=150)
 for name,color in [('entirelyBelowTowerBase','#2d83b5'),('entirelyAboveTowerBase','#ed9334'),('crossesTowerBase','#9352a6')]:
  ids=np.flatnonzero(strata[name]&valid);ax.add_collection(PolyCollection(t[ids][:,:,[0,2]],facecolor=color,edgecolor='none',alpha=.2,label=name))
 for ring in [target.exterior,*target.interiors]:x,y=ring.xy;ax.plot(x,y,'k-',linewidth=1)
 ax.autoscale();ax.set_aspect('equal');ax.invert_yaxis();ax.legend();ax.set_title('Orchards Tower2 original source projection / recorded tower footprint');fig.tight_layout();DOC.mkdir(exist_ok=True);fig.savefig(DOC/'source-height-projection.png');plt.close(fig)
 refs=[Path(__file__),PRIOR/'result.json',PRIOR/'selection.json.gz',PRIOR/'context.json.gz',rt]
 result=module('orchards_extent_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'orchards-original-whole-source-height-extent-v1',refs,dict(uids=[UID],sourceSHA256=row['sourceSHA256'],summary=[{k:v for k,v in x.items()if k!='excessSourceFaces'}for x in output],fullAcceptance=False,nextStep='Use exact excess facet heights and source identity to determine whether lower attached geometry explains the extent; retain raw identity failure and all physical requirements.'))
 print(dict(jobId=result['jobId'],summary=result['summary']),flush=True)
if __name__=='__main__':main()
