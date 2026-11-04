"""Exact-source identity review only; no collision, placement or publication waiver."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PAIR=BASE/'government-xl-lee-kong-pair-runtime-v1-20261020';BATCH='government-xl-lee-kong-pair-identity-review-v1-20261020';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__)];pins={}
folders=[PAIR,BASE/'government-xl-lee-kong72296-source-views-v1-20261020',BASE/'government-xl-lee-kong253697-source-views-v1-20261020']
with connect() as c:
 c.execute('SET TRANSACTION READ ONLY')
 for folder in folders:
  r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
rows=read(PAIR/'selection.json.gz')['rows'];assert {r['uid'] for r in rows}=={'landsd/72296:0','landsd/253697:0'}
for row in rows:
 uid=row['uid'];key=uid.split('/')[1];proof=read(PAIR/key/'identity.json');pr=proof['originalOwnership']['fullProjection']
 assert proof['originalOwnership']['sourceGraphVerified'] and proof['exactCurrentComponentRoute']['qualified'] and proof['exactWholeCellCoverage']['covered'] and proof['geographicCell']['targetCoversWholeCell']
 assert pr['exactObjectAndCSUID'] and pr['targetCoveredBySourceProjection']>.99
 assert set(proof['reasons'])=={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
 assert {f['uid'] for f in pr['intersectingForms']}=={'landsd/72296:0','landsd/253697:0','landsd/147956:0','landsd/145527:0'}
 assert pr['sourceExcessCoveredByUnrelatedFormsM2']<4 and pr['sourceExcessMaximumDistanceFromTargetM']<2.34
 image=BASE/('government-xl-lee-kong'+key.split(':')[0]+'-source-views-v1-20261020')/'complete-source-four-views.png'
 assert digest(image.read_bytes())==pins[str(image.relative_to(ROOT))]
 save(DOC/(key+'-review.json'),dict(uid=uid,reviewer='Codex ROOT',reviewType='exact-original-component-identity',sourceSHA256=row['sourceSHA256'],sourceFormSHA256=proof['sourceFormSHA256'],worldTrianglesSHA256=proof['worldTrianglesSHA256'],modelId=row['modelId'],sourceFaces=row['triangles'],identityOnlyApproved=True,identityReviewApproved=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),rawProof=proof,rawReasonsRetained=proof['reasons'],imagesActuallyInspected=[dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes()))],reviewBasis=[
 'Exact provider ObjectID, CSUID and tower/podium type uniquely route this complete unchanged source to the current target. Original graph and complete one-metre GeoRef cell agree. Both current basic forms independently name Lee Kong Commercial Building.',
 'Complete source projection covers more than 99% of the routed target footprint. The two raw foreign-footprint flags remain recorded. Small overlaps with adjacent Vancor and unnamed145527 footprints do not contradict the unique authoritative source route; those neighbours remain independent and must not be suppressed or relabelled.',
 'ROOT inspected each complete four-view original export: a lower block with projecting canopy/parapet and a separate tall narrow tower with vertical recesses and stepped roof. Source-authored coordinates are retained, including the different vertical split from basic-model height metadata. This is source inspection, not a claim of photographic facade verification.',
 'This accepts source identity only. It grants no collision clearance, support, neighbour, placement or publication approval; those independent current checks remain mandatory. No legal common ownership or structural engineering conclusion is inferred.'
 ],sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,placementReviewed=False,publicationApproved=False,installationApproved=False))
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
module('lee_pair_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-pair-identity-review',list(dict.fromkeys(refs)),dict(uids=[r['uid'] for r in rows],identityAccepted=True,installationApproved=False))
