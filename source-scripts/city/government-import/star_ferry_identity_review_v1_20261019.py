"""Source-specific identity review of the unchanged complete Star Ferry asset."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-star-ferry-identity-review-v1-20261019';DOC=BASE/BATCH
VIEWS=BASE/'government-xl-star-ferry-extent-views-v1-20261019'
IDENTITY=BASE/'government-xl-next-five-original-identity-v1-20261018/210032:0/identity.json'
SHA='a8635ec84493ea64fa8b803bc5ea6e90f1dcd46979674e9d6d24445067491de7'
assert not DOC.exists()
r=read(VIEWS/'result.json');refs=[Path(__file__),VIEWS/'result.json']
with connect() as c:
    c.execute('SET TRANSACTION READ ONLY')
    assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
pins={e['path']:e['sha256'] for e in r['evidenceRefs']}
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
assert digest(IDENTITY.read_bytes())==pins[str(IDENTITY.relative_to(ROOT))]
p=read(IDENTITY)
assert p['uid']=='landsd/210032:0' and p['sourceSHA256']==SHA
assert p['originalOwnership']['sourceGraphVerified'] and p['exactCurrentComponentRoute']['qualified']
assert p['exactWholeCellCoverage']['covered'] and p['geographicCell']['targetCoversWholeCell']
full=p['originalOwnership']['fullProjection']
assert full['exactObjectAndCSUID'] and full['targetCoveredBySourceProjection']>.999
assert set(p['reasons'])=={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent','full-source-unrelated-overlap'}
images=[VIEWS/(n+'.png') for n in ['whole','extent-front','extent-reverse']]
for q in images:assert digest(q.read_bytes())==pins[str(q.relative_to(ROOT))]
decision=dict(uid=p['uid'],sourceSHA256=SHA,sourceFormSHA256=p['sourceFormSHA256'],worldTrianglesSHA256=p['worldTrianglesSHA256'],reviewer='Codex ROOT',identityOnlyApproved=True,identityReviewApproved=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),rawProof=p,rawReasonsRetained=p['reasons'],imagesActuallyInspected=[dict(path=str(q.relative_to(ROOT)),sha256=digest(q.read_bytes())) for q in images],reviewBasis=[
    'Exact official ObjectID and CSUID, unchanged source graph, unique current metadata route and complete GeoRef cell bind this full original asset to Star Ferry Pier.',
    'The inspected whole, front and reverse source views show the twin pier structure plus landward roofed access structures, a long covered walkway and parallel open-sided canopies. The extent highlights are these authored access/canopy components, not an unrelated complete high-rise model.',
    'Footprint excess and overlap are retained as raw diagnostics. Approval identifies the complete original source only; it does not assign new landmark names or ownership to neighbouring forms.',
    'Keep original vertices, fixed pose and scale. This decision does not suppress neighbouring buildings, approve physical overlap, resolve support, or approve publication. Those checks remain separate.'
],installationApproved=False,publicationApproved=False,physicalAcceptancePending=True,modelGeometryChanges=0)
save(DOC/'210032:0-review.json',decision)
refs.extend(images+[IDENTITY])
module('star_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'star-ferry-exact-original-identity-review',list(dict.fromkeys(refs)),dict(uids=[p['uid']],identityOnlyApproved=True,installationApproved=False))
