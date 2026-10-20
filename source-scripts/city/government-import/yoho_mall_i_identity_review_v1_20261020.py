"""Source-specific original identity review; physical/collision checks remain separate."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from original_source_ownership import document,graph_reasons
from shapely.geometry import Polygon
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-mall-i-identity-review-v1-20261020';DOC=BASE/BATCH
ID=BASE/'government-xl-next-twenty-original-identity-v2-20261020';PRI=BASE/'government-xl-yoho-mall-i-primary-records-v1-20261020';CAP=BASE/'government-xl-yoho-mall-i-private-runtime-v3-20261020';EXT=BASE/'government-xl-next-twenty-held-extent-v2-20261020'
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'original_source_ownership.py'];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [ID,PRI,CAP,EXT]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(folder,p):
  key=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[folder][key];refs.append(p);used[key]=pins[folder][key];return read(p)
 row=take(CAP,CAP/'selection.json.gz')['rows'][0];uid=row['uid'];assert uid=='landsd/189427:0';identity=take(ID,ID/'189427:0/identity.json');extent=take(EXT,EXT/'189427:0.json');primary=take(PRI,PRI/'footprints.json')['features'];assert len(primary)==1;record=primary[0];attrs=record['attributes'];building=row['source']['building'];modelid=row['modelId'];sha=row['sourceSHA256'];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==sha;refs.append(asset)
 assert sha==identity['sourceSHA256']=='371ab03231021e27ccc89d2cca415c581a4ec1478e878b0b36b4e83c9fa930b2'
 assert modelid=='B219423400602063C0' and attrs['Status']=='Active' and attrs['GeoRefNo']==modelid[1:11] and attrs['BuildingCSUID']==building['buildingCSUID']=='2194234006P20170509' and attrs['BuildingID']==building['buildingId']
 assert attrs['BuildingBlockType']==building['structureType']=='Podium';assert graph_reasons(document(asset.read_bytes()),modelid,21928)==[]
 mp=ROOT/'3d-viewer/city/data/manifest.json';refs.append(mp);matches=[];georefs=[]
 for tile in read(mp)['tiles']:
  p=ROOT/'3d-viewer'/tile['url'];data=read(p);refs.append(p)
  for b in data['buildings']:
   if b.get('buildingCSUID')==attrs['BuildingCSUID']:matches.append(b)
   if str(b.get('buildingCSUID',''))[:10]==attrs['GeoRefNo']:georefs.append(b)
 assert matches==[building]and georefs==[building]
 rings=[[[x-834500,816500-y]for x,y in ring]for ring in record['geometry']['rings']];assert len(rings)==1
 official=Polygon(rings[0]);current=Polygon(building['rings'][0],building['rings'][1:]);agreement=dict(currentAreaM2=current.area,primaryAreaM2=official.area,intersectionM2=current.intersection(official).area,symmetricDifferenceM2=current.symmetric_difference(official).area)
 assert current.intersection(official).area/current.area>.9999
 raw=identity['freshCurrentIdentity'];assert raw['exactObjectAndCSUID']and identity['originalOwnership']['sourceGraphVerified'];assert abs(raw['targetCoveredBySourceProjection']-.9994637739724315)<1e-9
 foreign=[r for r in raw['intersectingForms']if not r['sameParent']];assert len(foreign)==1 and foreign[0]['uid']=='way/949541091:0'
 image=EXT/'189427:0.png';assert digest(image.read_bytes())==pins[EXT][str(image.relative_to(ROOT))];refs.append(image)
 review=dict(uids=[uid],sourceIdentityAccepted=True,sourceSHA256=sha,modelId=modelid,buildingCSUID=attrs['BuildingCSUID'],completeOriginalFaces=21928,uniqueCurrentCSUIDAndGeoRef=True,currentPrimaryRecord=attrs,primaryFootprintAgreement=agreement,objectIdRevisionContext=dict(viewerSnapshotObjectId=building['objectId'],currentServiceObjectId=attrs['OBJECTID'],stableIdentityFields=['BuildingCSUID','GeoRefNo','BuildingID']),rawIdentityReasons=identity['reasons'],rawProjection=raw,rawExtentEvidence=extent,imagesActuallyViewed=[dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes()))],collisionReviewRequiredFor=[foreign[0]['uid']],reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,geometryChanges=0,sourcePoseChanges=0,installationApproved=False,basis='The complete named original government graph, stable GeoRef/CSUID/BuildingID and unique current viewer record identify the same active podium. Current primary footprint agrees with the recorded source footprint. The reviewed complete-source plan shows the main mass aligned and a thin authored projection outside the 2D footprint; no separate named source actor is inferred. Accept source identity only. Preserve all extent and foreign-overlap warnings for separate collision/placement review. Current service OBJECTID differs from the viewer snapshot; stable identity fields, not cross-revision row numbers, establish the match. No neighbouring ownership or architectural function is inferred.')
 save(DOC/'ROOT-IDENTITY-REVIEW.json',review)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 module('yoho_identity_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-podium-source-identity-review',list(dict.fromkeys(refs)),dict(uids=[uid],sourceIdentityAccepted=True,installationApproved=False,geometryChanges=0))
if __name__=='__main__':main()
