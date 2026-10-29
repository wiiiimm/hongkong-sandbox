"""Bind the complete unchanged depot original, coastal surface and two canopies."""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from conditional_canopy_install_contract_v1_20261029 import form_sha
from multi_conditional_canopy_install_contract_v1_20261029 import verify

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-depot120104-final-source-review-v1-20261029'
UID = 'landsd/120104:0'
SHA = '655eb47347eec12814da670830672cf5808a23bbb590e520b22b0d21f6ce360f'
P = 'government-xl-depot120104-'
CURRENT = 'government-xl-oceanwalk-depot-current-v1-20261029'


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def ref(path): return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))

    def take(batch, path):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    def doc(batch, name): return take(batch, BASE / batch / name)

    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_ref = ref(manifest)
    refs.append(manifest)
    identity = doc(CURRENT + '-identity', '120104:0/identity.json')
    route = identity['exactCurrentComponentRoute']
    assert route['qualified'] and not route['reasons'] and identity['originalOwnership']['sourceGraphVerified']
    assert identity['originalOwnership']['originalRootName'] == 'B162761882001063C0'
    assert identity['sourceSHA256'] == SHA and route['official']['objectId'] == route['source']['building']['objectId'] == 120104
    source_form = route['source']['building']
    assert source_form['buildingCSUID'] == '1627618820T20050430'
    tile = ROOT / '3d-viewer' / route['source']['tile']
    assert digest(tile.read_bytes()) == route['source']['tileSHA256']
    assert [b for b in read(tile)['buildings'] if b.get('buildingCSUID') == source_form['buildingCSUID']] == [source_form]
    refs.append(tile)
    runtime = P + 'three-member-runtime-v1-20261029'
    selected = doc(runtime, 'selection.json.gz')
    row, = selected['rows']
    assert row['uid'] == UID and row['sourceSHA256'] == SHA and selected['manifestSHA256'] == manifest_ref['sha256']
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == SHA
    refs.append(asset)
    attributes = doc(P + 'three-member-attributes-v1-20261029', 'attributes.json.gz')['rows'][0]
    old = next(r for r in doc(CURRENT + '-attributes', 'attributes.json.gz')['rows'] if r['uid'] == UID)
    for key in ['completeOriginalIndex', 'completeLiteralWorldPosition', 'completeExplicitLeftAssociatedFloat32WorldPosition', 'completeExplicitBalancedFloat32WorldPosition']:
        assert np.array_equal(np.asarray(old[key]), np.asarray(attributes[key]))
    foreign = doc(P + 'current-foreign-v1-20261029', 'summary.json')
    assert foreign['uids'] == [UID] and foreign['foreignPairs'] == 3
    foreign_rows = {r['foreignUid']: r for r in foreign['rows']}
    assert set(foreign_rows) == {'landsd/108740:0', 'landsd/177363:0', 'landsd/178180:0'}
    assert all(r['positiveContactPairs'] == 0 for r in foreign_rows['landsd/108740:0']['modes'])
    # BASIC geometry is generated from these exact fixed forms, independently
    # of terrain sampling. Recheck all captured production/input hashes before
    # reusing its unchanged finite contacts.
    basic = doc(P + 'current-foreign-v1-20261029', 'basic.json')
    for name, sha in basic['inputHashes'].items():
        assert digest((ROOT / name).read_bytes()) == sha
        refs.append(ROOT / name)
    foundations = doc(P + 'three-member-foundations-v1-20261029', 'summary.json')
    rims = doc(P + 'three-member-rims-v1-20261029', 'summary.json')
    assert foundations['establishedFoundationPolicyPassed'] and len(foundations['rows']) == len(rims['rows']) == 4
    assert all(r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0 for r in foundations['rows'])
    assert all(r['groundContactResolved'] for r in rims['rows'])
    scope = doc(P + 'three-member-scope-v1-20261029', 'scope.json')
    forms = doc(P + 'three-member-scope-v1-20261029', 'form-obligations.json.gz')
    byuid = {f['uid']: f for f in forms}
    assert len(byuid) == 4 and byuid[UID] == source_form
    assert scope['currentNativeActors'] == 7018 and not scope['touchingNativeUids'] and not scope['terrainContacts']
    neighbours = doc(P + 'three-member-neighbours-v1-20261029', 'summary.json')
    assert neighbours['forms'] == 4 and not neighbours['basicFlags'] and neighbours['completeScopeVerified']
    surface = doc(P + 'three-member-surface-v2-20261029', 'summary.json')
    assert surface['status'] == 'private-three-member-chain-surface-validator-passed' and len(surface['members']) == 3
    assert doc(P + 'exact-low-lineage-v1-20261029', 'summary.json')['exactActualLowFacetPreservationPassed']
    features, replacements = [], []
    for number in ['177363', '178180']:
        feature = doc(P + 'two-canopies-private-review-v1-20261029', 'ROOT-PRIVATE-CANOPY-REVIEW-' + number + '.json')
        fresh = doc(P + 'canopy' + number + '-primary-v1-20261029', 'summary.json')
        official = fresh['officialRecords'][UID]
        assert official['BuildingCSUID'] == source_form['buildingCSUID'] and official['BuildingID'] == source_form['buildingId']
        assert official['Status'] == 'Active' and official['BaseHeight'] == 5.6 and official['TopHeight'] == 19.1
        assert feature['exactBasicForm'] == byuid[feature['basicUid']] and feature['currentManifest'] == manifest_ref
        features.append(feature)
        replacements.append(dict(sourceUid=UID, basicUid=feature['basicUid'], sourceSHA256=SHA,
            sourceFormSHA256=form_sha(source_form), basicFormSHA256=form_sha(feature['exactBasicForm']), onlyWhileExactOwnerActive=True, approved=True))
    preview = P + 'two-canopies-private-preview-v1-20261029'
    reports, images = [], []
    for width in [390, 1280]:
        path = BASE / preview / str(width) / 'staged-browser.json'
        report = take(preview, path)
        assert report['passed'] and not report['errors']
        views = [r for r in report['views'] if 'time' in r]
        assert len(views) == 2
        for view in views:
            assert view['uid'] == UID and view['sourceSHA256'] == SHA and view['fullyFramed'] and view['solidAppearance'] and not view['fallbackFaces'] and view['pick'] == view['collision'] == UID
            assert view['suppressed'] == {f['basicUid']: dict(loaded=True, suppressed=True, detailedActive=False) for f in features}
        reports.append(ref(path))
        for time in [1500, 2200]:
            path = BASE / preview / str(width) / f'staged-landsd-120104-0-{width}-{time}-canvas.png'
            assert digest(path.read_bytes()) == pins[preview][str(path.relative_to(ROOT))]
            refs.append(path)
            images.append(ref(path))
    lifecycle = doc(P + 'two-canopies-lifecycle-v1-20261029', 'report.json')
    cat = take(preview, HERE / 'local' / preview / 'catalogue.json')
    basis = ('Exact original graph B162761882001063C0 and unique pinned native object/CSUID identify the complete depot original, including its long hall, crossing roof and authored canopy/column components. Fresh active provider object119923 retains the same stable CSUID1627618820T20050430, BuildingID1103044034 and surveyed5.6/19.1m heights; viewer/native object120104 is explicitly preserved rather than silently renumbered. Raw54.3802m excess/52.0367m centroid warnings remain recorded. Both estimated3m BASIC canopies are same-feature duplicates under the higher authored roofs, supported by fresh active unsurveyed-canopy records, complete component outlines and ROOT-inspected contact diagrams; raw roof/outline shortfalls are retained and are not structural support approval. Only those two basics hide while the exact source is active; failure/Base-only/Auto/eviction restores them. All four actual renderer coordinate modes have complete ground, zero buried/upward-buried facets and passing ordinary rim limits. Three canonical coastal terrain patches preserve the19600m2 absent area, root water masks and all14complete low parent facets unchanged. All7018installed native bounds and current terrain were scoped; no native or retained-terrain contacts were nominated. All4regional forms pass ordinary regressions; the other original depot building108740 remains unchanged with zero finite contacts. ROOT viewed all4current desktop/mobile day/night exports. This is bounded original-source and duplicate-feature interpretation, with no geometry fitting, scaling, simplification, AI remodelling or global tolerance exception.')
    common = dict(uids=[UID], sourceSHA256ByUid={UID: SHA}, reviewer='ROOT', currentManifest=manifest_ref,
        identityAccepted=True, sourceSpecificPhysicalInterpretationAccepted=True, completeNeighbourInterpretationAccepted=True,
        visualAcceptance=True, sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False,
        sourceEvidenceInterpretationUsedAI=True, installationApproved=False, publication=False,
        conditionalCanopyReplacements=replacements, qualification=basis)
    physical = dict(**common, identityProof=dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True),
        pinnedNativeViewerObjectId=120104, liveProviderObjectId=119923, stableBuildingCSUID=source_form['buildingCSUID'],
        rawIdentityDiagnosticsRetained=identity['reasons'], completeFourWorldFoundations=True, completeCurrentNeighbourChecks=4,
        currentNativeActors=7018, completeOriginalFaces=14623, retainedNativeUids=[], supportByUid={UID: []},
        ordinaryFoundationRows=foundations['rows'], ordinaryRimRows=rims['rows'],
        terrainCandidates=[m['candidate'] for m in surface['members']], globalClearanceExceptionsCreated=0)
    visual = dict(**common, imagesActuallyViewed=images, browserReports=reports,
        canopyLifecycleReport=ref(BASE / (P + 'two-canopies-lifecycle-v1-20261029') / 'report.json'),
        canopyFeatureReviews=[ref(BASE / (P + 'two-canopies-private-review-v1-20261029') / ('ROOT-PRIVATE-CANOPY-REVIEW-' + n + '.json')) for n in ['177363', '178180']])
    proof = verify(cat['models'], visual, physical, lifecycle, features, byuid)
    save(out / 'ROOT-SOURCE-REVIEW.json', visual)
    save(out / 'ROOT-PHYSICAL-REVIEW.json', physical)
    save(out / 'multi-canopy-contract.json', proof)
    result = dict(uids=[UID], sourceSHA256ByUid={UID: SHA}, identityAccepted=True,
        sourceSpecificPhysicalInterpretationAccepted=True, completeNeighbourInterpretationAccepted=True,
        visualAcceptance=True, sourceGeometryChanges=0, installationApproved=False, publication=False,
        nextStep='Guarded three-new-terrain-member and exact-two-canopy staging/live installation; preserve every existing global support, ledger and rollback guard.')
    refs.extend([HERE / 'multi_conditional_canopy_install_contract_v1_20261029.py', HERE / 'conditional_canopy_install_contract_v1_20261029.py'])
    module('depot_final_source_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'exact-original-depot-coastal-terrain-and-two-conditional-canopies-review', refs, result)


if __name__ == '__main__':
    main()
