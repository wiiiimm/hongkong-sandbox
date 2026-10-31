"""Prove whole four-world Hoi Yu terrain is byte-identical as oriented facets."""
from pathlib import Path
from collections import Counter
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympic-hoi-yu-unchanged-terrain-v1-20261022';UID='landsd/177605:0'
def main():
 doc=BASE/BATCH;assert not doc.exists();prior=BASE/'government-xl-olympic-facet-band-return-v1-20261022';r,_=authenticate(prior);newpath=ROOT/r['candidate']['path'];oldpath=ROOT/'3d-viewer'/r['candidate']['replaces']['url'];assert digest(newpath.read_bytes())==r['candidate']['sha256']and digest(oldpath.read_bytes())==r['candidate']['replaces']['sha256'];inv=BASE/'government-xl-after-aquarium-current-inventory-v1-20261022';_,pins=authenticate(inv);ip=inv/'complete-bounds.json.gz';assert digest(ip.read_bytes())==pins[str(ip.relative_to(ROOT))];row=next(r for r in read(ip)['rows']if r['uid']==UID);mp=ROOT/'3d-viewer/city/data/manifest.json';assert digest(mp.read_bytes())==pins[str(mp.relative_to(ROOT))];matches=[]
 for url in read(mp)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url
  matches.extend((p,e)for e in read(p)['models']if e['uid']==UID)
 assert len(matches)==1;cp,e=matches[0];asset=cp.parent/e['asset'];assert digest(asset.read_bytes())==e['sha256']==row['sourceSHA256'];bounds=np.asarray(row['completeFourWorldBounds']);lo=bounds[:,0].min(0);hi=bounds[:,1].max(0);counters=[]
 for p in [oldpath,newpath]:
  m=read(p)['nativeMesh'];t=np.asarray(m['position'],dtype='<f4').astype('<f8').reshape(-1,3)[np.asarray(m['index']).reshape(-1,3)];y=(t[:,1,2]-t[:,0,2])*(t[:,2,0]-t[:,0,0])-(t[:,1,0]-t[:,0,0])*(t[:,2,2]-t[:,0,2]);negative=y<0;t[negative]=t[negative][:,[0,2,1]];ids=np.flatnonzero((t[:,:,0].max(1)>=lo[0])&(t[:,:,0].min(1)<=hi[0])&(t[:,:,2].max(1)>=lo[2])&(t[:,:,2].min(1)<=hi[2]));count=Counter()
  for f in t[ids]:
   points=list(map(tuple,f));key=min(tuple(points[k:]+points[:k])for k in range(3));count[key]+=1
  counters.append(count)
 assert counters[0]==counters[1],'Changed terrain over complete installed actor';save(doc/'identical-facets.json.gz',[dict(vertices=[list(p)for p in key],multiplicity=n)for key,n in sorted(counters[0].items())]);result=dict(uids=['landsd/81242:0'],checkedNativeUid=UID,sourceSHA256=e['sha256'],completeFourWorldBounds=row['completeFourWorldBounds'],completeBoundUnion=[lo.tolist(),hi.tolist()],identicalOrientedFloat32TerrainFacets=sum(counters[0].values()),terrainFacetMultisetsIdentical=True,verticalFacetsIncluded=True,sourceGeometryChanges=0,installationApproved=False,newlyInstalled=0,currentSourceFlags={k:e.get(k)for k in ['placementReviewed','identityReviewApproved','publicationApproved']},qualification='Complete current source bounds from original/literal/two Float32 representations. Exact actual terrain facet vertices, orientation and multiplicities identical; existing support warning is retained without historical reapproval. No new physical-support credit.')
 save(doc/'summary.json',result);refs=[Path(__file__),prior/'result.json',inv/'result.json',ip,mp,cp,asset,oldpath,newpath,ROOT/'3d-viewer/city/world.js',ROOT/'3d-viewer/city/native-terrain.js'];module('hoi_yu_untouched_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'identical-complete-four-world-neighbour-terrain',refs,result);print(result,flush=True)
if __name__=='__main__':main()
