"""Review D's immutable original with finite support and zero native contacts."""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-beverly-d-finite-source-review-v1-20261026'
CONFIG = BASE / 'government-xl-beverly-d-finite-independent-original-install-config-v1-20261026.json'


def main():
    out = BASE / BATCH
    assert not out.exists()
    cfg = read(CONFIG)
    refs, pins = [Path(__file__), CONFIG], {}

    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        p = BASE / batch / name
        assert digest(p.read_bytes()) == pins[batch][str(p.relative_to(ROOT))]
        refs.append(p)
        return read(p)

    uid = 'landsd/255541:0'
    selection = take(cfg['runtime'], 'selection.json.gz')
    source, = selection['rows']
    assert source['uid'] == uid and cfg['sources'] == {uid: source['sourceSHA256']}
    prior = take(cfg['identityReview'], 'ROOT-IDENTITY-REVIEW.json')
    raw = take('government-xl-beverly-d-after-a-identity-v1-20261026', '255541:0/identity.json')
    assert prior['identityOnlyApproved'] and prior['identityReviewApproved'] and prior['sourceSHA256'] == source['sourceSHA256']
    assert {k:v for k,v in raw.items() if k != 'exactRouteManifestSHA256'} == {k:v for k,v in prior['rawIdentityVerbatim'].items() if k != 'exactRouteManifestSHA256'}
    assert not raw['passed'] and set(raw['reasons']) == {'fresh-current-spatial-bound:targetCoveredBySourceProjection', 'full-source-target-coverage'}
    identity_proof = prior['identityProof']
    assert all(identity_proof.values())
    metrics = take(cfg['runtime'], 'metrics.json')
    policy = module('beverly_d_acceptance_policy', HERE / 'acceptance-policy.py')
    reasons = policy.reasons(dict(state='runtime-validated-awaiting-acceptance', sourceSHA256=source['sourceSHA256'], identityProof=identity_proof), metrics['rows'][0], metrics['profiles']['mobile'])
    assert reasons == ['ground-contact-unresolved'], reasons
    foundations = take('government-xl-beverly-d-after-a-foundations-v1-20261026', 'summary.json')
    assert foundations['establishedFoundationPolicyPassed'] and len(foundations['rows']) == 4
    assert all(r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0 and r['triangles'] == 14819 for r in foundations['rows'])
    continuous = take('government-xl-beverly-d-after-a-continuous-v1-20261026', 'summary.json')['rows'][0]
    assert continuous['wholeSourceFaces'] == 14819 and continuous['wholeSourceUncoveredFaces'] == 0 and not continuous['continuousAffectedFaces']
    scope = take(cfg['scope'], 'summary.json')
    forms = {r['building']['uid']:r['building'] for r in take(cfg['scope'], '255541:0-forms.json.gz')}
    assert set(forms) == {uid, 'landsd/233218:0', 'landsd/255544:0', 'landsd/70279:0'}
    assert scope['rows'][0]['currentNativeActorsChecked'] == cfg['currentNativeActors'] == 6958
    finite = take(cfg['finiteEvidence'], 'finite-basic-evidence.json')
    bindings = take(cfg['finiteEvidence'], 'support-bindings.json')
    assert finite['verifiedFinitePaths'] == 196 and finite['completeFourWorldCanonicalRetainedBasicSupport'] is False
    assert bindings[0]['currentBasicForm'] == forms['landsd/233218:0']
    native = take(cfg['nativeContext'], 'summary.json')['rows']
    assert len(native) == 1 and native[0]['uid'] == uid and native[0]['nativeUid'] == 'landsd/255544:0'
    entry = native[0]['rawCurrentNativeEntry']
    assert entry['publicationApproved'] is False
    assert len(native[0]['modes']) == 4 and all(m['finiteContactPairs'] == 0 for m in native[0]['modes'])
    fallback = take(cfg['nativeFallbackContext'], 'summary.json')['rows']
    assert len(fallback) == 1 and all(m['finiteContactPairs'] == 0 for m in fallback[0]['modes'] if m['mode'] != 'before-basic')
    foreign_batch = 'government-xl-beverly-d-after-a-foreign-basics-v1-20261026'
    foreign = take(foreign_batch, 'summary.json')['rows']
    assert {r['foreignUid'] for r in foreign} == {'landsd/233218:0', 'landsd/70279:0'}
    assert all(m['allFiniteContactPairs'] == 0 for r in foreign if r['foreignUid'] == 'landsd/70279:0' for m in r['modes'])
    basic = next(r for r in take(foreign_batch, 'basic.json')['rows'] if r['uid'] == 'landsd/70279:0')
    shelter = np.asarray(basic['position']).reshape(-1, 3)[np.asarray(basic['index']).reshape(-1, 3)]
    assert float(shelter[:, :, 1].max()) == prior['unrelatedShelterMaximumY'] and prior['sourceAboveCompleteShelterByM'] > 10
    reports, images, retained_images = [], [], []
    for width in [390, 1280]:
        report = take(cfg['browser'], str(width) + '/staged-browser.json')
        assert report['passed'] and not report['errors']
        p = BASE / cfg['browser'] / str(width) / 'staged-browser.json'
        reports.append(dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())))
        for v in [v for v in report['views'] if 'time' in v] + report['retainedNativeOwnViews']:
            path = p.parent / v['file']
            assert digest(path.read_bytes()) == pins[cfg['browser']][str(path.relative_to(ROOT))]
            refs.append(path)
            image = dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))
            (images if v['uid'] == uid else retained_images).append(image if v['uid'] == uid else dict(**image, uid=v['uid'], width=width, time=v['time']))
    assert len(images) == len(retained_images) == 4
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] == scope['currentManifestSHA256'] == raw['exactRouteManifestSHA256']
    refs.append(manifest)
    review = dict(uids=[uid], sourceSHA256ByUid=cfg['sources'], sourceSpecificPhysicalInterpretationAccepted=True,
                  identityAccepted=True, completeNeighbourInterpretationAccepted=True, completeFourWorldSourceClearance=True,
                  completeFourWorldCanonicalRetainedBasicSupport=False, completeFourWorldFiniteRetainedBasicSupport=True,
                  completeCurrentNeighbourChecks=4, identityProof=identity_proof, identityProofByUid={uid:identity_proof},
                  sourceSpecificIdentityReview=dict(path=str((BASE / cfg['identityReview'] / 'ROOT-IDENTITY-REVIEW.json').relative_to(ROOT)), sha256=digest((BASE / cfg['identityReview'] / 'ROOT-IDENTITY-REVIEW.json').read_bytes())),
                  freshRawIdentityVerbatim=raw, rawIdentityReasonsRetained=raw['reasons'], freshAutomaticIdentityStillRejected=True,
                  exactPriorIdentityInputsUnchangedExceptManifest=True,
                  currentManifest=dict(path=str(manifest.relative_to(ROOT)), sha256=digest(manifest.read_bytes())),
                  retainedCurrentBasicSupportUids=['landsd/233218:0'], retainedBasicSupportDependencies=bindings,
                  leaseResources=sorted('building:' + u for u in forms), terrainEdits=False, sourceGeometryChanges=0,
                  sourcePoseChanges=0, installationApproved=False, publication=False, visualAcceptance=True,
                  originalSourceReviewAccepted=True, imagesActuallyViewed=images, retainedImagesActuallyViewed=retained_images,
                  browserReports=reports, retainedNativeEntries={entry['uid']:entry}, runtimeAvailabilityDependenciesByUid={},
                  sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False,
                  qualification=cfg['placementReview'] + ' ROOT opened all8 individual private exports: D4 and C4 at both widths/daynight. D roofs/facades/podium interfaces readable. C roofs/mostfacades remain readable; an existing foreground BASIC building partially occludes lower central C surfaces, disclosed as normal scene occlusion, not D geometry or a new collision. Native C asset/wholeentry/publicationApproved:false remain unchanged and are not reapproved. Original light-grey/darknight materials and surrounding BASIC windows retained. No new static visible defect observed. Raw footprint failure remains verbatim and the automatic95% rule stays unchanged. Separate guarded publication/live review/full readback mandatory.')
    from finite_basic_native_independent_admission_v1_20261026 import replay
    refs.extend(replay(cfg, review))
    save(out / 'ROOT-PHYSICAL-REVIEW.json', review)
    save(out / 'ROOT-SOURCE-REVIEW.json', review)
    refs.extend([HERE / 'acceptance-policy.py', HERE / 'test_finite_basic_native_independent_admission_v1_20261026.py'])
    module('beverly_d_finite_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'bounded-original-finite-v2-support-zero-native-contact-and-exact-reviewed-identity', list(dict.fromkeys(refs)), review)


if __name__ == '__main__':
    main()
