"""Record the exact South Hillcrest source-wall interpretation and complete pair checks."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-south-hillcrest-physical-review-v1-20261022'
DOC = BASE / BATCH
SOURCES = {'landsd/198440:0': '11f518515180ca97e88c0f207075af73642e8ad57931ca5d4dd3b95e028e532e', 'landsd/259604:0': 'e6bbbe3fbfcc89ea9870c71a6541ef6edf7283a95f72cb0c1b4ef7f5a8cac375'}


def main():
    assert not DOC.exists()
    refs, cache = [Path(__file__)], {}
    def take(name, filename):
        if name not in cache:
            cache[name] = authenticate(BASE / name)[1]
            refs.append(BASE / name / 'result.json')
        path = BASE / name / filename
        assert digest(path.read_bytes()) == cache[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    runtime = 'government-xl-south-hillcrest-private-original-runtime-v3-20261022'
    selected = take(runtime, 'selection.json.gz')
    metrics = take(runtime, 'metrics.json')
    assert {r['uid']: r['sourceSHA256'] for r in selected['rows']} == SOURCES
    raw = []
    policy = module('south_hillcrest_review_policy', HERE / 'acceptance-policy.py')
    for row in metrics['rows']:
        uid = row['uid']
        identity = take('government-xl-south-hillcrest-current-identities-v1-20261022', uid.split('/')[1] + '/identity.json')
        assert identity['passed'] and not identity['reasons'] and identity['sourceSHA256'] == SOURCES[uid]
        reasons = policy.reasons(dict(state='runtime-validated-awaiting-acceptance', sourceSHA256=row['sourceSHA256'], identityProof=identity['proof']), row, metrics['profiles']['mobile'])
        assert reasons == (['terrain-intersects-source-over-0.5m'] if uid == 'landsd/259604:0' else ['ground-contact-unresolved'])
        raw.append(dict(uid=uid, reasons=reasons))
    scope = take('government-xl-south-hillcrest-private-original-scope-v2-20261022', 'scope.json')
    assert scope['currentNativeActors'] == 6836 and not scope['touchingNativeUids'] and not scope['terrainContacts']
    neighbours = take('government-xl-south-hillcrest-private-original-form-checks-v2-20261022', 'summary.json')
    assert neighbours['forms'] == scope['intersectingForms'] == 54 and not neighbours['flagged']
    pair = take('government-xl-south-hillcrest-pair-four-world-support-v1-20261022', 'summary.json')
    assert pair['allModesPassed'] and len(pair['rows']) == 4
    assert all(r['faces'] == r['covered'] == 15453 and r['buried'] == r['remainingUnexplained'] == 0 for r in pair['rows'])
    podium = take('government-xl-south-hillcrest-podium-four-world-foundations-v1-20261022', 'summary.json')
    assert len(podium['rows']) == 4 and all(r['triangles'] == r['completeTerrainTriangles'] == 1041 and r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0 for r in podium['rows'])
    context = take('government-xl-south-hillcrest-podium-clearance-attribution-v1-20261022', 'context.json')
    assert context['failedSamples'] == context['failedFaces'] == 4 and context['failedCentroids'] == context['upwardFailedFaceCount'] == 0
    assert {r['faceIndex'] for r in context['faces']} == {105, 106, 107, 108}
    assert len({tuple(r['position']) for r in context['samples']}) == 1
    assert context['maximumAbsoluteRenderedOriginalGroundDeltaM'] < .002
    assert all(abs(r['normalisedVertical']) < .002 for r in context['faces'])
    visual = 'government-xl-south-hillcrest-podium-wall-context-v1-20261022'
    take(visual, 'profiles.json')
    images = []
    for name in ['source-context.png', 'face-profiles.png']:
        path = BASE / visual / name
        sha = cache[visual][str(path.relative_to(ROOT))]
        assert digest(path.read_bytes()) == sha
        refs.append(path)
        images.append(dict(path=str(path.relative_to(ROOT)), sha256=sha))
    review = dict(uids=sorted(SOURCES), sourceSHA256ByUid=SOURCES, reviewer='Codex ROOT', sourceSpecificPhysicalInterpretationAccepted=True, sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False, rawPolicyReasons=raw, rawCanonicalFailuresPreserved=True, imagesActuallyViewed=images, sourceGeometryChanges=0, sourcePoseChanges=0, installationApproved=False, publicationApproved=False, basis='Four failed vertex samples refer to one original low corner shared by nearly vertical source wall faces105–108. No centroid or upward face fails. Original government terrain reproduces the approximately1.715m embedding; rendered height differs by less than2mm. Inspected whole-source context and individual face profiles show a small corner intersection with the ground while the original walls remain exposed. All1041podium faces are covered and none fully buried in original/literal/two explicit Float32 representations. Both original sources pass exact current identity; all15453tower faces and all support contacts pass in all four coordinate modes. All54base forms pass and no existing detailed actor/terrain patch touches the replacement domain. This accepts only the recorded source-authored wall-ground relationship; it does not alter the0.5m raw threshold.', scope='Exact two unchanged source revisions and private terrain-v2. Staged/live images, picking/collision/failure-retry, final source acceptance and guarded publication remain required.')
    save(DOC / 'ROOT-PHYSICAL-REVIEW.json', review)
    refs.append(HERE / 'acceptance-policy.py')
    module('south_hillcrest_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'source-specific-original-wall-ground-interpretation', refs, review)


if __name__ == '__main__':
    main()
