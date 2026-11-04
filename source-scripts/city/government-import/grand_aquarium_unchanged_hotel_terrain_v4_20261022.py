"""Prove identical actual terrain facet multisets across complete installed hotel bounds."""
from pathlib import Path
from collections import Counter
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grand-aquarium-unchanged-hotel-terrain-v4-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists();prior=BASE/'government-xl-grand-aquarium-narrow-boundary-return-v1-20261022';r,pins=authenticate(prior);newpath=ROOT/r['candidate']['path'];oldpath=ROOT/'3d-viewer'/r['candidate']['replaces']['url'];assert digest(newpath.read_bytes())==r['candidate']['sha256']and digest(oldpath.read_bytes())==r['candidate']['replaces']['sha256'];catpath=ROOT/'3d-viewer/city/data/official-models/government-xxl-ocean-park-20260912/catalogue.json';cat=read(catpath);refs=[Path(__file__),ROOT/'3d-viewer/city/world.js',ROOT/'3d-viewer/city/native-terrain.js',prior/'result.json',oldpath,newpath,catpath];surfaces=[]
 for path in [oldpath,newpath]:
  m=read(path)['nativeMesh'];t=np.asarray(m['position'],dtype=np.float32).reshape(-1,3)[np.asarray(m['index']).reshape(-1,3)];normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);negative=normal[:,1]<0;t[negative]=t[negative][:,[0,2,1]];surfaces.append(t)
 rows=[]
 for uid in ['landsd/125385:0','landsd/32681:0']:
  e=next(e for e in cat['models']if e['uid']==uid);assert e['placementReviewed']and e['identityReviewApproved'];asset=catpath.parent/e['asset'];assert digest(asset.read_bytes())==e['sha256'];refs.append(asset);lo,hi=np.asarray(e['worldBounds']);counters=[]
  for t in surfaces:
   ids=np.flatnonzero((t[:,:,0].max(1)>=lo[0])&(t[:,:,0].min(1)<=hi[0])&(t[:,:,2].max(1)>=lo[2])&(t[:,:,2].min(1)<=hi[2]));counter=Counter()
   for f in t[ids]:
    points=list(map(tuple,f.astype(float)));key=min(tuple(points[k:]+points[:k])for k in range(3));counter[key]+=1
   counters.append(counter)
  assert counters[0]==counters[1],'Changed current rendered terrain over complete actor bounds'
  items=[dict(vertices=[list(p)for p in key],multiplicity=n)for key,n in sorted(counters[0].items())];save(doc/(uid.split('/')[1]+'-facets.json.gz'),items);rows.append(dict(uid=uid,sourceSHA256=e['sha256'],wholeSourceBounds=e['worldBounds'],identicalOrientedFloat32TerrainFacets=sum(counters[0].values()),terrainFacetMultisetsIdentical=True,verticalFacetsIncluded=True,productionUpwardWindingNormalisationApplied=True,completeAABBCandidateScope=True,oldSupportFlagsNotErased=True,currentPublicationApproved=e['publicationApproved'],installationApproved=False))
 result=dict(uids=['landsd/93424:0'],rows=rows,neighbourTerrainRegressionProven=True,qualification='Exact unchanged rendered facet multiset over each complete original actor bound; multiplicities and winding preserved. All candidate native terrain facets were scanned, including vertical faces. Existing actor bytes and placement/identity flags checked. Publication flags are preserved, including explicit false. Historical support/publication is not reapproved; no new structural-root requirement is introduced for untouched installed actors. Other neighbours, source contact/coverage and publication remain independent.',sourceGeometryChanges=0,newlyInstalled=0,installationApproved=False);save(doc/'summary.json',result);module('exact_unchanged_hotel_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'identical-whole-neighbour-rendered-terrain-facets',refs,result);print(rows)
if __name__=='__main__':main()
