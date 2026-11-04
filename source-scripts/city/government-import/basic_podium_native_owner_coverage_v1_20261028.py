"""Bind the private BASIC footing to the exact local native terrain owner.

Every contributing drawn facet must match an unchanged owner facet bit-for-bit
in the production Float32 coordinates. This is not collision/visual approval.
"""
import argparse,sys,uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
sys.path.insert(0,str(HERE.parent/'island-detail-integration'))
from basic_podium_footings import terrain_geometry_sha
BASE=ROOT/'docs/astra-city/government-import';RUNTIME='government-xl-elegant-garden-sixteen-original-updated-runtime-v1-20261028';PATCH='government-xl-elegant-garden-sixteen-original-two-member-partition-v1-20261028';PROPOSAL='government-xl-elegant-garden-unnamed-basic-podium-footing-v1-20261028'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
 assert a.batch.startswith('government-xl-')and '/'not in a.batch
 out=BASE/a.batch;local=HERE/'local'/a.batch;lp=local/'reservation.json';assert not out.exists()
 rp=BASE/'government-xl-elegant-garden-sixteen-original-updated-terrain-plan-v1-20261028.json';resources=set(read(rp)['resources'])
 if not a.owned:
  assert not local.exists();claim=reservations.claim('basic-podium-native-coverage-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp];pins={}
 def take(batch,path):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 b=take(PROPOSAL,BASE/PROPOSAL/'input.json')['building'];proposal=take(PROPOSAL,BASE/PROPOSAL/'proposal.json');old=take(PROPOSAL,BASE/PROPOSAL/'continuous-ground.json.gz')
 assert b['uid']==proposal['uid']=='landsd/213586:0'
 polygon=shapely.Polygon(b['rings'][0],b['rings'][1:]);captured=take(RUNTIME,HERE/'local'/RUNTIME/'runtime-geometry.json.gz')['rows']
 ground=np.unique(np.concatenate([np.asarray(r['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)for r in captured]),axis=0)
 assert digest(ground.tobytes())==old['completeDrawnGroundSHA256']
 shapes=shapely.polygons(ground[:,:,[0,2]]);ids=np.flatnonzero((shapely.area(shapes)>1e-10)&shapely.intersects(shapes,polygon))
 ids=[int(i)for i in ids if shapes[i].intersection(polygon).area>1e-10];assert ids
 def key(t):return tuple(sorted(tuple(float(v)for v in p)for p in t))
 owners={};parts={};dependencies=[]
 patchreceipt=take(PATCH,BASE/PATCH/'result.json')
 for member in patchreceipt['members']:
  path=ROOT/member['candidate']['path'];patch=take(PATCH,path)
  tri=np.asarray(patch['nativeMesh']['position'],dtype='<f4').astype('<f8').reshape(-1,3)[np.asarray(patch['nativeMesh']['index']).reshape(-1,3)]
  parts[member['member']]=tri
  for i,t in enumerate(tri):owners.setdefault(key(t),[]).append(dict(member=member['member'],ownerFace=i))
  dependencies.append(dict(member=member['member'],sourcePath=str(path.relative_to(ROOT)),sourceSHA256=digest(path.read_bytes()),geometrySHA256=terrain_geometry_sha(patch),plannedDestination='city/data/government-xl-elegant-garden-'+member['member']+'-original-v1-20261028.json'))
 mapped=[];missing=[]
 for i in ids:
  hits=owners.get(key(ground[i]),[])
  if hits:mapped.append(dict(drawnFace=i,owners=hits))
  else:missing.append(i)
 used={p['member']for r in mapped for p in r['owners']}
 nativepolys=shapely.polygons(np.concatenate([parts[m]for m in sorted(used)])[:,:,[0,2]])if used else []
 nativecoverage=shapely.union_all(nativepolys);uncovered=polygon.difference(nativecoverage).area
 matched=not missing and uncovered<1e-8
 result=dict(uids=[b['uid']],uid=b['uid'],status='private-native-terrain-owner-coverage',drawnPositiveAreaFaces=len(ids),bitExactMatchedFaces=len(mapped),missingDrawnFaces=missing,
  nativeCoverageUncoveredAreaM2=uncovered,nativeCoverageMatchesActualDrawnGround=matched,ownerDependencies=[d for d in dependencies if d['member']in used],
  sourceGeometryChanges=0,governmentGeometryChanges=0,collisionReviewApproved=False,visualReviewApproved=False,installationApproved=False,
  qualification='Every positive-area actual drawn footprint facet is checked against complete unchanged coordinated native terrain facets converted through the existing Float32 representation, without clipping/welding or surface tolerance credit. Complete native projected coverage is separately measured. Dependencies are draft source/destination bindings only; the real footing still requires collision/visual acceptance and a qualified publication review. No native/BASIC mesh, pose, source height or terrain changed.')
 save(out/'face-owner-map.json',mapped);save(out/'summary.json',result);refs.append(HERE.parent/'island-detail-integration/basic_podium_footings.py')
 assert reservations.owns(lease)
 module('basic_podium_owner_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-private-basic-podium-local-native-terrain-coverage',list(dict.fromkeys(refs)),result)
 print(dict(matched=matched,drawnFaces=len(ids),missingFaces=len(missing),uncoveredAreaM2=uncovered,owners=sorted(used)),flush=True)
if __name__=='__main__':main()
