"""Bind ROOT's exact Fook Yat source interpretation to completed physical checks."""
from copy import deepcopy
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-fook-yat-original-physical-review-v1-20261022'
UID = 'landsd/139132:0'
SHA = '2f87351265d718c0b5423820e08beb2cca3c82752742bd9fdceed2c9232eb3b7'
NAMES = dict(runtime='government-xl-fook-yat-bounded-replacement-runtime-v1-20261022', identity='government-xl-fook-yat-current-complete-identity-v2-20261022', foundations='government-xl-fook-yat-four-world-foundations-v1-20261022', scope='government-xl-fook-yat-bounded-replacement-scope-v1-20261022', neighbours='government-xl-fook-yat-bounded-replacement-neighbours-v1-20261022', plots='government-xl-fook-yat-complete-original-identity-plots-v1-20261022')


def main():
    doc = BASE / BATCH
    assert not doc.exists()
    refs, bound = [Path(__file__)], {}
    for key, name in NAMES.items():
        receipt, pins = authenticate(BASE / name)
        bound[key] = pins
        refs.append(BASE / name / 'result.json')
    def take(key, filename):
        path = BASE / NAMES[key] / filename
        assert digest(path.read_bytes()) == bound[key][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    identity = take('identity', '139132:0/identity.json')
    assert identity['uid'] == UID and identity['sourceSHA256'] == SHA
    assert set(identity['reasons']) == {'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM', 'full-source-maximum-extent'}
    assert identity['originalOwnership']['sourceGraphVerified'] and identity['originalOwnership']['originalRootName'] == 'B338822187101063C0'
    assert identity['exactCurrentComponentRoute']['qualified'] and identity['exactCurrentComponentRoute']['uid'] == UID
    assert identity['exactWholeCellCoverage']['covered'] and identity['exactWholeCellCoverage']['wholeOriginalFacesAccounted'] == 11515
    context = take('identity', '139132:0/context.json')['identity']
    assert context['unrelatedIntersectingForms'] == 0 and context['sourceExcessCoveredByUnrelatedFormsM2'] == 0
    assert context['targetCoveredBySourceProjection'] > .99
    plots = take('plots', 'summary.json')
    assert plots['sourceSHA256'] == SHA and plots['completeSourceFaces'] == 11515
    assert plots['originalWorldSHA256'] == identity['worldTrianglesSHA256']
    inspected = []
    for filename in ['whole-source-plan.png', 'whole-source-perspectives.png']:
        path = BASE / NAMES['plots'] / filename
        sha = digest(path.read_bytes())
        assert sha == bound['plots'][str(path.relative_to(ROOT))]
        inspected.append(dict(path=str(path.relative_to(ROOT)), sha256=sha))
        refs.append(path)
    proof = dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True)
    interpreted = deepcopy(identity)
    interpreted.update(passed=True, reasons=[], proof=proof, rawIdentityVerbatim=deepcopy(identity), sourceIdentityReviewUsedAI=True, physicalAccepted=False, installationApproved=False, qualification='Exact Fook Yat original/form/world identity only. ROOT inspected both complete source diagrams: primary and lower wing outlines follow the current footprint; the distant excess consists of source-authored low-level extensions, with small facade offsets also visible. The whole original graph belongs to the exact uniquely routed government root. No other current building is overlapped. Retain the complete source, raw extent warnings and exact bindings; no global extent threshold change or source edit.')
    foundations = take('foundations', 'summary.json')['rows']
    assert {r['mode'] for r in foundations} == {'original', 'literal', 'explicitLeftF32', 'explicitBalancedF32'}
    assert all(r['triangles'] == r['completeTerrainTriangles'] == 11515 and r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0 for r in foundations)
    scope = take('scope', 'scope.json')
    assert scope['currentNativeActors'] == 6838 and not scope['touchingNativeUids'] and scope['positiveAreaTerrainOverlaps'] == 0 and scope['intersectingForms'] == 26
    neighbours = take('neighbours', 'summary.json')
    assert neighbours['forms'] == 26 and not neighbours['flagged'] and not neighbours['ordinaryFlagged']
    metrics = take('runtime', 'metrics.json')
    metric = next(r for r in metrics['rows'] if r['uid'] == UID)
    policy = module('fook_review_policy', HERE / 'acceptance-policy.py')
    assert not policy.reasons(dict(state='runtime-validated-awaiting-acceptance', sourceSHA256=SHA, identityProof=proof), metric, metrics['profiles']['mobile'])
    assert metric['missingTerrain'] == 0 and metric['maxSamplerDelta'] == 0 and metric['checks'] == 38910
    selection = take('runtime', 'selection.json.gz')
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    result = dict(uids=[UID], sourceSHA256ByUid={UID: SHA}, sourceSpecificPhysicalInterpretationAccepted=True, sourceIdentityAssemblyQualified=True, sourceSpecificBoundaryInterpretationAccepted=True, identityProof=proof, currentManifestSHA256=selection['manifestSHA256'], imagesActuallyViewed=inspected, reviewer='ROOT', identityOnlyReviewUsedAI=True, sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False, sourceGeometryChanges=0, sourcePoseChanges=0, completeFourWorldFoundations=True, completeCurrentNeighbourChecks=26, rawIdentityReasonsRetained=identity['reasons'], installationApproved=False, publication=False, qualification='Bounded original terrain restores ground contact with all26 current forms unchanged in quality and no installed native/terrain contacts. Four coordinate modes cover all11515 original faces without burial. Source-specific extent interpretation only; desktop/mobile browser, collision, picking, failure/retry and guarded installation remain required.')
    save(doc / 'ROOT-PHYSICAL-REVIEW.json', result)
    save(doc / 'reviewed-identity.json', interpreted)
    save(doc / 'expected-raw-identity.json', identity)
    refs.extend([HERE / 'acceptance-policy.py', HERE / 'selected_original_identity_v2.py'])
    module('fook_physical_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'fook-yat-exact-original-physical-review', refs, result)


if __name__ == '__main__':
    main()
