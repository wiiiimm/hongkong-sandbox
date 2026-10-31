"""Bounded ROOT interpretation of three immutable official components; no publication."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

PREFIX = 'government-xl-dragon-after-podium323546-'
SOURCES = {'landsd/226794:0': '84bf084baee2bf710240afd7181f607559731aa0688af9fe36bfed4de1b34bc4',
           'landsd/232428:0': 'd9eb8bea76a4dcfe5ba44de231686641d952957ac741c1ae1db955d4219b5218',
           'landsd/95231:0': '85c87026fda19d12215d63d77a4cd3e0ec6c59813ebece3ae0aadc746d1d1bbb'}


def main():
    base = ROOT / 'docs/astra-city/government-import'
    batch = PREFIX + 'three-identity-physical-review-v1-20261026'; out = base / batch
    assert not out.exists(); refs = [Path(__file__)]; pins = {}
    def take(suffix, name='summary.json'):
        folder = base / (PREFIX + suffix + '-20261026')
        if folder.name not in pins:
            pins[folder.name] = authenticate(folder)[1]; refs.append(folder / 'result.json')
        path = folder / name
        assert digest(path.read_bytes()) == pins[folder.name][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    selection = take('three-original-ground-v1', 'selection.json.gz')
    assert {r['uid']: r['sourceSHA256'] for r in selection['rows']} == SOURCES
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']; refs.append(manifest)
    raw = take('three-identity-v1'); identities = []
    for r in raw['rows']:
        uid = r['uid']; detail = take('three-identity-v1', uid.split('/')[1] + '/identity.json')
        assert detail['sourceSHA256'] == SOURCES[uid]
        assert detail['exactCurrentComponentRoute']['qualified'] and detail['originalOwnership']['sourceGraphVerified']
        assert detail['freshCurrentIdentity']['exactObjectAndCSUID']
        assert not r['passed'] and r['reasons']
        identities.append(dict(uid=uid, sourceSHA256=SOURCES[uid], rawPassed=False, rawReasons=r['reasons'],
            originalRoot=detail['originalOwnership']['originalRootName'], sourceFormSHA256=detail['sourceFormSHA256'],
            worldTrianglesSHA256=detail['worldTrianglesSHA256'], rawFreshCurrentIdentity=detail['freshCurrentIdentity']))
    context = take('three-identity-context-v1')
    assert context['requiredOriginalAssembly'] == SOURCES
    assert all(r['completeAssemblyWholeCellCovered'] for r in context['rows'])
    primary = take('three-primary-v1')
    assert primary['footprints'] == 3 and not primary['missingRequestedCSUIDs'] and primary['structureIDs'] == [587906, 756403]
    rebind = take('three-retained-numerics-v1')
    assert rebind['allFourWorldSourceAttributesIdentical'] and rebind['allActualLiteralSourceAndDrawnGroundInputsIdentical']
    for suffix in ['226794-foundations-v1', '232428-foundations-v1', 'corner-foundation-v1']:
        foundation = take(suffix); assert foundation['establishedFoundationPolicyPassed']
        assert len(foundation['rows']) == 4 and all(r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0 for r in foundation['rows'])
    compound = take('compound-clearance-v1')
    assert all(r['compoundCapPathsPassed'] and not r['negativeNonWallFaces'] and len(r['exactAffectedFaces']) == 19 for r in compound['rows'])
    corner = take('corner-compound-v1')
    assert all(r['noAffectedFaces'] and not r['exactAffectedFaces'] and not r['negativeNonWallFaces'] for r in corner['rows'])
    for suffix, expected in [('root-paths-v1', 40), ('corner-paths-v1', 6)]:
        paths = take(suffix)
        assert len(paths['rows']) == 4 and all(r['targets'] == r['finiteAttachmentPaths'] == expected and r['disconnected'] == r['aboveExistingEndpointCeiling'] == 0 for r in paths['rows'])
        assert paths['supportApproved'] is False
    pair = take('original-pair-contacts-v1'); cornerpair = take('podium-corner-contacts-v1')
    assert all(r['areaContactPairs'] == 0 and r['allPairsExamined'] and r['sourceFacesOmitted'] == 0 for r in pair['rows'] + cornerpair['rows'])
    native = take('three-empty-native-v1'); assert native['emptyNativeContactSetProved'] and native['rows'] == []
    scope = take('three-scope-v1'); forms = set()
    for r in scope['rows']:
        assert r['currentNativeActorsChecked'] == 6962 and not r['nearbyNativeActors']
        forms.update(f['building']['uid'] for f in take('three-scope-v1', r['uid'].split('/')[1] + '-forms.json.gz'))
    foreign = take('three-foreign-v1'); assert foreign['foreignPairs'] == 25
    # No external BASIC actor is suppressed or promoted to a support dependency.
    external = [r for r in foreign['rows'] if r['foreignUid'] not in SOURCES]
    assert {r['foreignUid'] for r in external if any(m['positiveContactPairs'] for m in r['modes'] if m['mode'] == 'original')} == {'landsd/97448:0','landsd/97821:0','landsd/232806:0','landsd/233209:0'}
    viewed = []
    for suffix, names in [('official-basemap-v1', ['official-map-comparison.png']), ('three-source-views-v1', ['complete-original-assembly.png', 'base-only-diagnostic.png']), ('three-identity-context-v1', ['source-record-context.png']), ('foreign-interface-views-v1', ['232428--97448-0.png','232428--97821-0.png','232428--232806-0.png','232428--233209-0.png','232428--95231-0.png','232428--226794-0.png'])]:
        take(suffix)
        for name in names:
            path = base / (PREFIX + suffix + '-20261026') / name
            assert digest(path.read_bytes()) == pins[path.parent.name][str(path.relative_to(ROOT))]
            refs.append(path); viewed.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    review = dict(uids=sorted(SOURCES), sourceSHA256ByUid=SOURCES, requiredOriginalAssembly=SOURCES,
        currentManifest=dict(path=str(manifest.relative_to(ROOT)), sha256=digest(manifest.read_bytes())), identityAccepted=True,
        identityReviewScope='Faithful imports of three exact official source components only; no property ownership or photographic completeness assertion.',
        identityRows=identities, rawAssemblyIdentityContext=context,
        identityInterpretation='Exact model roots, unique current CSUID/component routes, original graph ownership, fresh primary footprints and inspected source/map context identify these three source components. The tower original has the same central slab and two semicircular projections as the official block context. The original podium contains the stepped deck and open-sided edge geometry, rather than the full extruded footprint envelope; retain its93.197percent footprint coverage and60.8794m2 uncovered record area. The small corner original is offset by less than1m in the footprint-outline diagnostic and occupies the inspected podium corner; preserve68.53percent individual coverage and its original cell failure. All three cells are covered by the exact original assembly, but assembly coverage does not rewrite individual tests. Distinct official structure IDs587906/756403 and the corner missing relation are not shared-ownership evidence. No scale or position correction is made.',
        sourceSpecificPhysicalInterpretationAccepted=True, completeNeighbourInterpretationAccepted=True,
        physicalReviewScope='Bounded original-source wall/deck interface and runtime availability interpretation; not structural certification or a collision-free claim.',
        physicalInterpretation='The complete inspected source assembly joins the tall slab and small cuboid at the stepped original podium. The19 affected tower walls have exact paths to clear caps in all four coordinate representations; no upward or whole-face terrain burial occurs. Both supported components have finite source attachment paths, including all40/6 strict unresolved samples. The small cuboid has no negative compound faces; its false empty-set cap-path aggregate is retained and no path is required for an empty affected set. Original pair line intersections are kept unchanged. Availability edges require the exact podium before either upper component; contact alone is not ownership evidence.',
        neighbourInterpretation='Four external BASIC actors remain: two low open-sided structures under/along podium edges and two adjoining podium boundary interfaces. Complete inspected source/BASIC diagrams retain their20/16/8/7 original positive contact pairs versus18/28/34/54 before-BASIC pairs. These are retained source/fallback intersections, not collision-free claims. The corner BASIC conflict is replaced by its identified original, whose5 original-podium positive contacts replace the14 original-podium/BASIC-corner contacts. All25 scoped foreign pairs remain in the receipt; no BASIC actor is hidden or granted support credit. All6962 installed native bounds are disjoint from each selected source with the established margin.',
        supportByUid={'landsd/226794:0':'landsd/232428:0','landsd/95231:0':'landsd/232428:0'},
        retainedCurrentBasicSupportUids=[], retainedBasicSupportDependencies=[], completeFourWorldSourceClearance=True,
        leaseResources=sorted('building:' + u for u in forms), terrainEdits=False,
        rawStrictSupportApproved=False, rawWarningsPreserved=True, originalInterfacesCollisionFree=False,
        inspectedSourceImages=viewed, sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False,
        sourceGeometryChanges=0, sourcePoseChanges=0, visualAcceptance=False, installationApproved=False, publication=False,
        qualification='Exact-source bounded ROOT evidence interpretation; automatic identity/support guards and every raw failure remain unchanged. Private desktop/mobile original exports must be separately opened and reviewed. Canonical publisher, exact rendering metadata/dependencies, lease/rollback, live checks and independent full521/old6962 readback remain mandatory. No installed credit.')
    save(out / 'ROOT-PHYSICAL-REVIEW.json', review)
    module('dragon_identity_physical_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch, 'bounded-three-original-source-identity-and-physical-interface-interpretation', refs, review)


if __name__ == '__main__':
    main()
