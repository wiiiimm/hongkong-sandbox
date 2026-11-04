"""ROOT exact-original identity review; no placement or publication approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';SRC=BASE/'government-xl-star-house-podium-identity-v2-20261020';VIEWS=BASE/'government-xl-star-house-podium-source-views-v1-20261020';OVER=BASE/'government-xl-star-house-podium-overlap-views-v1-20261020';BATCH='government-xl-star-house-podium-identity-review-v1-20261020';DOC=BASE/BATCH
assert not DOC.exists();pins={};refs=[Path(__file__)]
with connect() as c:
 c.execute('SET TRANSACTION READ ONLY')
 for folder in [SRC,VIEWS,OVER]:
  r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
proof=read(SRC/'identity.json');pr=proof['originalOwnership']['fullProjection'];assert proof['uid']=='landsd/231484:0'
assert proof['originalOwnership']['sourceGraphVerified'] and proof['exactCurrentComponentRoute']['qualified'] and proof['exactWholeCellCoverage']['covered'] and proof['geographicCell']['targetCoversWholeCell']
assert pr['exactObjectAndCSUID'] and pr['targetCoveredBySourceProjection']>.997
assert set(proof['reasons'])=={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
assert {f['uid'] for f in pr['intersectingForms'] if not f['sameParent']}=={'landsd/211943:0','landsd/215934:0'}
images=[VIEWS/'complete-source-four-views.png',OVER/'overlap-context.png']
review=dict(uid=proof['uid'],reviewer='Codex ROOT',reviewType='exact-original-component-identity',sourceSHA256=proof['sourceSHA256'],sourceFormSHA256=proof['sourceFormSHA256'],worldTrianglesSHA256=proof['worldTrianglesSHA256'],identityOnlyApproved=True,identityReviewApproved=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),rawProof=proof,rawReasonsRetained=proof['reasons'],imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())) for p in images],reviewBasis=[
 'Exact provider ObjectID231484 and CSUID3545617307P20060311 route the complete unchanged source to the current Star House podium record. Source graph, typed component route and whole geographic cell are verified. Exact building record remained unchanged while its historical tile hash was refreshed explicitly.',
 'Complete original projection covers99.712649% of the current target footprint. ROOT inspected the complete four-angle source export and exact footprint overlay: a coherent broad rectangular low-rise podium with projecting edge structures and roof details. This establishes source correspondence, not photographic facade verification.',
 'Preserve the raw116.3700m2 Ocean Terminal open-sided-structure footprint overlap and0.7718m2 Marco Polo hotel footprint overlap. The diagram places affected source faces at the podium perimeter. Their existence does not invalidate the unique provider identity, but physical collision/placement/neighbour checks remain mandatory. No adjacent UID is merged, suppressed, relabelled or accepted as this source.',
 'Identity acceptance only. All original source bytes, facets and native pose remain unchanged. No support-interface, foundation, collision, neighbour, browser or publication requirement is waived. No legal ownership or structural engineering conclusion is made.'
],sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,placementReviewed=False,publicationApproved=False,installationApproved=False)
save(DOC/'231484:0-review.json',review)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
module('star_identity_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-podium-identity-review',list(dict.fromkeys(refs)),dict(uids=[proof['uid']],identityAccepted=True,installationApproved=False,modelGeometryChanges=0))
