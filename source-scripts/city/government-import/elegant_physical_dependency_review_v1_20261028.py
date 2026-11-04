"""ROOT review of the exact composed original support graph and activation contract.

Consumes completed proofs; no geometry search, model edits or publication.
"""
import argparse
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved

BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-elegant-garden-'
BATCH = P + 'physical-dependency-review-v1-20261028'
MODES = {'original', 'literal', 'leftF32', 'balancedF32'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    out, local = BASE / BATCH, HERE / 'local' / BATCH
    leasepath = local / 'reservation.json'
    resourcepath = BASE / (P + 'sixteen-original-updated-terrain-plan-v1-20261028.json')
    resources = read(resourcepath)['resources']
    assert not out.exists()
    if not args.owned:
        assert not local.exists()
        claim = reservations.claim('root-composed-original-support-' + str(uuid.uuid4()),
                                   resources, batch=BATCH, ttl=1800)
        assert claim['ok']
        return execute_reserved(claim['reservation'], leasepath,
                                [sys.executable, __file__, '--owned'])
    lease = read(leasepath)
    assert reservations.owns(lease)
    refs, receipts, pins = [Path(__file__), resourcepath], {}, {}

    def take(suffix, name='summary.json'):
        folder = BASE / (P + suffix + '-20261028')
        if suffix not in pins:
            receipts[suffix], pins[suffix] = authenticate(folder)
            refs.append(folder / 'result.json')
        if name == 'result.json':
            return receipts[suffix]
        path = folder / name
        assert digest(path.read_bytes()) == pins[suffix][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take('sixteen-original-updated-runtime-v1', 'selection.json.gz')
    sources = {r['uid']: r for r in selection['rows']}
    assert len(sources) == 16
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    for row in sources.values():
        path = ROOT / row['candidate']['path']
        assert digest(path.read_bytes()) == row['sourceSHA256']
        refs.append(path)
    identity = take('identity-boundary-reviews-v1')
    assert identity['allSixteenSourceAssociationsQualified']
    applicability = take('224123-original-applicability-review-v2')
    assert applicability['sourceSpecificOriginalApplicabilityAccepted']
    assert applicability['sourceSHA256'] == sources['landsd/224123:0']['sourceSHA256']
    assert applicability['rawTopHeightConflictUnresolved']
    foundation_rows = []
    for uid in sorted(sources):
        suffix = 'final-foundation-' + uid.split('/')[1].split(':')[0] + '-v1'
        result = take(suffix, 'result.json')
        assert len(result['rows']) == 4
        for row in result['rows']:
            assert row['uid'] == uid and row['establishedFoundationPolicyPassed']
            assert row['fullyBuriedTriangles'] == row['fullyBuriedUpwardTriangles'] == 0
            assert row['completeTerrainTriangles'] == row['triangles'] == sources[uid]['triangles']
        foundation_rows.extend(result['rows'])
    support = take('final-sixteen-composed-support-v1')
    assert support['selfSupportExcluded'] and support['allOtherOriginalFacesIncluded']
    assert support['surveyedBasicSupportIncluded'] and support['terrainIncluded']
    assert len(support['rows']) == 64
    paths = []
    for suffix in ['remaining-eight-current-paths-v1', 'fortune-and-main-podium-current-paths-v1']:
        result = take(suffix)
        for row in result['rows']:
            assert row['unmappedWitnesses'] == 0
            assert row['endpointBoundedPaths'] == row['mappedWitnesses'] == row['currentWarnings']
        paths.extend(result['rows'])
    fourwall = take('current-four-wall-path-rebind-v1')
    assert len(fourwall['rows']) == 4
    assert all(r['verifiedExistingPaths'] == r['exactCurrentWarnings'] == 7 for r in fourwall['rows'])
    assert sum(r['endpointBoundedPaths'] for r in paths) + 28 == 552
    provenance = take('current-support-provenance-v1')
    graph = take('current-support-provenance-v1', 'actor-graph.json')
    components = take('current-component-support-v1')
    assert provenance['strictSamplesAttributed'] == 3252 and provenance['pathsAttributed'] == 552
    assert len(components['rows']) == 64
    for row in components['rows']:
        assert row['unmappedStrictSamples'] == 0
        assert not row['witnessComponentsWithoutTerrainRoute'] or (
            row['uid'] == 'landsd/173764:0' and row['witnessComponentsWithoutTerrainRoute'] == [0])
    rex = take('rex-surveyed-podium-support-v1')
    assert rex['supportUid'] == 'landsd/228592:0' and rex['supportBasicBeforeAfterClear']
    assert len(rex['rows']) == 4
    assert all(r['canonicalContacts'] == r['samples'] == 49 and r['stillUnresolved'] == 0 for r in rex['rows'])
    fixture = take('supported-activation-fixture-v2')
    assert fixture['supportProviderMetadataBound'] and fixture['allFourWorldProviderSetsAgree']
    assert fixture['nativeSupportGraphAcyclic'] and fixture['rexFreshProductionGeometryMatchesReviewed']
    assert set(fixture['activationGroup']) == set(sources)
    by_mode = {mode: {r['uid']: r['providers'] for r in graph['edges'] if r['mode'] == mode} for mode in MODES}
    assert all(set(rows) == set(sources) for rows in by_mode.values())
    assert all(rows == by_mode['original'] for rows in by_mode.values())

    def rooted(uid, trail=()):
        assert uid not in trail, 'Support cycle'
        if uid in ['drawn-terrain', 'landsd/228592:0']:
            return True
        providers = by_mode['original'][uid]
        return bool(providers) and all(rooted(p, (*trail, uid)) for p in providers)

    assert all(rooted(uid) for uid in sources)
    roles = take('remaining-interface-reviews-v1')
    assert roles['all28ViewsActuallyInspected'] and len(roles['boundedInterfaceReviews']) == 14
    assert all(r['interfaceRoleApproved'] for r in roles['boundedInterfaceReviews'])
    assert roles['retainedGrandScholarCanopyKept'] and roles['rawFloat32OnlyContactPreserved']
    louis = take('identity-boundary-reviews-v1', 'louis-opaque-source-joint-review.json')
    assert louis['boundaryInterfaceRoleApproved']
    matrix = take('activation-interference-matrix-v1')
    assert matrix['rows'] == 1824 and matrix['completeOriginalPairs'] == 120 and matrix['completeMixedPairs'] == 288
    activation = take('activation-plan-v1')
    assert activation['desktopMobilePlannerContractPassed'] and activation['plannerCases'] == 66
    lifecycle = take('supported-activation-browser-v3')
    assert lifecycle['browserPassed'] and lifecycle['cases'] == lifecycle['expectedCases'] == 17
    assert set(lifecycle['uids']) == set(sources)
    neighbours = take('sixteen-original-updated-neighbours-v1')
    assert len(neighbours['nativeRows']) == 9 and all(r['passed'] for r in neighbours['nativeRows'])
    assert len(neighbours['nativeResolved']) == 9
    # Retain root judgements separately from every diagnostic's raw false flags.
    result = dict(
        uids=sorted(sources), sourceSHA256ByUid={u: r['sourceSHA256'] for u, r in sources.items()},
        currentManifestSHA256=selection['manifestSHA256'],
        originalSupportDependencyRolesAccepted=True, composedPhysicalApplicabilityAccepted=True,
        exactPhysicalProviders=by_mode['original'], foundationRows=foundation_rows,
        retainedSurveyedBasicRoot=dict(uid='landsd/173764:0', supportUid=rex['supportUid'],
                                      strictContactsPerWorld=49, mustRemainBasic=True),
        sourceHeightConflictRetained=['landsd/224123:0'],
        basis=[
            'ROOT accepts the authored lower-bearing/opaque interface roles already individually reviewed, composed with all four coordinate-stream proofs. The 813 strict witnesses per world and all 138 finite endpoint-bounded paths per world account for the complete tested support sample set without changing height limits or source vertices.',
            'Every witness-bearing component has a provider route to drawn terrain, except Rex whose exact complete current surveyed BASIC podium separately passes49/49 in every world and is bound by retained-basic runtime metadata. The provider graph is acyclic and identical across all four streams.',
            'Unwitnessed detached original ornament/facade components remain preserved as authored details. They are not fabricated structural supports; this decision is original-model applicability, not structural engineering certification or a requirement that each air-conditioner independently touch terrain.',
            'All16 originals must activate together under the reviewed availability group. Native support dependencies are distinct from availability edges. Actual17case browser failure/retry/BaseOnly/eviction evidence verifies complete transitions and collision-map consistency, without a measured performance claim.',
            'This accepts the exact composed original support/dependency roles. It does not turn failed generic identity/coverage flags true, certify the unresolved224123recorded height, approve a terrain replacement or install assets. The3BASIC foundation qualifications, final visual qualification, canonical publisher and live readback remain separate mandatory gates.'
        ],
        originalDiagnosticNegativeFlagsOverwritten=False,
        sourceGeometryChanges=0, sourcePoseChanges=0,
        evidenceInterpretationUsedAI=True, aiGeometryModelling=False,
        terrainReplacementApproved=False, installationApproved=False, publication=False)
    save(out / 'summary.json', result)
    assert reservations.owns(lease)
    module('composed_support_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'root-composed-original-bearing-dependency-and-atomic-activation-review',
        list(dict.fromkeys(refs)), read(out / 'summary.json'))
    print('Composed original physical/dependency roles accepted; canonical publisher/live installation still pending.')


if __name__ == '__main__':
    main()
