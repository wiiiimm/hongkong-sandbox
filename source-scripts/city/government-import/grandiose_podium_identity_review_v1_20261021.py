"""Bounded original identity review; preserve all physical acceptance obligations."""
from pathlib import Path
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grandiose-podium-identity-review-v1-20261021';DOC=BASE/BATCH
ID=BASE/'government-xl-grandiose-podium-identity-v1-20261021';PRI=BASE/'government-xl-grandiose-podium-primary-records-v1-20261021';EXT=BASE/'government-xl-grandiose-podium-extent-v1-20261021';CAP=BASE/'government-xl-grandiose-podium-current-terrain-v1-20261021'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [ID,PRI,EXT,CAP]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=read(CAP/'selection.json.gz')['rows'][0];b=row['source']['building'];identity=read(ID/'identity.json');extent=read(EXT/'246824:0.json');records=read(PRI/'footprints.json')['features'];assert len(records)==1
 record=records[0];a=record['attributes'];assert a['Status']=='Active' and a['GeoRefNo']==row['modelId'][1:11]=='4498618852'
 assert a['BuildingCSUID']==b['buildingCSUID']=='4498618852P20060317' and a['BuildingID']==b['buildingId']==1101763586
 assert a['BuildingBlockType']==b['structureType']=='Podium'
 assert identity['originalOwnership']['sourceGraphVerified'] and identity['freshCurrentIdentity']['exactObjectAndCSUID']
 assert row['sourceSHA256']==identity['sourceSHA256']==extent['sourceSHA256'] and extent['completeFaceCount']==3627
 rings=[[[x-834500,816500-y] for x,y in ring] for ring in record['geometry']['rings']];assert len(rings)==1
 official=Polygon(rings[0]);current=Polygon(b['rings'][0],b['rings'][1:]);overlap=current.intersection(official).area/current.area;assert overlap>.9999
 matches=[]
 for tile in read(ROOT/'3d-viewer/city/data/manifest.json')['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];refs.append(path)
  for form in read(path)['buildings']:
   if str(form.get('buildingCSUID',''))[:10]==a['GeoRefNo']:matches.append(form)
 assert matches==[b]
 image=EXT/'246824:0.png';assert str(image.relative_to(ROOT)) in pins
 review=dict(uids=[row['uid']],sourceIdentityAccepted=True,sourceSHA256=row['sourceSHA256'],modelId=row['modelId'],completeOriginalFaces=3627,primaryRecord=a,uniqueCurrentGeoRef=True,primaryFootprintCoverage=overlap,rawReasons=identity['reasons'],rawExtent=extent,imagesActuallyViewed=[dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes()))],basis='Stable GeoRef, CSUID, BuildingID and active government podium record identify the same unique current source. The complete unchanged original graph is verified; the viewed plan and 3D context show aligned main mass with a thin authored projection extending along one edge. Accept source identity only, without inferring the function or ownership of those projections. Preserve full extent, contact, terrain, collision, neighbour and browser obligations; this is not placement or publication approval.',collisionReviewRequiredFor=['landsd/27898:0'],reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,geometryChanges=0,sourcePoseChanges=0,installationApproved=False)
 save(DOC/'ROOT-IDENTITY-REVIEW.json',review)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in pins)
 module('tko_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-podium-source-identity-review',list(dict.fromkeys(refs)),dict(uids=[row['uid']],sourceIdentityAccepted=True,installationApproved=False,newlyInstalled=0))
if __name__=='__main__':main()
