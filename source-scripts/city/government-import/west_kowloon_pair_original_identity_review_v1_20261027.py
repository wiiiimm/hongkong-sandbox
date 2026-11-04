"""Source-specific identity review of the two unchanged West Kowloon originals."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
EXPECTED={
 'landsd/182397:0':dict(buildingID=1810186242,csuid='3484119323T20190328',modelId='B348411932301063C0',sha256='f16aa7f57a9b89962a6e1f3183e4dea922c7dbcb173515e608deae1ddc4b48b1',faces=10322),
 'landsd/309340:0':dict(buildingID=1810186243,csuid='3481019326T20190328',modelId='B348101932601063C0',sha256='a8d145aaefe5aff04cd0f3d36b51ddf03baa951cb24d30504f0e9de272f12f0a',faces=338)}


def validate_primary(form,primary,expected):
 assert form['buildingCSUID']==primary['BuildingCSUID']==expected['csuid']
 assert primary['BuildingID']==expected['buildingID'] and primary['Status']=='Active'
 assert primary['GeoRefNo']==expected['modelId'][1:11]==form['buildingCSUID'][:10]
 assert primary['BuildingBlockType']==form['structureType']=='Tower'
 assert primary['BaseHeight']==form['baseHeightHKPD'] and primary['TopHeight']==form['topHeightHKPD']
 assert type(primary['OBJECTID'])is int and primary['OBJECTID']>0


def main():
 base=ROOT/'docs/astra-city/government-import';batch='government-xl-west-kowloon-north-pair-identity-review-v1-20261027';out=base/batch;assert not out.exists()
 refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py'];pins={}
 def take(name,path):
  if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
  assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 prefix='government-xl-west-kowloon-north-pair-';runtime=prefix+'current-runtime-v1-20261027';identity=prefix+'identity-v1-20261027';primary_name=prefix+'primary-records-v1-20261027'
 selected=take(runtime,base/runtime/'selection.json.gz')['rows'];assert {r['uid']for r in selected}==set(EXPECTED)
 primary=take(primary_name,base/primary_name/'footprints.json')['features'];assert len(primary)==2
 role=take('government-xl-west-kowloon-north-masked-landscape-role-review-v1-20261027',base/'government-xl-west-kowloon-north-masked-landscape-role-review-v1-20261027/ROOT-SOURCE-ROLE-REVIEW.json');assert role['sourceRoleAccepted'] and not role['physicalAcceptance']
 source_views=['government-xl-after-dragon-next-five-182397-source-plots-v1-20261026','government-xl-west-kowloon-auxiliary309340-source-views-v1-20261027'];images=[]
 for name in source_views:
  for filename in ('whole-source-plan.png','whole-source-perspectives.png'):
   if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
   path=base/name/filename;sha=digest(path.read_bytes());assert sha==pins[name][str(path.relative_to(ROOT))];refs.append(path);images.append(dict(path=str(path.relative_to(ROOT)),sha256=sha))
 rows=[]
 for row in selected:
  uid=row['uid'];expected=EXPECTED[uid];form=row['source']['building'];matches=[f for f in primary if f['attributes']['BuildingCSUID']==expected['csuid']];assert len(matches)==1;record=matches[0]['attributes'];validate_primary(form,record,expected)
  proof=take(identity,base/identity/uid.split('/')[1]/'identity.json');assert proof['originalOwnership']['sourceGraphVerified'] and proof['originalOwnership']['originalRootName']==expected['modelId']
  assert proof['exactCurrentComponentRoute']['qualified'] and proof['exactCurrentComponentRoute']['uid']==uid and proof['freshCurrentIdentity']['exactObjectAndCSUID']
  tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'];assert next(f for f in read(tile)['buildings']if f['uid']==uid)==form;refs.append(tile)
  asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==expected['sha256'];refs.append(asset)
  tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==expected['faces'] and digest(tri.astype('<f8').tobytes())==proof['worldTrianglesSHA256']
  native=row['native']
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY');sha,data=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(native['cacheKey'],)).fetchone();assert sha==native['resultSha'];assert next(m for m in data['models']if m['modelId']==expected['modelId'])==native['model']
  candidates=[c for c in native['model']['matching']['officialCandidates']if c['buildingCSUID']==form['buildingCSUID']and c['objectId']==form['objectId']];assert len(candidates)==1
  rows.append(dict(uid=uid,sourceSHA256=expected['sha256'],sourceWorldSHA256=proof['worldTrianglesSHA256'],modelId=expected['modelId'],buildingCSUID=expected['csuid'],stableBuildingID=expected['buildingID'],freshPrimaryObjectID=record['OBJECTID'],viewerObjectID=form['objectId'],identityAccepted=True,identityOnlyApproved=True,rawRoutedIdentityPassed=proof['passed'],rawReasons=proof['reasons'],rawCurrentSpatialIdentity=proof['freshCurrentIdentity'],rawGeoRefCell=proof['geographicCell'],rawExactWholeCellCoverage=proof['exactWholeCellCoverage'],physicalAcceptance=False,installationApproved=False,publication=False))
 result=dict(uids=list(EXPECTED),sourceSHA256ByUid={uid:e['sha256']for uid,e in EXPECTED.items()},rows=rows,identityAccepted=True,identityOnlyApproved=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,rootActuallyViewedSourceImages=images,qualification='Bounded identity interpretation for these two exact provider-owned original units only. Unique fresh Active primary BuildingID/CSUID/GeoRef/type/heights, immutable source graph and complete current routing are bound. North Tower source contains its authored forecourt in addition to the tower core; the338-face auxiliary is the complete unlabelled L-shaped unit as issued, not an invented complete-solid footprint. Its source and current footprint both fail the one-metre reference-cell coverage rule; that raw fact and70.1percent target projection coverage remain explicit. No source geometry, current footprint or raw diagnostics are changed, no alias/name added, and no placement, physical, support, terrain, runtime or publication approval transfers.')
 for row in rows:save(out/row['uid'].split('/')[1]/'ROOT-IDENTITY-REVIEW.json',dict(row,rootActuallyViewedSourceImages=images,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False))
 save(out/'summary.json',result)
 module('west_kowloon_pair_identity_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'bounded-exact-original-provider-unit-identity-review-only',refs,result)
 print(dict(identityAccepted=len(rows),physicalAcceptance=False),flush=True)

if __name__=='__main__':main()
