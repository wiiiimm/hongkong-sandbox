"""Bounded identity-only review of four unchanged official Ocean source units.

Accept stable published component identity, not whole-landmark completeness or
physical interfaces. Preserve every automatic projection failure and live
OBJECTID/footprint difference. No geometry or placement edits.
"""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
P='government-xl-after-waterfront-ocean-four-corrected-'
SOURCES={
 'landsd/234188:0':'9525abed0ad9c229351f3b8ac2f2847fa12541467851fa2902a47c2f0efc5275',
 'landsd/156599:0':'0c91d5079caf5faad9a5c39298d574250f6d35744175ceffc547f204ccab4156',
 'landsd/210743:0':'c3beec630e624668e79bec0de9254da02d7ec978795c1632a4f85955e624d719',
 'landsd/231469:0':'fa12965c13b5ffda4ac178e1aa162d8ecf516bf1c1aea951b0f1a0a3af8f006a'}
PERMITS={'landsd/234188:0':'K73/77','landsd/156599:0':'K73/77','landsd/210743:0':'K5/82','landsd/231469:0':'K16/70'}

def stable_identity(form,entry,attributes,model_id):
 assert entry['uid']==form['uid'] and entry['objectId']==form['objectId']
 assert entry['buildingCSUID']==form['buildingCSUID']==attributes['BuildingCSUID']
 assert form['buildingId']==attributes['BuildingID']
 assert model_id[1:11]==attributes['GeoRefNo']==form['buildingCSUID'][:10]
 assert attributes['Status']=='Active'
 assert attributes['BuildingBlockType']==form['structureType']
 assert attributes['BaseHeight']==form['baseHeightHKPD'] and abs(attributes['TopHeight']-form['topHeightHKPD'])<1e-9
 return dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True)

def main():
 base=ROOT/'docs/astra-city/government-import';batch=P+'identity-review-v1-20261027';out=base/batch;assert not out.exists()
 refs=[Path(__file__)];pins={}
 def take(name,file):
  if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
  path=base/name/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(P+'runtime-v1-20261027','selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
 primary=P+'primary-records-v1-20261027';footprints=take(primary,'footprints.json')['features'];relations=take(primary,'relations.json')['features'];structures=take(primary,'structures.json')['features'];assert len(footprints)==4
 visual=take(P+'original-visual-v1-20261027','summary.json');assert set(visual['uids'])==set(SOURCES) and len(visual['views'])==1
 image=visual['views'][0]['image'];image_path=ROOT/image['path'];assert digest(image_path.read_bytes())==image['sha256']==pins[P+'original-visual-v1-20261027'][image['path']];refs.append(image_path)
 rows=[]
 for selected in selection['rows']:
  uid=selected['uid'];form=selected['source']['building'];entry=selected['candidate']['entry'];asset=ROOT/selected['candidate']['path'];assert digest(asset.read_bytes())==SOURCES[uid];refs.append(asset)
  raw=take(P+'identity-v1-20261027',uid.split('/')[1]+'/identity.json')
  assert raw['sourceSHA256']==SOURCES[uid] and raw['uid']==uid
  assert raw['originalOwnership']['sourceGraphVerified'] and raw['originalOwnership']['originalRootName']==selected['modelId']
  assert raw['freshCurrentIdentity']['exactObjectAndCSUID'] and raw['exactCurrentComponentRoute']['qualified'] and raw['exactWholeCellCoverage']['covered']
  matches=[f for f in footprints if f['attributes']['BuildingCSUID']==form['buildingCSUID']];assert len(matches)==1;feature=matches[0];attributes=feature['attributes']
  matches=[v for v in selected['native']['model']['matching']['viewerMatches'] if v['uid']==uid and v.get('buildingCSUID')==form['buildingCSUID'] and v.get('objectId')==form['objectId']]
  assert len(matches)==1
  triangles=decode_original_world_triangles(asset.read_bytes());assert len(triangles)==selected['triangles'] and digest(triangles.astype('<f8').tobytes())==raw['worldTrianglesSHA256']
  proof=stable_identity(form,entry,attributes,selected['modelId'])
  links=[r['attributes']for r in relations if r['attributes']['BuildingCSUID']==form['buildingCSUID']];assert len(links)==1
  linked=[r['attributes']for r in structures if r['attributes']['BuildingStructureID']==links[0]['BuildingStructureID']];assert len(linked)==1 and linked[0]['OPNo']==PERMITS[uid]
  # Report fresh footprint drift independently of source mesh projection tests.
  geometry=shapely.GeometryCollection()
  for ring in feature['geometry']['rings']:
   geometry=geometry.symmetric_difference(shapely.Polygon([[v[0]-834500,816500-v[1]]for v in ring]))
  target=shapely.Polygon(form['rings'][0],form['rings'][1:]);assert geometry.is_valid and target.is_valid
  tile=ROOT/'3d-viewer'/selected['source']['tile'];assert digest(tile.read_bytes())==selected['source']['tileSHA256'];assert next(f for f in read(tile)['buildings'] if f['uid']==uid)==form;refs.append(tile)
  row=dict(uid=uid,modelId=selected['modelId'],sourceSHA256=SOURCES[uid],sourceFormSHA256=raw['sourceFormSHA256'],worldTrianglesSHA256=raw['worldTrianglesSHA256'],completeSourceFaces=selected['triangles'],identityProof=proof,rawIdentityVerbatim=raw,rawReasonsRetained=raw['reasons'],freshPrimaryFootprint=attributes,freshPrimaryGeometry=feature['geometry'],structureRelation=links[0],structure=linked[0],currentViewerObjectID=form['objectId'],currentServiceObjectID=attributes['OBJECTID'],serviceObjectIDChanged=attributes['OBJECTID']!=form['objectId'],primaryVersusViewerFootprintIoU=geometry.intersection(target).area/geometry.union(target).area,primaryVersusViewerDifferenceM2=geometry.symmetric_difference(target).area,identityOnlyApproved=True,identityReviewApproved=True)
  rows.append(row);save(out/uid.split('/')[1]/'ROOT-IDENTITY-REVIEW.json',row)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 result=dict(uids=list(SOURCES),sourceSHA256ByUid=SOURCES,rows=rows,currentManifestSHA256=selection['manifestSHA256'],identityAccepted=True,sourceSpecificIdentityReviewAccepted=True,rawFailuresPreserved=True,sourceDiagnosticActuallyViewedByRoot=True,sourceDiagnosticImage=image,identityOnlyApproved=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='ROOT accepts only exact official component identity: immutable owned ModelId/root and complete geographic-cell route, exact current UID/ObjectID/CSUID native binding, fresh stable BuildingID/CSUID/GeoRef/type/heights and unique official structure links. The observed U-shaped main and upper originals are coherent; their K73/77 recorded podium/tower relation supports identity only. Each small original retains its own official unit and permit; no shared legal ownership is inferred. Original source projection differs from current footprint coverage and extensions; every raw failure, footprint drift and mutable service OBJECTID difference remains recorded. These are faithful published source units, not a claim of complete current architecture. All support, shared-plane/crossing interfaces, grade, runtime, device and publication checks remain separate.')
 for bound in pins.values():
  for name,sha in bound.items():assert digest((ROOT/name).read_bytes())==sha
 save(out/'summary.json',result)
 module('ocean_four_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-four-ocean-original-stable-primary-identity-only-review',list(dict.fromkeys(refs)),result)
 print(dict(identities=len(rows),identityOnly=True,physicalAcceptance=False),flush=True)
if __name__=='__main__':main()
