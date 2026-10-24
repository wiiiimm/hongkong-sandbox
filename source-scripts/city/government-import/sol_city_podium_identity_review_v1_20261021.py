"""Exact unchanged source identity review; physical/publication checks stay independent."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sol-city-podium-identity-review-v1-20261021';DOC=BASE/BATCH
SRC=BASE/'government-xl-sol-city-current-identity-v1-20261021';VIEWS=BASE/'government-xl-sol-city-podium-source-views-v1-20261021';OVER=BASE/'government-xl-sol-city-overlap-view-v1-20261021';PRIMARY=BASE/'government-xl-sol-city-primary-records-v2-20261021'
assert not DOC.exists();pins={};refs=[Path(__file__)]
with connect()as db:
 db.execute('SET TRANSACTION READ ONLY')
 for folder in [SRC,VIEWS,OVER,PRIMARY]:
  r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
proof=read(SRC/'273271:0/identity.json');pr=proof['originalOwnership']['fullProjection'];route=proof['exactCurrentComponentRoute']
assert proof['uid']=='landsd/273271:0' and proof['sourceSHA256']=='d29f47a2057f80dc83e57792a3d53e9f8636ba86ae614ca5877e436e23bdaf43'
assert proof['originalOwnership']['sourceGraphVerified']and route['qualified']and proof['exactWholeCellCoverage']['covered']and proof['geographicCell']['targetCoversWholeCell']
assert route['official']['objectId']==273271 and route['official']['buildingCSUID']=='2063534193P20200511'
assert pr['exactObjectAndCSUID']and pr['targetCoveredBySourceProjection']==0.9866439660640891
assert set(proof['reasons'])=={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
assert {f['uid']for f in pr['intersectingForms']}=={'landsd/273271:0','landsd/251569:0','landsd/260034:0','landsd/268424:0','landsd/273080:0','landsd/170270:0'}
images=[VIEWS/'complete-source-four-views.png',OVER/'source-overlap.png']
review=dict(uid=proof['uid'],reviewer='Codex ROOT',reviewType='exact-original-component-identity',sourceSHA256=proof['sourceSHA256'],sourceFormSHA256=proof['sourceFormSHA256'],worldTrianglesSHA256=proof['worldTrianglesSHA256'],identityOnlyApproved=True,sourceIdentityReviewed=True,identityReviewApproved=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),rawProof=proof,rawReasonsRetained=proof['reasons'],imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],reviewBasis=[
'Exact provider ObjectID 273271 and Podium CSUID 2063534193P20200511 uniquely route the unchanged complete government source. Source graph, typed component route and whole one-metre geographic cell checks pass. No coordinates, root transform, scale or source facets are changed.',
'The complete source projection covers 98.66439660640891% of the current target footprint. ROOT inspected all 4,985 original faces from four angles: an extended low-rise podium with several connected blocks, roofs and open-sided edge structures. This is source correspondence evidence, not photographic facade or ownership verification.',
'The remaining raw flags concern projected overlap, not a conflicting exact provider identity. Retain all four separately identified tower records and the unnamed 170270 record. ROOT inspected the original local overlap from two angles: the podium structure and separate unnamed source meet/intersect in the original files. The recorded 34.302376456188746m2 plan overlap is not evidence that the entire podium is the wrong source. It remains an explicit physical/collision review obligation.',
'Identity only is accepted. No adjacent UID is merged, suppressed, relabelled or assigned to this source. No legal ownership, structural engineering, physical clearance or support conclusion is made. Complete current collision, support, foundation, neighbour, runtime, browser and publication requirements remain independent.'
],sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,placementReviewed=False,publicationApproved=False,installationApproved=False)
save(DOC/'273271:0-review.json',review)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
module('sol_identity_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-podium-identity-review',list(dict.fromkeys(refs)),dict(uids=[proof['uid']],identityAccepted=True,installationApproved=False,modelGeometryChanges=0,sourceIdentityReviewUsedAI=True))
