"""Exact official shared-structure attribution; no geometry or physical exemption."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from yoho_eight_current_bound_identity_20261009 import stream_pin
BASE=ROOT/'docs/astra-city/government-import';B='government-xl-source118003-structure-identity-v1-20261022';D=BASE/B
N=dict(runtime='government-xl-source118003-after-tung-ping-current-v1-20261022-runtime',identity='government-xl-source118003-after-tung-ping-current-v1-20261022-identity',scope='government-xl-source118003-after-tung-ping-current-v1-20261022-scope',primary='government-xl-source118003-primary-records-v1-20261022',lookup='government-xl-source118003-adjacent-lookup-v1-20261022',adjacent='government-xl-source118003-adjacent-original-acquire-v1-20261022',comparison='government-xl-source118003-complete-adjacent-diagnostic-v1-20261022')
UID='landsd/118003:0';OTHER='landsd/118128:0';SHA='f3d9ed0d2750849db16427133f0c09c441a01d8a5ef1f3c9c8e26dbf6f1a96e0';OTHER_SHA='e3eee7aecd7157ae547c8a8747ba4e3f6a7f17f5a99ce3a699aecd8089b277b4'
REASONS={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage','full-source-unrelated-overlap'}
assert not D.exists();refs=[Path(__file__)];pins={}
for k,n in N.items():
 _,pins[k]=authenticate(BASE/n);refs.append(BASE/n/'result.json')
def take(k,f):
 p=BASE/N[k]/f;assert digest(p.read_bytes())==pins[k][str(p.relative_to(ROOT))];refs.append(p);return read(p)
s=take('runtime','selection.json.gz');assert len(s['rows'])==1;r=s['rows'][0];assert r['uid']==UID and r['sourceSHA256']==SHA
raw=take('identity','118003:0/identity.json');assert not raw['passed']and set(raw['reasons'])==REASONS and raw['sourceSHA256']==SHA
assert raw['originalOwnership']['sourceGraphVerified']and raw['exactCurrentComponentRoute']['qualified']and raw['exactWholeCellCoverage']['covered']
assert raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==12969
assert {f['uid']for f in raw['freshCurrentIdentity']['intersectingForms']}=={UID,OTHER}
assert {f['uid']for f in raw['freshCurrentIdentity']['intersectingForms']if not f['sameParent']}=={OTHER}
forms=take('scope','form-obligations.json.gz');assert next(f for f in forms if f['uid']==UID)==r['source']['building']
lookup=take('lookup','lookup.json');other=lookup['currentAdjacentForm'];assert next(f for f in forms if f['uid']==OTHER)==other
primary=take('primary','footprints.json');attrs={f['attributes']['BuildingCSUID']:f['attributes']for f in primary['features']};assert len(attrs)==len(primary['features'])==2
relations=take('primary','relations.json')['features'];assert {(f['attributes']['BuildingCSUID'],f['attributes']['BuildingStructureID'])for f in relations}=={('3553718593T20050430',1645937),('3553718587T20050430',1645937)}
structures=take('primary','structures.json')['features'];assert len(structures)==1 and structures[0]['attributes']['BuildingStructureID']==1645937 and structures[0]['attributes']['Storeys']==7
acq=take('adjacent','summary.json');assert acq['sourceRecovered']and acq['sourceSHA256']==OTHER_SHA
comparison=take('comparison','summary.json');assert comparison['completePairEnumeration'] and comparison['trianglePairsTested']==2493 and comparison['sourceSHA256ByUid']=={UID:SHA,OTHER:OTHER_SHA}
assert 0<comparison['sourceProjectedIntersectionM2']<.012
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');sha,d=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(r['native']['cacheKey'],)).fetchone()
 assert sha==r['native']['resultSha']==lookup['nativeResultSHA256']
 models={m['modelId']:m for m in d['models']if m['modelId']in {'B355371859301063C0','B355371858701063C0'}}
 assert models['B355371859301063C0']==r['native']['model']and models['B355371858701063C0']==lookup['matchedOriginalModels'][0]
streams={}
for uid,form,modelid,count,asset,expected in [(UID,r['source']['building'],'B355371859301063C0',12969,ROOT/r['candidate']['path'],SHA),(OTHER,other,'B355371858701063C0',550,ROOT/acq['asset']['path'],OTHER_SHA)]:
 csuid=form['buildingCSUID'];a=attrs[csuid];assert a['Status']=='Active'and a['GeoRefNo']==csuid[:10]==modelid[1:11]
 assert a['BaseHeight']==form['baseHeightHKPD']and a['TopHeight']==form['topHeightHKPD']
 assert models[modelid]['asset']['sha256']==expected and models[modelid]['triangles']==count
 blob=asset.read_bytes();assert digest(blob)==expected;refs.append(asset);streams[uid]=stream_pin(blob,modelid,count)
form=r['source']['building'];entry=r['candidate']['entry'];route=raw['exactCurrentComponentRoute']
assert route['source']['building']==form and route['official']['objectId']==form['objectId']==entry['objectId']==118003
assert route['official']['buildingCSUID']==form['buildingCSUID']==entry['buildingCSUID']=='3553718593T20050430'
assert [f for f in forms if f.get('objectId')==118003 and f.get('buildingCSUID')==form['buildingCSUID']]==[form]
manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==s['manifestSHA256']==pins['scope'][str(manifest.relative_to(ROOT))];refs.append(manifest)
proof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True)
result=dict(uids=[UID],uid=UID,sourceSHA256=SHA,relatedUID=OTHER,relatedSourceSHA256=OTHER_SHA,sourceFormSHA256=raw['sourceFormSHA256'],worldTrianglesSHA256=raw['worldTrianglesSHA256'],currentManifestSHA256=s['manifestSHA256'],identityAccepted=True,passed=True,reasons=[],proof=proof,rawIdentityVerbatim=raw,allCurrentFormsRetained=forms,officialStructureID=1645937,currentNativeSourceVersionsReadBack=True,sourceSpecificIdentityRecomputed=True,currentFormSuppression=False,currentCollisionExemption=False,currentTerrainExemption=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Fresh active exact CSUID/GeoRefNo/native records and explicit shared government BuildingStructureID attribute the sole other footprint to the same official structure. ROOT reviews the bounded main footprint discrepancy separately with complete source diagrams/strict physical evidence; coarse polygons are not geometry ownership. Full unchanged original graph/root/streams and distinct original adjacent source retained. No approval of the adjacent source, suppression, geometry/pose change or collision/terrain exemption. Complete physical/browser/publication gates remain.')
save(D/'identity.json',result);save(D/'complete-original-streams.json.gz',streams)
refs.extend([HERE/'yoho_eight_current_bound_identity_20261009.py',HERE/'exact_packed_world_geometry_20261009.py'])
module('structure_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B,'exact-official-structure-bounded-identity',refs,result)
