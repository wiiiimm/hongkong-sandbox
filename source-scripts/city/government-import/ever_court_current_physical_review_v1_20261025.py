"""Bind Ever Court's exact original and current-scene evidence; no publication."""
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
PREFIX = 'government-xl-ever-court-current-'
BATCH = PREFIX + 'physical-review-v1-20261025'
UID = 'landsd/158003:0'
SHA = '9feaee0a9981f0ea7bbee401631a0e46ed77c58a04c7e1c0f98fb9fc2c9967fc'


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [HERE / __file__.split('/')[-1]], {}

    def take(batch, filename='summary.json'):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        path = BASE / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    runtime = PREFIX + 'inset-runtime-v1-20261025'
    selection = take(runtime, 'selection.json.gz')
    assert len(selection['rows']) == 1
    source = selection['rows'][0]
    assert source['uid'] == UID and source['sourceSHA256'] == SHA
    asset = ROOT / source['candidate']['path']
    assert digest(asset.read_bytes()) == SHA
    refs.append(asset)
    identity = take(PREFIX + 'identity-v1-20261025', '158003:0/identity.json')
    assert identity['sourceSHA256'] == SHA and identity['originalOwnership']['sourceGraphVerified']
    assert identity['originalOwnership']['originalRootName'] == 'B357132066201063C0'
    assert identity['exactCurrentComponentRoute']['qualified'] and identity['exactWholeCellCoverage']['covered']
    spatial = identity['freshCurrentIdentity']
    assert spatial['exactObjectAndCSUID'] and spatial['targetCoveredBySourceProjection'] > .995
    assert spatial['sourceExcessMaximumDistanceFromTargetM'] < 5
    assert 6 < spatial['sourceExcessCoveredByUnrelatedFormsM2'] < 6.2
    assert identity['exactRouteManifestSHA256'] == selection['manifestSHA256']
    expected_reasons = ['fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2', 'full-source-unrelated-overlap']
    assert identity['reasons'] == expected_reasons
    pre = PREFIX + 'inset-prephysical-v1-20261025'
    suite = take(pre)
    assert suite['status'] == 'prephysical-evidence-complete-awaiting-identity-and-browser'
    foundations = take(pre + '-foundations')['rows']
    assert len(foundations) == 4
    assert all(r['triangles'] == r['completeTerrainTriangles'] == 10759 and r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0 for r in foundations)
    rims = take(pre + '-rims')['rows']
    assert len(rims) == 4 and all(r['passed'] and r['completeSourceFaces'] == 10759 for r in rims)
    continuous = take(pre + '-continuous')['rows']
    assert len(continuous) == 1 and continuous[0]['wholeSourceUncoveredFaces'] == 0
    assert not continuous[0]['continuousAffectedFaces']
    coverage = take(pre + '-coverage')['rows']
    assert len(coverage) == 1 and not coverage[0]['stillUncoveredFaces']
    scope_name = PREFIX + 'inset-scope-v1-20261025'
    scope = take(scope_name, 'scope.json')
    forms = take(scope_name, 'form-obligations.json.gz')
    assert scope['currentNativeActors'] == 6911 and len(forms) == scope['intersectingForms'] == 25
    assert scope['touchingNativeUids'] == ['landsd/266918:0'] and scope['positiveAreaTerrainOverlaps'] == 0
    assert len(scope['terrainContacts']) == 1
    terrain = scope['terrainContacts'][0]
    assert terrain['coarseOverlapAreaM2'] == 0 and all(c['overlapAreaM2'] == 0 for c in terrain['packedContacts'])
    neighbours = take(PREFIX + 'inset-neighbours-v1-20261025')
    resolved = take(PREFIX + 'basic-supports-v1-20261025')
    assert resolved['allBasicFlagsResolved'] and resolved['allRetainedNativeChecksPassed']
    assert {p['uid']: p['supportUid'] for p in resolved['proofs']} == {'landsd/263574:0': 'landsd/227319:0', 'landsd/263773:0': 'landsd/226694:0'}
    assert neighbours['requiredNativeUids'] == neighbours['nativeResolved'] == ['landsd/266918:0']
    assert all(r['passed'] and r['terrain']['newlyWhollyBuried'] == r['terrain']['newlyUpwardWhollyBuried'] == 0 for r in neighbours['nativeRows'])
    model_scope = take(PREFIX + 'source-scope-v1-20261025')
    assert len(model_scope['rows']) == 1 and not model_scope['rows'][0]['nearbyNativeActors']
    contacts = take(PREFIX + 'foreign-contacts-v1-20261025')
    expected = {'landsd/146263:0': 0, 'landsd/226694:0': 21, 'landsd/227319:0': 118, 'landsd/263574:0': 0, 'landsd/263773:0': 19}
    assert contacts['foreignPairs'] == 5 and {r['foreignUid'] for r in contacts['rows']} == set(expected)
    for row in contacts['rows']:
        modes = [r for r in row['modes'] if r['mode'] != 'before-basic']
        assert len(modes) == 4 and all(r['completeSourceFaces'] == 10759 and r['positiveContactPairs'] == expected[row['foreignUid']] for r in modes)
    images = []
    for batch, names in [(PREFIX + 'source-views-v1-20261025', ['whole-source-plan.png', 'whole-source-perspectives.png'])] + [(PREFIX + f'contact-{uid}-views-v1-20261025', ['before-after-contact-context.png']) for uid in ['227319', '226694', '263773']]:
        take(batch)
        for name in names:
            path = BASE / batch / name
            sha = digest(path.read_bytes())
            assert pins[batch][str(path.relative_to(ROOT))] == sha
            refs.append(path)
            images.append(dict(path=str(path.relative_to(ROOT)), sha256=sha))
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    resources = {'building:' + f['uid'] for f in forms}
    resources.update(['building:' + UID, 'building:landsd/266918:0', 'terrain:city/data/terrain.json', 'terrain:' + terrain['url']])
    proof = dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True)
    result = dict(uids=[UID], sourceSHA256ByUid={UID: SHA}, requiredOriginalAssembly={UID: SHA}, supportByUid={}, retainedNativeUids=['landsd/266918:0'], retainedCurrentBasicSupportUids=[], retainedBasicSupportDependencies=[], reviewer='ROOT', identityAccepted=True, identityProof=proof, identityProofByUid={UID: proof}, sourceSpecificPhysicalInterpretationAccepted=True, completeNeighbourInterpretationAccepted=True, completeFourWorldFoundations=True, completeFourWorldSourceClearance=True, completeCurrentNeighbourChecks=25, currentManifest=dict(path=str(manifest.relative_to(ROOT)), sha256=digest(manifest.read_bytes())), leaseResources=sorted(resources), imagesActuallyViewed=images, rawIdentityReasons=expected_reasons, rawCanonicalFailuresPreserved=True, terrainEdits=True, sourceGeometryChanges=0, sourcePoseChanges=0, sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False, visualAcceptance=False, installationApproved=False, publication=False, interpretation=[
        'Exact source graph root, object ID, CSUID, current component route and complete GeoRef cell agree. Original covers 99.598 percent of its recorded footprint; the 4.8504m extension and 6.1815m2 foreign projection remain archived. ROOT inspected the complete plan and perspectives: the matching tall block has perimeter facade detail and lower extensions; this is a bounded source identity interpretation, not a changed global overlap limit.',
        'ROOT inspected all three before/after foreign-contact diagrams. The new contacts lie at adjoining BASIC podium/facade margins; the original is retained intact. Surface crossings alone are not source misidentification. All five foreign BASIC actors remain unchanged, with no inferred legal ownership, zero-volume-intersection claim, suppression, or support credit. Final actual browser appearance remains unapproved.',
        'The private original-TIN inset passes all four source representations, foundations, continuous whole-source coverage and exact rim limits without exemptions. All 25 terrain-domain forms are included. Two raw increased-ground-gap warnings are resolved only by the existing unchanged BASIC-to-BASIC podium proofs; these are neighbour evidence, not dependencies of Ever Court.',
        'Existing Mongkok terrain and original266918 only touch the closed terrain boundary, with zero positive-area overlap. Its full63844face regression passes with no change in burial. Preserve its catalogue, geometry and terrain bytes and require its own desktop/mobile day/night exports. Boundary contact is not permission to drop it from scope or omit a terrain lease.',
        'This receipt permits a guarded private browser run only. Exact catalogue/terrain publication, retained support guards, all old assets, fixed521 inventory, source picking, failure/retry and actual desktop/mobile exports remain separate mandatory checks.'
    ])
    save(out / 'ROOT-PHYSICAL-REVIEW.json', result)
    module('ever_court_review_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'bounded-current-ever-court-original-physical-review', refs, result)


if __name__ == '__main__':
    main()
