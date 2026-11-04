"""Exact-source YOHO compound identity review; raw individual footprint flags retained."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from original_source_ownership import document,graph_reasons
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-compound-identity-review-v1-20261020';DOC=BASE/BATCH
NAMES=['government-xl-yoho-seven-original-identity-v4-20261020','government-xl-yoho-seven-primary-records-v1-20261020','government-xl-yoho301659-compound-context-v1-20261020','government-xl-yoho300857-podium-identity-v1-20261020','government-xl-yoho300857-podium-extent-diagnostic-v3-20261020','government-xl-yoho300857-extent-views-v1-20261020']
EXPECTED={'landsd/301659:0':('B216763410301062G0','2167634103T20221222','77040c9783eb8440ce571bf4c99aab40b397de62ff9240fbf2325ac067b411a3',138),'landsd/301636:0':('B216933408902063C0','2169334089P20221215','88497660f40256fa62868e1e80fff1cbebeff358c7f3cd9df1d5604f3370b0f8',19952)}
assert not DOC.exists();refs=[Path(__file__),HERE/'original_source_ownership.py'];pins={}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for name in NAMES:
  d=BASE/name;r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
  for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
def consume(n,f):
 p=BASE/NAMES[n]/f;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
rows=consume(0,'selection.json.gz')['rows'];primary=consume(1,'footprints.json')['features'];context=consume(2,'context.json');podium=consume(3,'identity.json');foreign=consume(4,'foreign-overlap.json')
assert context['ownSourceFootprintCoverage']==0 and context['compoundFootprintCoverage']>=.999999 and context['positiveOriginalPodiumContacts']==45
assert context['sourceWorldSHA256']=='7c5ea4a6765f499e7e69231d8f7a35da97f4adfc684e6ca9eb505fa3853d30b1'
assert context['podiumWorldSHA256']=='45cbca13e3858f7b7543d0594c25e20f9c798ee182980874d92466dcfb032813'
assert podium['originalOwnership']['sourceGraphVerified'] and podium['originalOwnership']['fullProjection']['exactObjectAndCSUID']
assert set(podium['reasons'])=={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent','full-source-unrelated-overlap'}
manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest);allforms=[]
for tile in read(manifest)['tiles']:
 p=ROOT/'3d-viewer'/tile['url'];allforms.extend(read(p)['buildings']);refs.append(p)
accounts=[]
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for uid,(modelid,csuid,sha,faces)in EXPECTED.items():
  r=next(x for x in rows if x['uid']==uid);assert (r['modelId'],r['source']['building']['buildingCSUID'],r['sourceSHA256'],r['triangles'])==(modelid,csuid,sha,faces)
  assert [x for x in allforms if x.get('buildingCSUID')==csuid]==[r['source']['building']]
  assert len([x for x in allforms if str(x.get('buildingCSUID',''))[:10]==csuid[:10]])==1
  records=[x for x in primary if x['attributes']['BuildingCSUID']==csuid];assert len(records)==1;attrs=records[0]['attributes'];assert attrs['Status']=='Active' and attrs['GeoRefNo']==modelid[1:11] and attrs['BuildingID']==r['source']['building']['buildingId']
  native=r['native'];dbsha,n=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(native['cacheKey'],)).fetchone();assert dbsha==native['resultSha'] and next(x for x in n['models']if x['modelId']==modelid)==native['model']
  candidates=native['model']['matching']['officialCandidates'];assert len(candidates)==1 and candidates[0]['buildingCSUID']==csuid
  asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==sha;refs.append(asset);assert graph_reasons(document(asset.read_bytes()),modelid,faces)==[]
  accounts.append(dict(uid=uid,sourceSHA256=sha,modelId=modelid,buildingCSUID=csuid,completeOriginalFaces=faces,uniqueCurrentGeoRef=True,completeNamedSourceGraphVerified=True,currentPrimaryRecord=attrs,rawNativeMatching=native['model']['matching']))
images=[]
for i,f in [(2,'context.png'),(5,'plan.png')]:
 p=BASE/NAMES[i]/f;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
review=dict(uids=list(EXPECTED),compoundIdentityAccepted=True,standaloneSmallStructureIdentityAccepted=False,requiredCompanionUID='landsd/301636:0',requiredCompanionSHA256=EXPECTED['landsd/301636:0'][2],accounts=accounts,compoundContext=context,rawPodiumIdentityReasons=podium['reasons'],rawSmallIdentity=consume(0,'301659:0/identity.json'),foreignOverlapEvidence=foreign,imagesActuallyViewed=images,reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,geometryChanges=0,sourcePoseChanges=0,installationApproved=False,basis='Both complete original meshes belong to exact named government roots and uniquely identified current GeoRefs with active primary records. Podium footprint extent is an incomplete 2D envelope of its source-defined extensions, not evidence of a second named source actor. Its original graph contains all facets; foreign projected overlap remains recorded for independent collision review. The small original has zero own-target overlap and is not approved as a standalone footprint replacement. Its recorded footprint is covered by the exact companion podium, and45 positive finite source contacts bind the small component to that assembly. Accept the original component identity only with this exact podium installed and loaded as its companion. No function, named landmark or ownership inference is made. All individual raw shape failures remain in evidence. This does not approve placement, collision, neighbour regressions, runtime or publication.')
save(DOC/'ROOT-COMPOUND-IDENTITY-REVIEW.json',review)
module('yoho_compound_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-government-original-compound-identity-review',list(dict.fromkeys(refs)),dict(uids=list(EXPECTED),compoundIdentityAccepted=True,standaloneSmallStructureIdentityAccepted=False,installationApproved=False,geometryChanges=0))
