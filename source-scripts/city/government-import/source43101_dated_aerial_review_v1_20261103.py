"""Record actual dated-image inspection, without absence or terminal inference."""
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v2_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-source43101-dated-aerial-review-v1-20261103'
PARENT = 'government-xl-source43101-dated-orthophoto-pixels-v2-20261103'


def owned():
    lease = read(HERE / 'local' / BATCH / 'reservation.json')
    assert reservations.owns(lease)
    _, pins = authenticate(BASE / PARENT)
    p = BASE / PARENT / 'summary.json'
    assert digest(p.read_bytes()) == pins[str(p.relative_to(ROOT))]
    parent = read(p)
    assert not parent['pixelCropPending'] and parent['allArchiveMemberCRCsVerified']
    assert parent['sourceSHA256'] == '52ff46b2a9d19be07e2f885e3bd97f9362338b75a4e6d14b2539266b0ebb570f'
    assert parent['allOriginalFaces'] == 24308 and parent['allOriginalRoots'] == 2
    assert parent['crop']['independentWorldFileMatches'] and not parent['crop']['fittedTransform']
    images = parent['images']
    assert len(images) == 2
    for image in images:
        assert digest((ROOT / image['path']).read_bytes()) == image['sha256'] == pins[image['path']]
    review = dict(reviewer='ROOT', uids=parent['uids'], sourceSHA256=parent['sourceSHA256'],
                  images=images, allListedExportsActuallyInspected=True,
                  datedImageAcquisitionJobId='112e2f0759ba569a7e4e9d8983f0874a7e1eba0c5598948913c921afc2ab1d1f',
                  officialIndexAttributes=parent['officialIndexAttributes'], completeOriginalRootsPreserved=True,
                  sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False,
                  sourceEvidenceInterpretationUsedAI=True, identityAccepted=False, physicalAcceptance=False,
                  installationApproved=False, publication=False, permanentRejection=False,
                  observations='ROOT viewed both the266x274original-pixel dated crop and the full two-panel unfitted overlay. The pale roof crosses the road along the red B4561111 projection; its curved lateral feature is visible. The cyan named root lies east of that roof over marked roadway/parking and darker context. No second corresponding pale roof is clearly visible at its projected position in this January2025sheet. This is dated visual context, not proof of absence in every period, a provider correction, or an approved source identity. Perspective, classification and later changes remain relevant. Do not delete either root, move the source or approve the complete scene from the one aligned root.',
                  nextAction='Bind both complete provider roots to exact current Dock1A source/component interfaces and current primary placement evidence. Preserve all raw source identity/physical failures; no repeated archive download, root pruning or automatic terminal decision.')
    out = BASE / BATCH
    save(out / 'ROOT-DATED-AERIAL-INSPECTION.json', review)
    summary = {k: v for k, v in review.items() if k not in ['images', 'observations']}
    summary['review'] = dict(path=str((out / 'ROOT-DATED-AERIAL-INSPECTION.json').relative_to(ROOT)), sha256=digest((out / 'ROOT-DATED-AERIAL-INSPECTION.json').read_bytes()))
    save(out / 'summary.json', summary)
    assert reservations.owns(lease)
    module('source43101_dated_aerial_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'actual-dated-unfitted-original-root-aerial-context-review', [Path(__file__), BASE / PARENT / 'result.json', p, *[ROOT / image['path'] for image in images]], summary)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not (BASE / BATCH).exists() and not (HERE / 'local' / BATCH).exists()
        claim = reservations.claim('source43101-dated-review-' + str(uuid.uuid4()), ['building:landsd/43101:0', 'immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], 'Source reservation unavailable'
        execute_reserved(claim['reservation'], HERE / 'local' / BATCH / 'reservation.json', [sys.executable, __file__, '--owned'])
