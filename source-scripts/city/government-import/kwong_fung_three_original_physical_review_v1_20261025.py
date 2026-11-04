"""Bounded review of the exact H143/93 originals; no geometry edits/publication."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-kwong-fung-three-original-physical-review-v1-20261025'
POD = 'landsd/229834:0'
SOURCES = {
    POD: '468fdbf5b58565b4b674fd3b815093dfca03f41766199e35f611bc531d991d29',
    'landsd/337316:0': '28fbf1ee9b232d42ea0ed99024479523fdb2427a71f4ebf8077a7aa2324d3962',
    'landsd/337318:0': '8715b74c26c061452df64b72088f47dd1da3842ec98e95e528caac5123c7f491',
}
COUNTS = {POD: 937, 'landsd/337316:0': 11641, 'landsd/337318:0': 9568}
SUPPORTS = {u: POD for u in SOURCES if u != POD}
RUNTIME = 'government-xl-kwong-fung-three-original-private-runtime-v1-20261025'
ATTRS = 'government-xl-kwong-fung-three-original-private-attributes-v1-20261025'
MODES = ['original', 'literal', 'leftF32', 'balancedF32']


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
    selection = take(RUNTIME, 'selection.json.gz')
    rows = {r['uid']: r for r in selection['rows']}
    assert {u: r['sourceSHA256'] for u, r in rows.items()} == SOURCES
    assert {u: r['triangles'] for u, r in rows.items()} == COUNTS
    attributes = take(ATTRS, 'attributes.json.gz')
    assert attributes['startEndAllInputsVerified']
    attrs = {r['uid']: r for r in attributes['rows']}
    geometry_path = HERE / 'local' / RUNTIME / 'runtime-geometry.json.gz'
    assert digest(geometry_path.read_bytes()) == pins[RUNTIME][str(geometry_path.relative_to(ROOT))]
    refs.append(geometry_path)
    geometry = {r['uid']: r for r in read(geometry_path)['rows']}
    worlds, forms = {}, {}
    helper = module('kwong_canonical_entry', HERE / 'xl-next-support-recovery-20261005.py')
    refs += [HERE / 'xl-next-support-recovery-20261005.py', HERE.parent / 'enhancement-screening/shape_prepare.py']
    identities = {}
    for u, row in rows.items():
        f = forms[u] = row['source']['building']
        assert f['structureType'] == ('Podium' if u == POD else 'Tower')
        tile = ROOT / '3d-viewer' / row['source']['tile']
        assert next(r for r in read(tile)['buildings'] if r['uid'] == u) == f
        refs.append(tile)
        canonical, _ = helper.diagnostic_entry(row['native'], f)
        canonical['asset'] = row['candidate']['entry']['asset']
        assert canonical == row['candidate']['entry'] and canonical['rootTranslation'] == [-834500, 0, 816500]
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == SOURCES[u] == attrs[u]['sourceSHA256'] == geometry[u]['sourceSHA256']
        refs.append(asset)
        a = attrs[u]; ix = np.asarray(a['completeOriginalIndex']).reshape(-1, 3)
        worlds[u] = {'original': decode_original_world_triangles(asset.read_bytes()), **{
            m: np.asarray(a[k]).reshape(-1, 3)[ix] for m, k in [
                ('literal', 'completeLiteralWorldPosition'), ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'),
                ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]}}
        assert all(len(t) == COUNTS[u] for t in worlds[u].values())
        raw = take('government-xl-kwong-fung-three-original-current-identity-v1-20261025', u.split('/')[1] + '/identity.json')
        assert raw['sourceSHA256'] == SOURCES[u] and raw['originalOwnership']['sourceGraphVerified']
        assert raw['exactCurrentComponentRoute']['qualified'] and raw['exactWholeCellCoverage']['covered']
        assert raw['freshCurrentIdentity']['exactObjectAndCSUID']
        assert set(raw['reasons']) == (set() if u == POD else {'fresh-current-spatial-bound:targetCoveredBySourceProjection', 'full-source-target-coverage'})
        assert raw['worldTrianglesSHA256'] == digest(worlds[u]['original'].astype('<f8').tobytes())
        identities[u] = raw
    assert len({f['parent'] for f in forms.values()}) == 1 and forms[POD]['parent']
    permit = take('government-xl-kwong-fung-three-original-complete-permit-v1-20261025')
    assert permit['permit'] == 'H143/93' and permit['exactSelectedPermitMembership']
    assert len(permit['completeStructureIDs']) == 3
    assert set(permit['completePermitCSUIDs']) == {f['buildingCSUID'] for f in forms.values()}
    primary = take('government-xl-kwong-fung-three-original-primary-records-v1-20261025', 'footprints.json')
    official = {r['attributes']['BuildingCSUID']: r['attributes'] for r in primary['features']}
    for f in forms.values():
        r = official[f['buildingCSUID']]
        assert r['Status'] == 'Active' and r['BuildingBlockType'] == f['structureType']
        assert r['BaseHeight'] == f['base'] and abs(r['TopHeight'] - f['base'] - f['height']) < 1e-8
    identity_context = take('government-xl-kwong-fung-three-original-identity-context-v1-20261025')
    assert identity_context['requiredOriginalAssembly'] == SOURCES
    assert all(r['completeAssemblyTargetCoverage'] >= .95 and r['completeAssemblyWholeCellCovered'] for r in identity_context['rows'])
    scope_name = 'government-xl-kwong-fung-three-original-current-scope-v1-20261025'
    scope = take(scope_name)
    model_forms = {}
    for row in scope['rows']:
        assert not row['nearbyNativeActors'] and row['currentNativeActorsChecked'] == 6921
        for r in take(scope_name, row['uid'].split('/')[1] + '-forms.json.gz'):
            model_forms[r['building']['uid']] = r['building']
    assert set(model_forms) == set(SOURCES) | {'landsd/84936:0', 'landsd/174224:0', 'landsd/213820:0', 'landsd/229409:0'}
    target = shapely.union_all([shapely.Polygon(f['rings'][0], f['rings'][1:]) for f in forms.values()])
    foreign_forms = shapely.union_all([shapely.Polygon(f['rings'][0], f['rings'][1:]) for u, f in model_forms.items() if u not in SOURCES])
    measures = []
    for mode in MODES:
        tri = np.concatenate([worlds[u][mode] for u in SOURCES])
        projection = shapely.union_all(shapely.polygons(tri[:, :, [0, 2]]))
        coverage = projection.intersection(target).area / target.area
        extent = float(shapely.distance(shapely.points(tri[:, :, [0, 2]].reshape(-1, 2)), target).max())
        foreign = projection.difference(target).intersection(foreign_forms).area
        assert coverage >= .95 and extent <= 10 and foreign <= 1
        measures.append(dict(mode=mode, compoundTargetCoverage=coverage, maximumExtentM=extent, unrelatedExcessM2=foreign))
    foundation = take('government-xl-kwong-fung229834-private-foundations-v1-20261025')
    assert len(foundation['rows']) == 4 and all(r['triangles'] == r['completeTerrainTriangles'] == 937 and r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0 and r['minimumGapM'] >= -.5 for r in foundation['rows'])
    rims = take('government-xl-kwong-fung229834-private-exact-rims-v1-20261025')
    assert len(rims['rows']) == 4 and all(r['passed'] and r['continuousClearanceLowerBoundM'] >= -.5 for r in rims['rows'])
    exact = take('government-xl-kwong-fung229834-private-complete-ground-v1-20261025')
    assert all(not r['exactAffectedFaces'] for r in exact['rows'])
    continuous = take('government-xl-kwong-fung-three-original-private-finite-continuous-v1-20261025')
    assert all(not r['continuousAffectedFaces'] and not r['wholeSourceUncoveredFaces'] for r in continuous['rows'])
    coverage = take('government-xl-kwong-fung-three-original-private-exact-coverage-v1-20261025')
    assert all(not r['stillUncoveredFaces'] for r in coverage['rows'])
    stricts, paths = {}, {}
    for u, expected_roots, expected_paths, affected in [('landsd/337316:0', 479, 37, 84), ('landsd/337318:0', 159, 38, 35)]:
        number = u.split('/')[1].split(':')[0]
        stricts[u] = strict = take(f'government-xl-kwong-fung{number}-original-pair-support-v1-20261025')
        assert strict['sourceSHA256ByUid'] == {u: SOURCES[u], POD: SOURCES[POD]}
        assert strict['supportedUid'] == u and strict['supportUid'] == POD
        for row in strict['rows']:
            mode = row['mode']
            for v in [u, POD]:
                assert row['sourceWorldSHA256ByUid'][v] == digest(worlds[v][mode].astype('<f8').tobytes())
            assert row['support']['strictContacts'] == expected_roots and len(row['support']['unresolved']) == expected_paths
            f = row['compoundFoundation']
            assert f['triangles'] == f['completeTerrainTriangles'] == COUNTS[u] and f['fullyBuriedTriangles'] == f['fullyBuriedUpwardTriangles'] == 0
        paths[u] = path = take(f'government-xl-kwong-fung{number}-strict-root-paths-v1-20261025')
        assert path['sourceSHA256ByUid'] == {u: SOURCES[u], POD: SOURCES[POD]}
        assert len(path['rows']) == 4 and all(r['targets'] == r['finiteAttachmentPaths'] == expected_paths and r['disconnected'] == r['aboveExistingEndpointCeiling'] == 0 for r in path['rows'])
        actual = np.asarray(geometry[u]['drawnGroundGeometry']).reshape(-1, 3, 3)
        assert all(t[:, :, 1].min() > actual[:, :, 1].max() for t in worlds[u].values()), 'Actual terrain cannot be excused as a podium junction'
        compound = take(f'government-xl-kwong-fung{number}-private-compound-clearance-v1-20261025')
        assert compound['sourceSHA256'] == SOURCES[u] and compound['supportSHA256'] == SOURCES[POD]
        assert len(compound['rows']) == 4 and all(len(r['exactAffectedFaces']) == affected for r in compound['rows'])
        if u.endswith('337318:0'):
            assert all(r['allAffectedWallLike'] and r['compoundCapPathsPassed'] and not r['negativeNonWallFaces'] for r in compound['rows'])
    basal = take('government-xl-kwong-fung337316-private-basal-junction-context-v1-20261025')
    assert basal['allFourContextsClassified'] and basal['sourceSHA256ByUid'] == {POD: SOURCES[POD], 'landsd/337316:0': SOURCES['landsd/337316:0']}
    assert len(basal['rows']) == 4 and all(r['negativeWallFaces'] == 51 and len(r['negativeNonWalls']) == 33 and r['allNegativeWallsHaveClearCapPaths'] and r['allNegativeNonWallsAreExactDownwardBasalClosures'] and not r['rawCanonicalCapPathsPassed'] for r in basal['rows'])
    pair = take('government-xl-kwong-fung-three-original-complete-pair-context-v1-20261025')
    assert pair['sourceSHA256ByUid'] == SOURCES and pair['completeUnorderedPairs'] == 3 and len(pair['rows']) == 12
    assert all((r['positiveSurfaceContacts'] > 0) == (POD in [r['uid'], r['peerUid']]) for r in pair['rows'])
    foreign = take('government-xl-kwong-fung-three-original-current-foreign-contacts-v1-20261025')
    assert foreign['foreignPairs'] == 10
    assert all(not m['allFiniteContactPairs'] and m['projectedOverlapAreaM2'] == 0 for r in foreign['rows'] if r['foreignUid'] not in SOURCES for m in r['modes'])
    terrain_name = 'government-xl-kwong-fung-three-original-private-patch-scope-v1-20261025'
    terrain_scope = take(terrain_name, 'scope.json')
    obligations = {f['uid']: f for f in take(terrain_name, 'form-obligations.json.gz')}
    assert len(obligations) == terrain_scope['intersectingForms'] == 29 and terrain_scope['currentNativeActors'] == 6921
    assert not terrain_scope['touchingNativeUids'] and terrain_scope['positiveAreaTerrainOverlaps'] == 0
    assert all(obligations[u] == f for u, f in model_forms.items())
    neighbours = take('government-xl-kwong-fung-three-original-private-form-checks-v1-20261025')
    assert neighbours['forms'] == 29 and neighbours['flagged'] == [] and neighbours['ordinaryFlagged'] == 0
    images = []
    for batch, names in [('government-xl-kwong-fung-three-original-source-views-v1-20261025', ['complete-original-assembly.png', 'base-only-diagnostic.png']), ('government-xl-kwong-fung-three-original-identity-context-v1-20261025', ['source-record-context.png'])]:
        take(batch)
        for name in names:
            path = BASE / batch / name
            assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
            refs.append(path); images.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] == scope['currentManifestSHA256']
    refs.append(manifest)
    proof = dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True)
    resources = {('building:' if u.startswith('landsd/') else 'source-form:') + u for u in obligations} | {'terrain:city/data/terrain.json'}
    result = dict(uids=sorted(SOURCES), sourceSHA256ByUid=SOURCES, requiredOriginalAssembly=SOURCES, supportByUid=SUPPORTS, retainedNativeUids=[], retainedCurrentBasicSupportUids=[], retainedBasicSupportDependencies=[], reviewer='ROOT', identityAccepted=True, identityProof=proof, identityProofByUid={u: proof for u in SOURCES}, sourceSpecificPhysicalInterpretationAccepted=True, completeNeighbourInterpretationAccepted=True, completeFourWorldFoundations=True, completeFourWorldSourceClearance=True, completeCurrentNeighbourChecks=29, currentManifest=dict(path=str(manifest.relative_to(ROOT)), sha256=digest(manifest.read_bytes())), leaseResources=sorted(resources), imagesActuallyViewed=images, rawIdentity=identities, rawSupportChecks=stricts, finiteOriginalSupportPaths=paths, compoundSpatialMeasures=measures, rawCanonicalFailuresPreserved=True, sourceGeometryChanges=0, sourcePoseChanges=0, sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False, terrainEdits=True, visualAcceptance=False, installationApproved=False, publication=False, interpretation=[
        'Exactly three current ObjectID/CSUID and source graph/component routes match the complete official H143/93 permit, the Tower/Podium roles and one building parent. ROOT inspected the complete source assembly, clipped base diagnostic and footprint/GeoRef image. Individual tower target-coverage negatives remain archived; the mandatory complete three-source assembly passes unchanged95percent/10m/1m2 compound limits and exact whole-cell tests. No unrelated actor is exempted by parent or permit.',
        'The original-TIN private inset clears the actual ground intersection without changing any building bytes/pose. All podium whole foundations, finite four-world clearance and rims pass. Complete22146-face current continuous coverage is proved. Old impossible floating witnesses remain archived; the exact finite fallback changes no clearance threshold.',
        'The two original towers have479 and159 strict contacts with the original podium. All37 and38 remaining probes have finite source-edge routes to strict roots without exceeding the existing endpoint ceiling. The ground lies below every tower source vertex in all four streams; the only remaining negative envelope is their own exact original podium. No BASIC proxy supplies native support.',
        'Block1 has35 original lower wall intersections, all with clear-cap paths. Block2 has51 such walls plus33 exactly downward horizontal closures at its complete global source minimum. These are the exact tower bottom closures embedded in its own original podium, not exposed upward floors or public ground surfaces. No whole/upward whole source burial occurs. ROOT accepts this bounded authored assembly junction while preserving raw minimum-gap/cap failures, every face and source pose. This is not a general size, wall, terrain-burial or engineering exemption.',
        'Complete original pairs in all four streams show tower-to-podium joins and no tower-to-tower surface contacts. All four unrelated neighbours have zero finite contact/projected overlap. All29 terrain-domain forms pass unchanged terrain checks; no existing native actor or positive-area terrain patch overlap is involved. Existing BASIC actors remain unsuppressed.',
        'Each tower must depend on this exact original podium UID/CSUID/SHA. This receipt permits private preview only. Actually inspected desktop/mobile own-source exports, picking/collision/failure/retry, joint activation, guarded publication, all old assets, global retained BASIC guards and full521 ledger readback remain mandatory.'
    ])
    save(out / 'ROOT-PHYSICAL-REVIEW.json', result)
    refs.append(HERE / 'exact_packed_world_geometry_20261009.py')
    module('kwong_physical_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'bounded-exact-kwong-fung-three-original-assembly-physical-review', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
