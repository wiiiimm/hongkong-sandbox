"""Bound one reviewed original elevated service component; retain all other gates.

This is a source identity interpretation, not geometry modelling or a general
extent allowance. The component's precise mechanical function is not asserted.
"""
from pathlib import Path
import copy
import json
import uuid
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files

UID='landsd/127037:0'
SHA='36af6c014ae69e699d5346b6700b8fe58944d3d16123f71f5bcbe5d0d7b60e43'
WORLD='5febbb3b2bb34cbb9010ff6a6d3d7af73469c47dd4d20218bc75c9b772f7283f'
FAR=[4267,4268,4269,4270,10670,10671,15800,15801,15802,15803,15820,15821,15822,15823,15824,15825,17930,17931]
EXTENT={'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent'}
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-stonecutters-current-identity-v1-20261021'
DOC=BASE/BATCH
LOCAL=HERE/'local'/BATCH

def polygon(rings):
 out=shapely.GeometryCollection()
 for ring in rings:out=out.symmetric_difference(shapely.Polygon(ring))
 assert out.is_valid
 return out

def main():
 assert not DOC.exists() and not LOCAL.exists()
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'],claim
 lease=claim['reservation'];refs=[Path(__file__)];consumed={}
 try:
  def take(batch,file):
   folder=BASE/batch;_,pins=authenticate(folder);path=folder/file;key=str(path.relative_to(ROOT));assert digest(path.read_bytes())==pins[key];consumed[key]=pins[key];refs.extend([folder/'result.json',path]);return read(path)
  row=take('government-xl-stonecutters-current-runtime-v1-20261021','selection.json.gz')['rows'][0]
  component=take('government-xl-stonecutters-far-components-v1-20261021','components.json')
  provider=take('government-xl-stonecutters-primary-record-v1-20261021','primary-response.json')
  extent=take('government-xl-stonecutters-primary-extent-context-v1-20261021','summary.json')
  assert row['uid']==UID and row['modelId']=='B324952061001063C0' and row['sourceSHA256']==SHA
  asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==SHA;refs.append(asset)
  tri=decode_original_world_triangles(raw);assert tri.shape==(19436,3,3) and digest(tri.astype('<f8').tobytes())==WORLD
  assert component['sourceSHA256']==SHA and component['worldTrianglesSHA256']==WORLD
  assert len(component['components'])==1 and component['components'][0]['faces']==350 and component['components'][0]['farFaceIds']==FAR
  # Fresh identity replay preserves every original graph/route/coverage gate.
  final=module('stone_current_identity_context',HERE/'xl-final-script-pass.py')
  lo,hi=tri.min((0,1)),tri.max((0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])
  form,_,tile=next(x for x in forms if x[0]['uid']==UID)
  assert form==row['source']['building']
  current={url:digest((ROOT/'3d-viewer'/url).read_bytes()) for _,_,url in forms}
  context=dict(uid=UID,sourceSHA256=SHA,identity=final.identity_context(row,tri,forms),neighbourTileHashes=current)
  previous=verify_files(row,context,LOCAL/'raw-identity')
  assert previous['originalOwnership']['sourceGraphVerified']
  assert set(previous['reasons'])==EXTENT, previous['reasons']
  assert previous['worldTrianglesSHA256']==WORLD
  official=provider['features'][0];a=official['attributes']
  assert len(provider['features'])==1 and not provider.get('exceededTransferLimit')
  assert (a['Status'],a['BuildingCSUID'],a['BuildingID'])==('Active','3249520610T20160623',1810152333)
  primary=polygon([[(x-834500,816500-y)for x,y in ring]for ring in official['geometry']['rings']])
  projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))
  foreign=shapely.union_all([polygon(b['rings'])for b,_,_ in forms if b['uid']!=UID])
  checks={}
  for name,target in [('primary',primary),('current',polygon(form['rings']))]:
   distances=shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),target).reshape(-1,3)
   ids=np.flatnonzero(distances.max(1)>10).tolist();assert ids==FAR
   mask=np.ones(len(tri),bool);mask[FAR]=False
   values=dict(coverage=float(target.intersection(projection).area/target.area),maximumExtentM=float(distances.max()),otherMaximumExtentM=float(distances[mask].max()),foreignExcessM2=float(projection.difference(target).intersection(foreign).area))
   assert values['coverage']>=.95 and values['otherMaximumExtentM']<=10 and values['foreignExcessM2']<=1
   assert values['maximumExtentM']==extent['checks'][name]['maximumExtentM']
   checks[name]=values
  # Explicit agent interpretation of exact source views, not a claimed photo match.
  review=dict(reviewedBy='Codex ROOT',sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,
   decision='Retain the exact source-authored elevated linear service assembly as part of this single matched government asset.',
   basis='ROOT inspected the plan/elevations and all four exact component views. The 18 outlying facets form the continuation of one narrow 350-face elevated assembly, not a second building mass. Exact named source graph, unique CSUID/BuildingID, primary/current 99% footprint coverage, and zero foreign footprint excess support the source identity.',
   uncertainty='Exact mechanical function is not named; DSD equipment photos provide facility context only, not a surveyed match of these exact facets.',
   limits='Only these exact 18 facets and immutable source/world hashes. No source edits, target removal, general distance increase, contact exemption or installation approval.')
  for batch,file in [('government-xl-stonecutters-component-views-v1-20261021','component-context.png'),('government-xl-stonecutters-component-shape-v1-20261021','component-3d.png')]:
   folder=BASE/batch;_,ps=authenticate(folder);path=folder/file;key=str(path.relative_to(ROOT));assert digest(path.read_bytes())==ps[key];consumed[key]=ps[key];refs.extend([folder/'result.json',path])
  out=copy.deepcopy(previous);out.update(policy='one-exact-stonecutters-elevated-service-extent-v1',passed=True,reasons=[],rawExtentReasonsRetained=sorted(EXTENT),rawIdentity=previous,sourceSpecificFaceIds=FAR,independentCurrentPrimaryChecks=checks,review=review,proof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},installationApproved=False,physicalAccepted=False,sourceGeometryChanges=0)
  save(DOC/'identity-proof.json',out);save(DOC/'context.json.gz',context);save(DOC/'selection.json.gz',dict(rows=[row]));save(DOC/'review.json',review)
  for key,h in consumed.items():assert digest((ROOT/key).read_bytes())==h,key
  for key,h in current.items():assert digest((ROOT/'3d-viewer'/key).read_bytes())==h;refs.append(ROOT/'3d-viewer'/key)
  assert reservations.owns(lease)
  refs.extend([HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'routed_original_cell_identity.py',HERE/'government_georef_cell_identity.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-final-script-pass.py'])
  module('stone_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-reviewed-elevated-service-extent',list(dict.fromkeys(refs)),dict(uids=[UID],identityAccepted=True,sourceIdentityReviewUsedAI=True,sourceGeometryChanges=0,installationApproved=False,nextStep='Complete original support/runtime/neighbour/seam/visual/publication gates independently.'))
  print(dict(uid=UID,identityAccepted=True,checks=checks),flush=True)
 finally:
  assert reservations.release(lease)['ok']
if __name__=='__main__':main()
