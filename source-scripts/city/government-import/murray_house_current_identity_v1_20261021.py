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

UID='landsd/61216:0'
SHA='b1b1d58399a067cfdc3b3bea06ef42be8e67527c3f98e65e955aba9120993f97'
WORLD='a6d9a4deedad4fce26d6b807e4f9c9640e78a66eec5243d5c6488c89f4b150ba'
FAR=[4128, 4129, 4130, 4131, 4140, 4141, 4146, 4147, 4148, 4149, 4150, 4151, 7267, 7268, 7269, 7270, 7271, 7272, 7273, 7274, 7275, 7348, 7349, 7350, 7351, 7386, 7387, 7388, 7389, 7390, 7492, 7493, 7494, 7495, 7496, 7501, 7502, 7503, 7504, 7505, 7506, 7507, 7532, 7533, 7534, 7535, 7536, 7537, 7538, 7539, 7540, 7565, 7566, 7567, 7568, 7576, 7577, 7578, 7579, 7580, 7581, 7582, 7583, 7584, 7585, 7586, 7587, 7588, 7589, 7590, 7591, 7592, 7593, 7595, 7596, 7597, 7598, 7599, 7600, 7601, 7602, 7603, 7604, 7605, 7606, 7607, 7608, 7609, 7610, 7611, 7612, 7613, 7614, 7615, 7616, 7634, 7635, 7636, 7637, 7638, 9270, 9271, 9272, 9273, 9274, 9275, 9310, 9311, 9312, 9313, 9314, 9315, 9336, 9337, 9338, 9339, 9340, 9341, 9342, 9343, 9344, 9345, 9346, 9347, 9348, 9349, 9350, 9351, 9352, 9353, 11053, 11054, 11055, 11056, 11064, 11065, 11066, 11067, 11068, 11069, 11070, 11072, 11073, 13706, 13707, 13708, 13709, 13710, 13711, 13712, 13713, 13714, 13715, 13716, 13717, 13718, 13719, 13720, 13721, 13722, 13723, 13724, 13725, 13726, 13727, 13736, 13737, 13738, 13739, 13740, 13872, 13873, 13874, 13875, 13876, 13877, 13878, 13879, 13880, 13881, 13882, 13883, 13884, 13885, 13886, 13887, 13888, 13889, 13890, 13891, 13892, 13893, 13894, 13895, 13896, 13897, 13898, 13899, 13900, 13901, 13902, 13903, 13904, 13905, 13906, 13907, 13908, 13909, 13910, 13911, 13912, 13913, 13914, 13915, 13916, 13917, 13918, 13919, 13920, 13921, 13922, 13923, 13924, 13925, 13926, 13927, 13928, 13929, 13930, 13931, 13932, 13933, 13934, 13935, 13936, 13937, 13938, 13939, 13940, 13941, 13942, 13943, 13944, 13945, 13946, 13947, 13948, 13949, 13950, 13951, 13952, 13953, 13954, 13955, 13956, 13957, 13958, 13959, 13960, 13961, 13962, 13963, 13964, 13965, 13966, 13967, 13968, 13969, 13970, 13971, 13972, 13973, 13974, 13975, 13976, 13977, 13978, 13979, 13980, 13981, 13982, 13983, 13984, 13985, 13986, 13987, 13988, 13989, 13990, 13991, 13992, 13993, 13994, 13995, 13996, 13997, 13998, 13999, 14000, 14001, 14002, 14003, 14004, 14005, 14006, 14007, 14008, 14009, 14010, 14011, 14012, 14013, 14014, 14015, 14016, 14017, 14018, 14019, 14020, 14021, 14022, 14023, 14024, 14025, 14026, 14027, 14028, 14029, 14030, 14031, 14032, 14033, 14034, 14035, 14036, 14037, 14038, 14039, 14136, 14137, 14138, 14139, 14140, 14141, 14142, 14143, 14144, 14145, 14146, 14147, 14148, 14149, 14150, 14151, 14152, 16231, 16232, 16235, 16236, 16239, 16240, 18664, 18665, 18666, 18667, 18668, 18669]
EXTENT={'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent'}
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-murray-house-current-identity-v1-20261021'
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
  row=take('government-xl-murray-current-runtime-v1-20261021','selection.json.gz')['rows'][0]
  component=take('government-xl-murray-house-far-components-v1-20261021','components.json')
  provider=take('government-xl-murray-house-primary-record-v1-20261021','primary-response.json')
  extent=take('government-xl-murray-house-primary-extent-context-v1-20261021','summary.json')
  assert row['uid']==UID and row['modelId']=='B396560883001063C0' and row['sourceSHA256']==SHA
  asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==SHA;refs.append(asset)
  tri=decode_original_world_triangles(raw);assert tri.shape==(19310,3,3) and digest(tri.astype('<f8').tobytes())==WORLD
  assert component['sourceSHA256']==SHA and component['worldTrianglesSHA256']==WORLD
  assert len(component['components'])==27 and sorted(i for group in component['components'] for i in group['farFaceIds'])==FAR
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
  assert (a['Status'],a['BuildingCSUID'],a['BuildingID'])==('Active','3965608830T20050430',1109347787)
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
   decision='Retain the exact authored walkway, posts and exterior projections within this matched Murray House government asset.',
   basis='ROOT inspected component-context.png plan and both elevations. Outlying facets form the low covered approach with repeated slender posts and local exterior projections; no separate occupied building mass is evident. Exact named source graph, unique CSUID/BuildingID, full primary/current footprint coverage and zero foreign footprint excess independently bind this single source.',
   uncertainty='Walkway and exterior projections describe visible morphology; no surveyed photographic match or structural engineering certification is asserted.',
   limits='Only the 367 enumerated source facets and exact source/world hashes; no geometry edits, general threshold change, contact exemption or installation approval.')
  for batch,file in [('government-xl-murray-house-component-views-v1-20261021','component-context.png')]:
   folder=BASE/batch;_,ps=authenticate(folder);path=folder/file;key=str(path.relative_to(ROOT));assert digest(path.read_bytes())==ps[key];consumed[key]=ps[key];refs.extend([folder/'result.json',path])
  out=copy.deepcopy(previous);out.update(policy='one-exact-murray-house-elevated-service-extent-v1',passed=True,reasons=[],rawExtentReasonsRetained=sorted(EXTENT),rawIdentity=previous,sourceSpecificFaceIds=FAR,independentCurrentPrimaryChecks=checks,review=review,proof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},installationApproved=False,physicalAccepted=False,sourceGeometryChanges=0)
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
