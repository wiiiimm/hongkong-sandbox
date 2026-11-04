"""Exact Tung Ping/BlockF record identity; no geometry edits or physical waiver."""
from copy import deepcopy
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from yoho_eight_current_bound_identity_20261009 import stream_pin
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-tung-ping-related-record-identity-v1-20261022'
NAMES=dict(runtime='government-xl-tung-ping-after-yoho-current-v1-20261022-runtime',identity='government-xl-tung-ping-after-yoho-current-v1-20261022-identity',scope='government-xl-tung-ping-after-yoho-current-v1-20261022-scope',primary='government-xl-tung-ping-primary-records-v1-20261022',alias='government-xl-tung-ping-official-block-alias-v1-20261022',lookup='government-xl-tung-ping-low-annex-source-lookup-v1-20261022',annex='government-xl-tung-ping-annex-original-acquire-v1-20261022',interface='government-xl-tung-ping-annex-exact-interface-v1-20261022')
UID='landsd/97301:0';RELATED='landsd/97300:0'
SOURCE='1401822634163c71c14b23c87791896c3e78d13d7362b112fc693eb19c94458d';ANNEX='ab0ddef30aa0ea08b5bc7f86db9eb10c90924d753fcff909a0500ad123a21dea'
REASONS={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
def main():
 doc=BASE/BATCH;assert not doc.exists();refs=[Path(__file__)];pins={}
 for key,name in NAMES.items():
  _,pins[key]=authenticate(BASE/name);refs.append(BASE/name/'result.json')
 def take(key,file):
  p=BASE/NAMES[key]/file;assert digest(p.read_bytes())==pins[key][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 selected=take('runtime','selection.json.gz');row=next(r for r in selected['rows']if r['uid']==UID)
 raw=take('identity','97301:0/identity.json');forms=take('scope','form-obligations.json.gz');scope=take('scope','scope.json')
 assert raw['uid']==UID and raw['sourceSHA256']==SOURCE==row['sourceSHA256']and not raw['passed']and set(raw['reasons'])==REASONS
 assert raw['originalOwnership']['sourceGraphVerified']and raw['exactCurrentComponentRoute']['qualified']and raw['exactWholeCellCoverage']['covered']
 assert raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==11443
 assert {r['uid']for r in raw['freshCurrentIdentity']['intersectingForms']}=={UID,RELATED}
 assert raw['freshCurrentIdentity']['unrelatedIntersectingForms']==1
 assert {r['uid']for r in raw['freshCurrentIdentity']['intersectingForms']if not r['sameParent']}=={RELATED}
 alias=take('alias','ROOT-ALIAS-OBSERVATION.json');assert alias['officialBuildingBlockAliasConfirmed']and alias['reviewer']=='ROOT'
 request=take('alias','request.json');pdf=BASE/NAMES['alias']/'housing-authority-tung-ping-block-f.pdf'
 assert digest(pdf.read_bytes())==request['sha256']==pins['alias'][str(pdf.relative_to(ROOT))];refs.append(pdf)
 assert request['url']=='https://www.housingauthority.gov.hk/hdw/content/static/file/b5/residential/plans/leitungestate_tungpinghouse.pdf'
 for image in alias['imagesActuallyViewed']:
  p=ROOT/image['path'];assert digest(p.read_bytes())==image['sha256']==pins['alias'][image['path']];refs.append(p)
 primary=take('primary','footprints.json');pr=take('primary','footprints-request.json');assert digest((BASE/NAMES['primary']/'footprints.json').read_bytes())==pr['decodedSHA256']
 attributes={f['attributes']['BuildingCSUID']:f['attributes']for f in primary['features']};assert len(primary['features'])==len(attributes)==2
 expected={UID:('3427311446T20050430','Tung Ping House','東平樓',SOURCE,'B342731144601063C0',11443),RELATED:('3426211455T20050430','TUNG PING HSE (BLK F)','東平樓(F座)',ANNEX,'B342621145501063C0',51)}
 lookup=take('lookup','lookup.json');annex=take('annex','summary.json');assert annex['sourceRecovered']and annex['sourceSHA256']==ANNEX
 models={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  sha,values=db.execute("SELECT result_sha,result->'models' FROM astra_modelling.native_stage_results WHERE cache_key=%s",(lookup['nativeCacheKey'],)).fetchone();assert sha==lookup['nativeResultSHA256']==row['native']['resultSha']
  models={m['modelId']:m for m in values if m['modelId']in {e[4]for e in expected.values()}}
 assert len(models)==2 and models[expected[UID][4]]==row['native']['model']and models[expected[RELATED][4]]==lookup['matchedOriginalModels'][0]
 paths={UID:ROOT/row['candidate']['path'],RELATED:ROOT/annex['asset']['path']};streams={};records=[]
 for uid,(csuid,en,tc,sha,modelid,count)in expected.items():
  form=next(f for f in forms if f['uid']==uid);record=attributes[csuid]
  assert form['buildingCSUID']==csuid and record['Status']=='Active'and record['GeoRefNo']==csuid[:10]==modelid[1:11]
  assert record['BuildingNameEN']==en and record['BuildingNameTC']==tc
  assert record['BaseHeight']==form['baseHeightHKPD']and record['TopHeight']==form['topHeightHKPD']
  assert models[modelid]['asset']['sha256']==sha and models[modelid]['triangles']==count
  path=paths[uid];blob=path.read_bytes();assert digest(blob)==sha;refs.append(path);streams[uid]=stream_pin(blob,modelid,count)
  records.append(dict(uid=uid,buildingCSUID=csuid,modelId=modelid,currentViewerObjectId=form['objectId'],currentPrimaryObjectId=record['OBJECTID'],primaryRecord=record))
 assert next(f for f in forms if f['uid']==UID)==row['source']['building']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256']==pins['scope'][str(manifest.relative_to(ROOT))];refs.append(manifest)
 proof=deepcopy(raw['proof']);assert all(proof[k]for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch']);proof['identityAccepted']=True
 report=dict(uids=[UID],uid=UID,sourceSHA256=SOURCE,relatedUID=RELATED,relatedSourceSHA256=ANNEX,sourceFormSHA256=raw['sourceFormSHA256'],worldTrianglesSHA256=raw['worldTrianglesSHA256'],currentManifestSHA256=selected['manifestSHA256'],identityAccepted=True,passed=True,reasons=[],proof=proof,onlyNamedRelatedReasonsReplaced=sorted(REASONS),rawIdentityVerbatim=raw,allCurrentFormsRetained=forms,sourceRecords=records,currentNativeSourceVersionsReadBack=True,sourceSpecificIdentityRecomputed=True,historicalManifestApprovalTransferred=False,currentFormSuppression=False,currentCollisionExemption=False,currentTerrainExemption=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Exact two CSUID/native-source records and independently official TungPing/BlockF name equivalence identify the sole related footprint. No legal/common-ownership, component-function or support inference. Original no-contact result retained; exact connectivity is not required for this identity attribution. Every other source/geo/route guard remains. No viewer form, geometry, pose, collision or terrain exemption; full physical and browser gates remain separate.')
 save(doc/'identity.json',report);save(doc/'complete-original-streams.json.gz',streams)
 refs.extend([HERE/'yoho_eight_current_bound_identity_20261009.py',HERE/'original_source_ownership.py',HERE/'exact_packed_world_geometry_20261009.py'])
 module('tung_ping_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-tung-ping-block-f-related-record-identity',refs,report)
 print(dict(identityAccepted=True,currentForms=len(forms),originalTowerFaces=11443,originalAnnexFaces=51),flush=True)
if __name__=='__main__':main()
