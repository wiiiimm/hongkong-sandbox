"""Record full pair contact orientation and horizontal-area facts; no approval."""
import argparse
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from shapely.geometry import Polygon,Point
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

def horizontal_area(contact):
 points=sorted(set((F(q[0]),F(q[2]))for q in contact['exactPoints']))
 def cross(o,a,b):return(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lo=[];hi=[]
 for q in points:
  while len(lo)>=2 and cross(lo[-2],lo[-1],q)<=0:lo.pop()
  lo.append(q)
 for q in reversed(points):
  while len(hi)>=2 and cross(hi[-2],hi[-1],q)<=0:hi.pop()
  hi.append(q)
 hull=lo[:-1]+hi[:-1];assert len(hull)>=3
 return abs(sum(hull[i][0]*hull[(i+1)%len(hull)][1]-hull[(i+1)%len(hull)][0]*hull[i][1]for i in range(len(hull))))/2

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ['batch','contacts','runtime','attributes','uid','native']:p.add_argument('--'+key,required=True)
 a=p.parse_args();assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.contacts,a.runtime,a.attributes])
 base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
  path=base/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selected=take(a.runtime,'selection.json.gz');source=next(r for r in selected['rows']if r['uid']==a.uid)
 attrs=next(r for r in take(a.attributes,'attributes.json.gz')['rows']if r['uid']==a.uid)
 native=next(r for r in take(a.contacts,'native-input.json.gz')['rows']if r['uid']==a.native)
 nattrs=next(r for r in take(a.contacts,'native-attributes.json.gz')['rows']if r['uid']==a.native)
 forms={f['uid']:f for f in take(a.contacts,'exact-current-form-bindings.json.gz')['rows']}
 polys=[Polygon(forms[uid]['rings'][0],forms[uid]['rings'][1:])for uid in [a.uid,a.native]]
 worlds={}
 for uid,asset,sha,attr in [(a.uid,ROOT/source['candidate']['path'],source['sourceSHA256'],attrs),(a.native,ROOT/native['path'],native['entry']['sha256'],nattrs)]:
  assert digest(asset.read_bytes())==sha==attr['sourceSHA256'];refs.append(asset)
  worlds[uid]={'original':decode_original_world_triangles(asset.read_bytes())}
  index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
  for name,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[uid][name]=np.asarray(attr[field]).reshape(-1,3)[index]
 rows=[]
 for mode in ['original','literal','leftF32','balancedF32']:
  report=take(a.contacts,a.uid.split('/')[1]+'--'+a.native.split('/')[1]+'--'+mode+'.json.gz');assert report['allPairsExamined']and report['sourceFacesOmitted']==0
  contacts=report['contacts'];t,u=worlds[a.uid][mode],worlds[a.native][mode];pairs=[];areas=[];points=[]
  for c in contacts:
   v=t[c['sourceFaceA']];w=u[c['sourceFaceB']];n=np.cross(v[1]-v[0],v[2]-v[0]);m=np.cross(w[1]-w[0],w[2]-w[0])
   detail=dict(sourceFace=c['sourceFaceA'],nativeFace=c['sourceFaceB'],dimension=c['dimension'],bounds=c['bounds'],sourceHorizontal=bool(np.all(v[:,1]==v[0,1])),nativeHorizontal=bool(np.all(w[:,1]==w[0,1])),sourceSignedNormalY=float(n[1]/np.linalg.norm(n))if np.linalg.norm(n)else None,nativeSignedNormalY=float(m[1]/np.linalg.norm(m))if np.linalg.norm(m)else None)
   if c['dimension']==2:
    assert detail['sourceHorizontal']and detail['nativeHorizontal']and c['bounds'][0][1]==c['bounds'][1][1]
    area=horizontal_area(c);areas.append(area);detail['exactHorizontalAreaM2']=str(area)
   pairs.append(detail);points.extend(Point(float(F(q[0])),float(F(q[2])))for q in c['exactPoints'])
  result=dict(mode=mode,sourceFaces=len(t),nativeFaces=len(u),finiteContactPairs=len(contacts),pointPairs=sum(c['dimension']==0 for c in contacts),linePairs=sum(c['dimension']==1 for c in contacts),horizontalAreaPairs=len(areas),sumHorizontalPairAreaM2=float(sum(areas)),exactSumHorizontalPairAreaM2=str(sum(areas)),maximumHorizontalPairAreaM2=float(max(areas,default=0)),areaContactYLevels=sorted({c['bounds'][0][1]for c in contacts if c['dimension']==2}),contactHeightRangeM=[min(c['bounds'][0][1]for c in contacts),max(c['bounds'][1][1]for c in contacts)],maximumContactDistanceToEachFootprintBoundaryM=[max(q.distance(poly.boundary)for q in points)for poly in polys])
  save(out/(mode+'.json.gz'),dict(**result,pairs=pairs));rows.append(result);print(result,flush=True)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256']==pins[a.contacts][str(manifest.relative_to(ROOT))];refs.append(manifest)
 result=dict(uids=[a.uid],nativeUid=a.native,sourceSHA256=source['sourceSHA256'],nativeSHA256=native['entry']['sha256'],rows=rows,currentFootprintOverlapM2=polys[0].intersection(polys[1]).area,currentFootprintDistanceM=polys[0].distance(polys[1]),sourceGeometryChanges=0,nativeMetadataChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Complete exact-contact dimensionality, source/native face orientation and exact rational horizontal contact polygon area sums. Pair-area sum is not a union area; overlapping contact polygons may be counted more than once. Footprint distances are diagnostic double-precision values. No architectural function, absence of interpenetration, identity, support or publication approval inferred.')
 save(out/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py')
 module('original_pair_contact_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-original-pair-horizontal-contact-orientation-context',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
