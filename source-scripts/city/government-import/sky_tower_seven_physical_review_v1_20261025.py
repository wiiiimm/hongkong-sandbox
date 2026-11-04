"""Exact original Sky Tower assembly review; no geometry edits or publication."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-sky-tower-seven-original-current-'
POD = 'landsd/244686:0'
SOURCES = {
    POD: 'd7acf64587218e56f8b6bd2e63f0c30f6e5aa3fc0b3bd7345edda60808bb97d8',
    'landsd/255923:0': '8a681ee9bf382b5a06eba73f436cbb42293cfc703e274a04b15ba271139b4184',
    'landsd/255924:0': '183cff1d4ce8c07933dd1dbfc2bc2199f17ab671d3415a8f8337f50726cf7b1e',
    'landsd/255926:0': '964074ce3188ed571dfd2ceae45a609828a5f3875a35229976a7aeaecae1c3ea',
    'landsd/255927:0': '6113c474ee5224ba595302cae896a25792910df67d2d158ca2ae5ce62d7215e7',
    'landsd/255928:0': 'fbce527b5048298b3b7e595482ad17e815f59d3824462e1a6d079b1c1f99cc66',
    'landsd/256122:0': '3cc5bcbafe7ca5cae54ee11ec7c23871e36559de8706668f8b89b5c30ae14073',
}
SUPPORTS = {u: POD for u in SOURCES if u != POD}
COUNTS = dict(zip(SOURCES, [12466, 792, 766, 808, 800, 807, 778]))
PATHS = {'landsd/255923:0': 17, 'landsd/255924:0': 17, 'landsd/255926:0': 31,
         'landsd/255927:0': 18, 'landsd/255928:0': 20, 'landsd/256122:0': 36}
BATCH = 'government-xl-sky-tower-seven-original-physical-review-v1-20261025'


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, filename='summary.json'):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        path = BASE / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    runtime = P + 'runtime-v1-20261025'
    selection = take(runtime, 'selection.json.gz')
    rows = {r['uid']: r for r in selection['rows']}
    assert {u: r['sourceSHA256'] for u, r in rows.items()} == SOURCES
    assert {u: r['triangles'] for u, r in rows.items()} == COUNTS and sum(COUNTS.values()) == 17217
    for uid, row in rows.items():
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == SOURCES[uid]
        refs.append(asset)
        identity = take(P + 'identity-v1-20261025', uid.split('/')[1] + '/identity.json')
        assert identity['sourceSHA256'] == SOURCES[uid] and identity['originalOwnership']['sourceGraphVerified']
        assert identity['exactCurrentComponentRoute']['qualified'] and identity['exactWholeCellCoverage']['covered']
        assert identity['exactRouteManifestSHA256'] == selection['manifestSHA256']
        current = identity['freshCurrentIdentity']
        assert current['exactObjectAndCSUID']
        if uid == POD:
            assert identity['reasons'] == ['fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2', 'full-source-unrelated-overlap']
            assert current['targetCoveredBySourceProjection'] == 0.999767250757024
            assert current['sourceExcessMaximumDistanceFromTargetM'] == 3.7191643842458326
            assert current['sourceExcessCoveredByUnrelatedFormsM2'] == 42.894860158613476
        else:
            assert identity['passed'] and not identity['reasons']
            assert row['source']['building']['parent'] == rows[POD]['source']['building']['parent']
    pre = 'government-xl-sky-tower-podium244686-current-inset-prephysical-v1-20261025'
    assert take(pre)['status'] == 'prephysical-evidence-complete-awaiting-identity-and-browser'
    foundations = take(pre + '-foundations')['rows']
    assert len(foundations) == 4 and all(r['triangles'] == r['completeTerrainTriangles'] == 12466 and r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0 for r in foundations)
    rims = take(pre + '-rims')['rows']
    assert len(rims) == 4 and all(r['passed'] and r['continuousClearanceLowerBoundM'] >= -.5 for r in rims)
    assert not take(pre + '-coverage')['rows'][0]['stillUncoveredFaces']
    raw_support, finite_paths = {}, {}
    for uid in SUPPORTS:
        number = uid.split('/')[1].split(':')[0]
        strict = take(P + f'support-{number}-v1-20261025')
        assert strict['supportedUid'] == uid and strict['supportUid'] == POD
        assert strict['sourceSHA256ByUid'] == {uid: SOURCES[uid], POD: SOURCES[POD]}
        assert len(strict['rows']) == 4
        for row in strict['rows']:
            f = row['compoundFoundation']
            assert f['triangles'] == f['completeTerrainTriangles'] == COUNTS[uid]
            assert f['fullyBuriedTriangles'] == f['fullyBuriedUpwardTriangles'] == 0 and f['minimumGapM'] >= -.5
            assert row['support']['strictContacts'] >= 150 and len(row['support']['unresolved']) == PATHS[uid]
        paths = take(P + f'support-paths-{number}-v1-20261025')
        assert paths['allUnresolvedHaveFinitePaths'] and len(paths['rows']) == 4
        assert all(r['targets'] == r['verifiedPaths'] == PATHS[uid] and r['remaining'] == 0 for r in paths['rows'])
        clearance = take(P + f'compound-clearance-{number}-v1-20261025')
        assert clearance['sourceSHA256'] == SOURCES[uid] and clearance['supportSHA256'] == SOURCES[POD]
        assert len(clearance['rows']) == 4 and all(r['completeSourceFaces'] == COUNTS[uid] and r['noAffectedFaces'] and not r['exactAffectedFaces'] for r in clearance['rows'])
        raw_support[uid], finite_paths[uid] = strict, paths
    scope_name = 'government-xl-sky-tower-podium244686-current-inset-scope-v1-20261025'
    terrain_scope = take(scope_name, 'scope.json')
    forms = {f['uid']: f for f in take(scope_name, 'form-obligations.json.gz')}
    assert terrain_scope['currentNativeActors'] == 6912 and len(forms) == terrain_scope['intersectingForms'] == 58
    assert not terrain_scope['touchingNativeUids'] and not terrain_scope['terrainContacts'] and terrain_scope['positiveAreaTerrainOverlaps'] == 0
    model_scope = take(P + 'scope-v1-20261025')
    assert set(model_scope['uids']) == set(SOURCES)
    for row in model_scope['rows']:
        assert row['currentNativeActorsChecked'] == 6912 and not row['nearbyNativeActors']
        for f in take(P + 'scope-v1-20261025', row['uid'].split('/')[1] + '-forms.json.gz'):
            assert forms[f['building']['uid']] == f['building']
    neighbours = take('government-xl-sky-tower-podium244686-current-inset-neighbours-v2-20261025')
    resolution = take('government-xl-sky-tower-podium244686-current-neighbour-supports-v1-20261025')
    assert neighbours['forms'] == 58 and not neighbours['requiredNativeUids']
    assert resolution['rawBasicFlagsPreserved'] == neighbours['basicFlags']
    assert len(resolution['proofs']) == 3 and {p['uid']: p['supportUid'] for p in resolution['proofs']} == {u: 'landsd/226294:0' for u in ['landsd/13943:0', 'landsd/208860:0', 'landsd/245838:0']}
    assert {r['uid'] for r in resolution['remainingBasicFlags']} == set(SUPPORTS)
    assert all(r['reasons'] == ['increased-neighbour-ground-gap'] for r in resolution['remainingBasicFlags'])
    pairs = take(P + 'pair-context-v1-20261025')
    assert pairs['sourceSHA256ByUid'] == SOURCES and pairs['completeUnorderedPairs'] == 21 and len(pairs['rows']) == 84
    for row in pairs['rows']:
        if POD in [row['uid'], row['peerUid']]:
            assert not row['strictBoundsSeparated'] and row['positiveSurfaceContacts'] > 0
        elif not row['strictBoundsSeparated']:
            assert row['positiveSurfaceContacts'] == 0
    foreign = take(P + 'foreign-contacts-v1-20261025')
    assert foreign['foreignPairs'] == 38
    positive_external = set()
    for row in foreign['rows']:
        if row['foreignUid'] in SOURCES:
            continue  # Archived BASIC proxies are replaced by the exact originals tested above.
        positive = [m for m in row['modes'] if m['mode'] != 'before-basic' and m['positiveContactPairs']]
        if positive:
            assert row['uid'] == POD and len(positive) == 4
            positive_external.add(row['foreignUid'])
    assert positive_external == {'landsd/13943:0', 'landsd/226294:0', 'landsd/245838:0'}
    images = []
    image_batches = [
        ('government-xl-sky-tower-podium244686-current-source-views-v1-20261025', ['whole-source-plan.png', 'whole-source-perspectives.png']),
        ('government-xl-sky-tower-seven-original-assembly-views-v1-20261025', ['complete-original-assembly.png', 'base-only-diagnostic.png']),
        *[(P + f'contact-{u}-views-v1-20261025', ['before-after-contact-context.png']) for u in ['13943', '226294', '245838']],
    ]
    for batch, names in image_batches:
        take(batch)
        for name in names:
            path = BASE / batch / name
            sha = digest(path.read_bytes())
            assert sha == pins[batch][str(path.relative_to(ROOT))]
            refs.append(path)
            images.append(dict(path=str(path.relative_to(ROOT)), sha256=sha))
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] == model_scope['currentManifestSHA256']
    refs.append(manifest)
    resources = {('building:' if u.startswith('landsd/') else 'source-form:') + u for u in forms} | {'terrain:city/data/terrain.json'}
    proof = dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True)
    result = dict(uids=sorted(SOURCES), sourceSHA256ByUid=SOURCES, requiredOriginalAssembly=SOURCES, supportByUid=SUPPORTS, retainedNativeUids=[], retainedCurrentBasicSupportUids=[], retainedBasicSupportDependencies=[], reviewer='ROOT', identityAccepted=True, identityProof=proof, identityProofByUid={u: proof for u in SOURCES}, sourceSpecificPhysicalInterpretationAccepted=True, completeNeighbourInterpretationAccepted=True, completeFourWorldFoundations=True, completeFourWorldSourceClearance=True, completeCurrentNeighbourChecks=58, currentManifest=dict(path=str(manifest.relative_to(ROOT)), sha256=digest(manifest.read_bytes())), leaseResources=sorted(resources), imagesActuallyViewed=images, rawSupportChecks=raw_support, finiteOriginalSupportPaths=finite_paths, rawNeighbourFlags=neighbours['basicFlags'], unchangedForeignBasicSupportProofs=resolution['proofs'], rawCanonicalFailuresPreserved=True, sourceGeometryChanges=0, sourcePoseChanges=0, sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False, terrainEdits=True, visualAcceptance=False, installationApproved=False, publication=False, interpretation=[
        'All17217original faces belong to seven uniquely routed, graph-verified government actors. Six original towers independently pass the raw current identity checks and share the podium parent. The exact podium graph/currentCSUID/ObjectID/completeGeoRefcell agrees with99.9767percent target coverage; preserve its raw42.89486m2foreign projection and3.71917m extent. ROOT inspected complete podium plan/perspectives and the original seven-source assembly. The external projections are small authored facade/canopy margins, not evidence of a different owned source. No generic overlap threshold changes.',
        'Original-TIN localinset4941faces/22parentfaces clears219whole/110upwardwhole podium burial from coarse terrain. All four complete podium foundations, continuous clearance/coverage and exact rim proofs pass unchanged limits. Every original tower has complete terrain-plus-originalpodium foundation coverage, zero whole/upwardwhole burial and ordinary full exact compound clearance in all4representations.',
        'Each original tower has150+strict measured contacts with the unchanged original podium. All139remaining strict probes have verified finite original-surface paths in every representation. Raw direct-probe failures remain archived; no endpoint, building scale, pose, vertex or tolerance changes. Each tower must declare the exact original244686UID/CSUID/SHA as its dependency.',
        'The old58form terrain-only report keeps all9BASIC ground-gap flags. Three external BASIC neighbours13943/208860/245838 have exact unchanged226294BASIC-roof proofs. The remaining six rows are the six explicitly co-imported towers: their old BASIC proxies are replaced, and every actual original is separately tested against the actual original podium above. The suppressed244686BASIC fallback is never credited as an installed support. All raw reports remain unchanged; failed-download BASIC fallback/retry remains a mandatory browser check.',
        'All21unordered original pairs are checked in four representations. Only original podium/tower pairs have positive surface contacts; no tower pair has positive contact. Full before/after foreignBASIC contacts are archived, including superseded seven-source BASIC proxies. Only podium margins touch external13943/226294/245838. ROOT inspected all three two-angle before/after diagrams. These unchanged external actors remain unsuppressed; no engineering/common-property/zero-volume-intersection assertion is made.',
        'All58current terrain-domain forms and every model-only form are included under exact current source hashes. All6912native bounds are checked for each original; no external native or terrain overlap exists. This receipt permits guarded private desktop/mobile preview only. Actual appearance, picking/collision, failure/retry, exact publication/leases, alloldassets, globalretainedBASICguards and full521ledger readback remain mandatory.'
    ])
    save(out / 'ROOT-PHYSICAL-REVIEW.json', result)
    module('sky_tower_physical_review_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'bounded-exact-seven-source-sky-tower-original-assembly-physical-review', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
