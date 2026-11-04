"""Bounded source/physical review of two exact unedited originals; no publication."""
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_source_assembly_diagnostic import COVERAGE_REASONS

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-unnamed276873-original-physical-review-v1-20261025'
TOWER, PODIUM = 'landsd/276873:0', 'landsd/275792:0'
SOURCES = {TOWER: '1ab145d9f584ac5e839a2841e0d5fef8b3b465fce51fee8058441e15ca3f2d3c',
           PODIUM: '1c8d63c502c8e2bcca1eed8579c2111a9e9ffe6003b26f5991cd472d52f80404'}
FACES = {TOWER: 10508, PODIUM: 577}
RUNTIME = 'government-xl-unnamed276873-two-original-ground-v1-20261025'
OLD_RUNTIME = 'government-xl-next-three-pairs-current-ground-v1-20261025'
ATTRIBUTES = 'government-xl-next-three-pairs-render-attributes-v1-20261025'
IDENTITY = 'government-xl-next-three-pairs-current-identity-v1-20261025'
MODES = ['original', 'literal', 'leftF32', 'balancedF32']


def normal(triangle):
    p, q, r = [[F.from_float(float(v)) for v in x] for x in triangle]
    a, b = [[t[i]-p[i] for i in range(3)] for t in [q, r]]
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def main():
    doc = BASE / BATCH
    assert not doc.exists()
    refs, pins = [Path(__file__)], {}
    def take(batch, path):
        if batch not in pins:
            _, pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selection = take(RUNTIME, BASE / RUNTIME / 'selection.json.gz')
    rows = {r['uid']: r for r in selection['rows']}
    assert set(rows) == set(SOURCES)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    forms = {u: r['source']['building'] for u, r in rows.items()}
    assert forms[TOWER]['structureType'] == 'Tower' and forms[PODIUM]['structureType'] == 'Podium'
    assert forms[TOWER]['parent'] == forms[PODIUM]['parent'] and forms[TOWER]['parent']
    attributes = take(ATTRIBUTES, BASE / ATTRIBUTES / 'attributes.json.gz')
    assert attributes['startEndAllInputsVerified']
    attrs = {r['uid']: r for r in attributes['rows']}
    geometry = {r['uid']: r for r in take(RUNTIME, HERE / 'local' / RUNTIME / 'runtime-geometry.json.gz')['rows']}
    previous_geometry = {r['uid']: r for r in take(OLD_RUNTIME, HERE / 'local' / OLD_RUNTIME / 'runtime-geometry.json.gz')['rows']}
    worlds, raw_identity = {}, {}
    helper = module('unnamed_source_entry', HERE / 'xl-next-support-recovery-20261005.py')
    refs.extend([HERE / 'xl-next-support-recovery-20261005.py', HERE.parent / 'enhancement-screening/shape_prepare.py'])
    for u, r in rows.items():
        assert r['sourceSHA256'] == SOURCES[u] == attrs[u]['sourceSHA256']
        assert r['triangles'] == FACES[u]
        path = ROOT / r['candidate']['path']
        assert digest(path.read_bytes()) == SOURCES[u]
        refs.append(path)
        source_tile = ROOT / '3d-viewer' / r['source']['tile']
        assert next(b for b in read(source_tile)['buildings'] if b['uid'] == u) == forms[u]
        refs.append(source_tile)
        canonical, _ = helper.diagnostic_entry(r['native'], forms[u])
        canonical['asset'] = r['candidate']['entry']['asset']
        assert canonical == r['candidate']['entry'] and canonical['rootTranslation'] == [-834500, 0, 816500]
        assert geometry[u] == previous_geometry[u], 'Do not transfer stale ground/geometry evidence'
        g = attrs[u]
        ix = np.asarray(g['completeOriginalIndex']).reshape(-1, 3)
        worlds[u] = {'original': decode_original_world_triangles(path.read_bytes()), **{
            mode: np.asarray(g[field]).reshape(-1, 3)[ix] for mode, field in [
                ('literal', 'completeLiteralWorldPosition'), ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'),
                ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]}}
        assert all(len(t) == FACES[u] for t in worlds[u].values())
        raw = take(IDENTITY, BASE / IDENTITY / u.split('/')[1] / 'identity.json')
        assert raw['sourceSHA256'] == SOURCES[u] and raw['exactCurrentComponentRoute']['qualified']
        assert not set(raw['reasons']) - COVERAGE_REASONS
        assert raw['originalOwnership']['sourceGraphVerified'] and raw['exactWholeCellCoverage']['covered']
        assert raw['geographicCell']['targetCoversWholeCell'] and raw['geographicCell']['originalProjectionCoversWholeCell']
        assert raw['worldTrianglesSHA256'] == digest(worlds[u]['original'].astype('<f8').tobytes())
        raw_identity[u] = raw
    primary = 'government-xl-unnamed276873-pair-primary-records-v1-20261025'
    footprints = take(primary, BASE / primary / 'footprints.json')['features']
    official = {f['attributes']['BuildingCSUID']: f['attributes'] for f in footprints}
    assert set(official) == {f['buildingCSUID'] for f in forms.values()}
    for f in forms.values():
        record = official[f['buildingCSUID']]
        assert record['Status'] == 'Active' and record['BuildingBlockType'] == f['structureType']
        assert record['BaseHeight'] == f['base'] and abs(record['TopHeight']-(f['base']+f['height'])) < 1e-8
    permit_batch = 'government-xl-unnamed276873-pair-complete-permit-v1-20261025'
    permit = take(permit_batch, BASE / permit_batch / 'summary.json')
    assert permit['permit'] == 'HK37/2021(OP)' and permit['exactSelectedPermitMembership']
    assert set(permit['completePermitCSUIDs']) == set(official) and len(permit['completeStructureIDs']) == 2
    scope_batch = 'government-xl-next-three-pairs-model-only-scope-v1-20261025'
    scope = take(scope_batch, BASE / scope_batch / 'summary.json')
    obligations = {}
    for r in [r for r in scope['rows'] if r['uid'] in SOURCES]:
        assert r['currentNativeActorsChecked'] == 6919 and not r['nearbyNativeActors']
        for f in take(scope_batch, BASE / scope_batch / (r['uid'].split('/')[1]+'-forms.json.gz')):
            obligations[f['building']['uid']] = f['building']
    assert obligations == forms
    target = shapely.union_all([shapely.Polygon(f['rings'][0], f['rings'][1:]) for f in forms.values()])
    pair_batch = 'government-xl-unnamed276873-two-original-pair-context-v1-20261025'
    measures = []
    for mode in MODES:
        tri = np.concatenate([worlds[u][mode] for u in [TOWER, PODIUM]])
        projection = shapely.union_all(shapely.polygons(tri[:, :, [0, 2]]))
        coverage = projection.intersection(target).area / target.area
        extent = float(shapely.distance(shapely.points(tri[:, :, [0, 2]].reshape(-1, 2)), target).max())
        assert coverage >= .95 and extent <= 10
        # All current forms in both complete source regions are these two.
        # No same-parent exclusion is used to clear a third actor.
        unrelated_excess = 0.
        pair = take(pair_batch, BASE / pair_batch / ('275792:0--276873:0--'+mode+'.json.gz'))
        assert pair['allPairsExamined']
        area = [c for c in pair['contacts'] if c['dimension'] == 2]
        assert len(area) == 75
        for c in area:
            a = normal(worlds[PODIUM][mode][c['sourceFaceA']])
            b = normal(worlds[TOWER][mode][c['sourceFaceB']])
            assert sum(v*w for v, w in zip(a, b)) < 0
        measures.append(dict(mode=mode, completeFaces=len(tri), compoundTargetCoverage=coverage,
                             maximumExtentM=extent, unrelatedExcessM2=unrelated_excess,
                             opposingOriginalAreaInterfaces=len(area)))
    strict_batch = 'government-xl-unnamed276873-original-pair-support-v1-20261025'
    strict = take(strict_batch, BASE / strict_batch / 'summary.json')
    assert strict['sourceSHA256ByUid'] == SOURCES
    for r in strict['rows']:
        assert r['support']['strictContacts'] == 134 and len(r['support']['unresolved']) == 178
        f = r['compoundFoundation']
        assert f['triangles'] == f['completeTerrainTriangles'] == FACES[TOWER]
        assert f['fullyBuriedTriangles'] == f['fullyBuriedUpwardTriangles'] == 0 and f['minimumGapM'] == 0
    path_batch = 'government-xl-unnamed276873-strict-root-paths-v1-20261025'
    paths = take(path_batch, BASE / path_batch / 'summary.json')
    assert paths['sourceSHA256ByUid'] == SOURCES and len(paths['rows']) == 4
    assert all(r['targets'] == r['finiteAttachmentPaths'] == 178 and r['disconnected'] == r['aboveExistingEndpointCeiling'] == 0 for r in paths['rows'])
    foundation_batch = 'government-xl-unnamed275792-podium-prephysical-v1-20261025-foundations'
    foundations = take(foundation_batch, BASE / foundation_batch / 'summary.json')
    assert len(foundations['rows']) == 4
    assert all(r['triangles'] == r['completeTerrainTriangles'] == 577 and r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0 for r in foundations['rows'])
    low_batch = 'government-xl-unnamed275792-complete-low-faces-v1-20261025'
    low = take(low_batch, BASE / low_batch / 'summary.json')
    assert len(low['rows']) == 4 and all(r['exactAffectedFaces'] == [4, 41, 42, 121, 363] and r['allAffectedWallLike'] and r['allAffectedHaveExposedHighestVertex'] for r in low['rows'])
    caps_batch = 'government-xl-unnamed275792-complete-ground-cap-paths-v1-20261025'
    caps = take(caps_batch, BASE / caps_batch / 'summary.json')
    assert caps['sourceSHA256'] == SOURCES[PODIUM] and caps['allFourCompleteGroundClearCapPaths'] and len(caps['rows']) == 4
    assert all(r['completeGroundClearancePartition']['allAffectedHavePaths'] and not r['completeGroundClearancePartition']['negativeNonWallFaces'] for r in caps['rows'])
    clearance_batch = 'government-xl-unnamed276873-complete-compound-clearance-v1-20261025'
    clearance = take(clearance_batch, BASE / clearance_batch / 'summary.json')
    assert clearance['sourceSHA256'] == SOURCES[TOWER] and clearance['supportSHA256'] == SOURCES[PODIUM]
    assert len(clearance['rows']) == 4 and all(r['noAffectedFaces'] and not r['exactAffectedFaces'] and not r['negativeNonWallFaces'] for r in clearance['rows'])
    foreign_batch = 'government-xl-unnamed276873-pair-foreign-contacts-v1-20261025'
    foreign = take(foreign_batch, BASE / foreign_batch / 'summary.json')
    assert foreign['foreignPairs'] == 2 and {(r['uid'], r['foreignUid']) for r in foreign['rows']} == {(TOWER, PODIUM), (PODIUM, TOWER)}
    images = []
    view_batch = 'government-xl-unnamed276873-two-original-source-views-v1-20261025'
    take(view_batch, BASE / view_batch / 'summary.json')
    for name in ['complete-original-assembly.png', 'base-only-diagnostic.png']:
        path = BASE / view_batch / name
        assert digest(path.read_bytes()) == pins[view_batch][str(path.relative_to(ROOT))]
        refs.append(path)
        images.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()), actuallyInspected=True))
    result = dict(uids=sorted(SOURCES), sourceSHA256ByUid=SOURCES, requiredOriginalAssembly=SOURCES,
                  supportByUid={TOWER: PODIUM}, retainedCurrentBasicSupportUids=[], retainedBasicSupportDependencies=[],
                  leaseResources=['building:'+u for u in sorted(obligations)], terrainEdits=False,
                  currentManifest=dict(path=str(manifest.relative_to(ROOT)), sha256=digest(manifest.read_bytes())),
                  identityAccepted=True, identityProof={k: True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},
                  rawIndividualIdentity=raw_identity, identityMeasures=measures, completeCurrentNeighbourChecks=2,
                  sourceSpecificPhysicalInterpretationAccepted=True, completeNeighbourInterpretationAccepted=True,
                  completeFourWorldFoundations=True, completeFourWorldSourceClearance=True,
                  completeFourWorldCanonicalRetainedBasicSupport=True, emptyRetainedBasicSupportQualification='No BASIC support credit; exact original podium is co-imported.',
                  sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False, sourceEvidenceInterpretationUsedAI=True,
                  visualAcceptance=False, installationApproved=False, publication=False, imagesActuallyViewed=images,
                  interpretation='Only this exact two-source permit assembly. Tower support warnings resolve along unchanged source paths to134 strict original roof anchors in all4worlds, with no endpoint rise and zero compound minimum gap. Five partially below-grade podium walls have exposed highest vertices and complete source cap paths in all4worlds; no complete/upward face is buried and no negative non-wall is excused. Their recorded negative gaps remain. Both co-import BASIC proxies are replaced atomically; raw80proxy contacts are not third-party clearance or BASIC support credit. All75original area interfaces have opposing normals. Original rooftop crane/truss remains immutable. The base-only image is effectively empty and supplies no base acceptance credit. Source geometry/height differences and live-versus-recorded OBJECTIDs remain explicit; exact stableCSUID/wholegeoref/sourcegraph/nativebytes and complete official permit membership bind the identity. Actual desktop/mobile own-source and joint browser acceptance remains required.')
    save(doc / 'ROOT-PHYSICAL-REVIEW.json', result)
    refs.extend(HERE / n for n in ['exact_packed_world_geometry_20261009.py', 'original_source_assembly_diagnostic.py'])
    module('unnamed_physical_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'bounded-two-original-identity-physical-neighbour-review-no-publication', list(dict.fromkeys(refs)), result)
    print(dict(identityAccepted=True, physicalAccepted=True, browserAcceptance=False, publication=False), flush=True)


if __name__ == '__main__':
    main()
