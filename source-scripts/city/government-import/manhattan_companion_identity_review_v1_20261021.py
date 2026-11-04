"""Source-specific identity only; retain all spatial/support/publication failures."""
from pathlib import Path
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from original_source_ownership import document,graph_reasons
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-manhattan-companion-identity-review-v1-20261021';DOC=BASE/BATCH
ID=BASE/'government-xl-manhattan-companion-identity-v1-20261021';PRI=BASE/'government-xl-manhattan-primary-records-v1-20261021';EXT=BASE/'government-xl-manhattan-companion-extent-v1-20261021'
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'original_source_ownership.py'];pins={};used={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [ID,PRI,EXT]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in r['evidenceRefs']}
 def take(d,p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[d][k];used[k]=pins[d][k];refs.append(p);return read(p)
 rows=take(ID,ID/'selection.json.gz')['rows'];primary=take(PRI,PRI/'footprints.json')['features'];manifestpath=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifestpath);forms=[]
 for tile in read(manifestpath)['tiles']:
  p=ROOT/'3d-viewer'/tile['url'];forms.extend(read(p)['buildings']);refs.append(p)
 reviewed=[]
 for row in rows:
  uid=row['uid'];key=uid.split('/')[1];identity=take(ID,ID/key/'identity.json');b=row['source']['building'];matches=[x for x in primary if x['attributes']['BuildingCSUID']==b['buildingCSUID']];assert len(matches)==1;record=matches[0];a=record['attributes'];modelid=row['modelId'];asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];refs.append(asset)
  assert a['Status']=='Active' and a['GeoRefNo']==modelid[1:11] and a['BuildingID']==b['buildingId'] and a['BuildingBlockType']==b['structureType']
  assert [f for f in forms if f.get('buildingCSUID')==b['buildingCSUID']]==[b]
  assert [f for f in forms if str(f.get('buildingCSUID',''))[:10]==a['GeoRefNo']]==[b]
  assert graph_reasons(document(raw),modelid,row['triangles'])==[] and identity['originalOwnership']['sourceGraphVerified'] and identity['freshCurrentIdentity']['exactObjectAndCSUID']
  rings=[[[x-834500,816500-y] for x,y in ring] for ring in record['geometry']['rings']];current=Polygon(b['rings'][0],b['rings'][1:]);official=Polygon(rings[0],rings[1:]);agreement=current.intersection(official).area/current.area
  images=[];extent=None
  if identity['reasons']:
   extent=take(EXT,EXT/(key+'.json'));p=EXT/(key+'.png');k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[EXT][k];refs.append(p);images=[dict(path=k,sha256=pins[EXT][k])]
  reviewed.append(dict(uid=uid,modelId=modelid,sourceSHA256=row['sourceSHA256'],completeOriginalFaces=row['triangles'],currentPrimaryRecord=a,uniqueCurrentCSUIDAndGeoRef=True,primaryFootprintAgreement=agreement,rawProjection=identity['freshCurrentIdentity'],rawReasons=identity['reasons'],rawExtent=extent,imagesActuallyViewed=images,sourceIdentityAccepted=True,placementAccepted=False,publicationApproved=False))
 # Bind this specific observed batch, not a new general acceptance threshold.
 expected={'landsd/271788:0':.9996083864844104,'landsd/260440:0':.999918774319945,'landsd/307773:0':.9998859440974625,'landsd/120103:0':.9999585916389286,'landsd/258271:0':.999878143433388,'landsd/266799:0':.9999582357742776,'landsd/213072:0':.9999672463917564}
 assert {r['uid'] for r in reviewed}==set(expected)
 for r in reviewed:assert abs(r['primaryFootprintAgreement']-expected[r['uid']])<1e-12
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 review=dict(uids=sorted(expected),rows=reviewed,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,installationApproved=False,reviewer='Codex ROOT',basis='Government active records, stable CSUID/GeoRef/BuildingID, unique current source form, complete original named graph and inspected complete-source diagrams identify the same seven source actors. Six 3D projections do not cover the full 2D footprint; retain those raw failures and all overlap/support warnings. Identity here means attribution to the government source actor, not a claim of complete footprint coverage, correct contact, safe collision, or publication readiness.',visualLimitations='Transparent whole-source obliques and plan outlines identify alignment and projection differences; they do not prove surface clearance or complete support. Source projection coverage ranges from about 75.6% to 99.8%. No original geometry or pose changed.')
 save(DOC/'ROOT-IDENTITY-REVIEW.json',review);module('manhattan_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-companion-attribution-review',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
