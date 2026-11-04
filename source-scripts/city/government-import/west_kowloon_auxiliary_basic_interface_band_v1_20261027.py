"""Measure complete mixed contacts against finite authored interfaces, without a tolerance."""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import math
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def point(raw):
 assert len(raw)==3 and all(isinstance(x,(str,int,F))and not isinstance(x,bool)for x in raw)
 return tuple(F(x)for x in raw)


def distance_squared(p,a,b):
 p,a,b=map(point,(p,a,b));direction=tuple(y-x for x,y in zip(a,b));length=sum(x*x for x in direction);assert length>0
 parameter=sum((x-y)*z for x,y,z in zip(p,a,direction))/length
 parameter=max(F(0),min(F(1),parameter))
 closest=tuple(x+parameter*y for x,y in zip(a,direction))
 return sum((x-y)**2 for x,y in zip(p,closest)),parameter


def finite_host_bound(contact,hosts):
 vertices=[point(p)for p in contact['exactPoints']];assert vertices
 choices=[]
 for index,host in hosts:
  points=[point(p)for p in host['exactPoints']]
  assert host['dimension']==1 and len(points)>=2
  a,b=max(combinations(points,2),key=lambda pair:sum((x-y)**2 for x,y in zip(*pair)))
  if a==b:continue
  distances=[distance_squared(p,a,b)for p in vertices]
  maximum=max(d for d,_ in distances)
  choices.append((maximum,index,a,b,distances))
 assert choices,'No positive finite original interface on the same source face'
 maximum,index,a,b,distances=min(choices,key=lambda r:(r[0],r[1]))
 return dict(authoredContactIndex=index,exactFiniteHostEndpoints=[[str(x)for x in p]for p in (a,b)],exactMaximumEndpointDistanceSquaredM2=str(maximum),vertexProofs=[dict(exactForeignContactVertex=list(map(str,p)),exactDistanceSquaredM2=str(d),exactClosestFiniteHostParameter=str(t))for p,(d,t)in zip(vertices,distances)],wholeContactConvexHullBoundedBySingleFiniteHostCapsule=True,thresholdApplied=False,installationApproved=False)


def main():
 batch='government-xl-west-kowloon-auxiliary-basic-interface-band-v1-20261027';base=ROOT/'docs/astra-city/government-import';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(name,file):
  if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
  path=base/name/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 prefix='government-xl-west-kowloon-north-pair-';pair_name=prefix+'original-contacts-v1-20261027';foreign_name=prefix+'foreign-contacts-v1-20261027';summary=take(pair_name,'summary.json');take(foreign_name,'summary.json')
 assert summary['uids']==['landsd/182397:0','landsd/309340:0'];rows=[]
 for mode in ('original','literal','leftF32','balancedF32'):
  authored=take(pair_name,mode+'.json.gz');mixed=take(foreign_name,'309340:0--182397:0--'+mode+'.json.gz')
  assert authored['allPairsExamined']and mixed['allPairsExamined']and authored['sourceFacesOmitted']==mixed['sourceFacesOmitted']==0
  results=[]
  for index,contact in enumerate(mixed['contacts']):
   if contact['dimension']<=0:continue
   hosts=[(j,c)for j,c in enumerate(authored['contacts'])if c['sourceFaceB']==contact['sourceFaceA']and c['dimension']==1 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
   proof=finite_host_bound(contact,hosts);results.append(dict(foreignContactIndex=index,sourceFace=contact['sourceFaceA'],**proof))
  assert len(results)==8
  maximum=max(F(r['exactMaximumEndpointDistanceSquaredM2'])for r in results)
  save(out/(mode+'.json'),dict(mode=mode,contacts=results,exactSquaredUpperDistanceBoundM2=str(maximum),entireMixedContactsExactlyOnAuthoredFiniteInterfaces=maximum==0,thresholdApplied=False,physicalAcceptance=False,installationApproved=False))
  rows.append(dict(mode=mode,mixedPositiveContacts=len(results),exactSquaredUpperDistanceBoundM2=str(maximum),approximateUpperDistanceBoundM=math.sqrt(float(maximum)),entireMixedContactsExactlyOnAuthoredFiniteInterfaces=maximum==0))
 result=dict(uids=['landsd/309340:0'],basicPeerUid='landsd/182397:0',sourceSHA256=summary['sourceSHA256ByUid']['landsd/309340:0'],sourceSHA256ByUid=summary['sourceSHA256ByUid'],rows=rows,thresholdApplied=False,sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Each entire mixed contact is bounded by one finite authored positive interface on the identical auxiliary source face. Exact endpoint-to-clamped-segment distances bound the convex contact hull using convexity of a finite segment capsule; no infinite-plane extrapolation, float coordinate round trip or arbitrary tolerance. Nonzero distance is NOT interface-equivalence or acceptance credit. All8 mixed contacts in every world retained.')
 save(out/'summary.json',result)
 module('west_kowloon_auxiliary_interface_band_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-finite-authored-interface-distance-for-complete-mixed-contacts',refs,result)
 print(rows,flush=True)

if __name__=='__main__':main()
