"""Whole altered2513 terrain domain versus exact current6645 native actors.

Every source/root/form/entry/module tuple is freshly rebound before/end. The
complete previous actual POSITION/matrix computations are reused only byte-
identically. Original/literal/two Float32 bounds include unused vertices. Every
non-disjoint actor remains a full numerical regression obligation, never an
accepted native or an automatic negative inferred from a bounding box.
"""
import importlib.util
import json
import re
import time
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, reservations
from actual_native_bounds_baseline_rebind_20261011 import validate_unchanged_actor
from complete_actual_native_position_bounds_separation_20261011 import verify, strict_planar_separation, box, NATIVE_MODES
BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'xl-terrain-recovery-20261011-twin-regency-whole-terrain-domain-current6645-native-census-v1'
DOC = BASE / BATCH
FOLDERS = [BASE / n for n in [
    'government-xl-complete-current-native-actual-position-matrix-bounds-v2-20261011',
    'government-xl-complete-native-actual-position-post-block17-delta-v1-20261011',
    'government-xl-complete-native-actual-position-vancor-post-mount-delta-v1-20261011',
    'government-xl-complete-native-actual-position-evangel-post-elements-delta-v1-20261011']]
PHYSICAL = BASE / 'government-xl-terrain-recovery-twin-regency-pair-authentic-current-v1-20261011'
PROPOSED = BASE / 'government-xl-terrain-recovery-twin-regency-pair-proposed-ground-capture-v1-20261011'
UIDS = ['landsd/222465:0', 'landsd/223206:0']
CURRENT = 'df35e9ba069dc8445ca873ba1a065cffafcd00e94813a3af040219121469830e'

def ref(p): return dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes()))
def canonical(x): return digest(json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())

def main():
    assert not DOC.exists()
    manifest = ROOT / '3d-viewer/city/data/manifest.json'; start = ref(manifest); assert start['sha256'] == CURRENT
    refs = [ref(Path(__file__)), start]; actors = {}; inputs = {}; inventories = []; receipts = {}
    for folder, count in zip(FOLDERS, [6637, 2, 3, 3]):
        receipt = read(folder / 'result.json'); receipts[folder.name] = receipt
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
        for name in ['input.json.gz', 'inventory.json.gz']:
            assert ref(folder / name) in receipt['evidenceRefs']; refs.append(ref(folder / name))
        refs.append(ref(folder / 'result.json'))
        inv = read(folder / 'inventory.json.gz'); inp = read(folder / 'input.json.gz')
        assert inv['successfullyCapturedActors'] == count and not inv['errors'] and inv['startAndEndInputHashesVerified']
        inventories.append(inv)
        for row in inv['rows']:
            assert row['uid'] not in actors; actors[row['uid']] = row
        for row in inp['rows']:
            assert row['uid'] not in inputs; inputs[row['uid']] = row
    assert len(actors) == len(inputs) == 6645 and set(actors) == set(inputs)
    delta = FOLDERS[-1]
    binding = read(delta / 'complete-unchanged-baseline-bindings.json.gz'); composition = read(delta / 'composition.json.gz')
    assert binding['currentManifest'] == composition['currentManifest'] == start
    assert binding['completeOldActorsRebound'] == composition['completeOldActorsExactlyRebound'] == 6642
    for name in ['complete-unchanged-baseline-bindings.json.gz', 'composition.json.gz']:
        assert ref(delta / name) in receipts[delta.name]['evidenceRefs']; refs.append(ref(delta / name))
    for b in binding['rows']:
        assert canonical(actors[b['uid']]) == b['unchangedActualCompleteBoundsRowSHA256']
    for folder in [PHYSICAL, PROPOSED]:
        r = read(folder / 'result.json'); receipts[folder.name] = r
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (r['jobId'],)).fetchone() == ('complete', r)
        refs.append(ref(folder / 'result.json'))
    proposal = read(PHYSICAL / 'terrain-candidates.json'); assert len(proposal) == 1 and proposal[0]['uids'] == UIDS
    assert ref(PHYSICAL / 'terrain-candidates.json') in receipts[PHYSICAL.name]['evidenceRefs']
    terrainpath = ROOT / proposal[0]['path']; terrainpin = ref(terrainpath)
    assert terrainpin['sha256'] == proposal[0]['sha256'] == 'f00e0dc6e588168dbb3ff69827b170c2a6beca41908bc7e556ea79e6b713a43e'
    terrain = read(terrainpath); p = np.asarray(terrain['nativeMesh']['position'], float).reshape(-1, 3)
    index = np.asarray(terrain['nativeMesh']['index'], np.uint32).reshape(-1, 3)
    assert len(index) == proposal[0]['triangles'] == 2513 and np.isfinite(p).all() and index.max() < len(p)
    bbox = proposal[0]['bounds']; assert np.all(p[:, 0] >= bbox[0]) and np.all(p[:, 0] <= bbox[2])
    assert np.all(p[:, 2] >= bbox[1]) and np.all(p[:, 2] <= bbox[3])
    parentpath = ROOT / '3d-viewer/city/data/terrain.json'; parent = read(parentpath)
    origin = parent['meta']['origin']; g = terrain['meta']['georef']
    x0 = g['bE'] - origin[0]; z0 = origin[1] - g['bN']
    assert [x0, z0, x0 + (terrain['w'] - 1) * g['aE'], z0 - (terrain['h'] - 1) * g['aN']] == bbox
    pg = parent['meta']['georef']; i0, j0, i1, j1 = terrain['coarseCells']
    coarse_extent = [pg['bE'] + i0 * pg['aE'] - origin[0], origin[1] - (pg['bN'] + j0 * pg['aN']),
        pg['bE'] + i1 * pg['aE'] - origin[0], origin[1] - (pg['bN'] + j1 * pg['aN'])]
    assert coarse_extent == bbox
    metricspath = PHYSICAL / 'metrics.json'; assert ref(metricspath) in receipts[PHYSICAL.name]['evidenceRefs']
    assert read(metricspath)['inputHashes'][str(parentpath.relative_to(ROOT))] == ref(parentpath)['sha256']
    refs.extend([ref(parentpath), ref(metricspath)])
    # Includes complete declared coarse grid domain, not only owned source bounds.
    corners = np.asarray([[bbox[0], p[:, 1].min(), bbox[1]], [bbox[2], p[:, 1].max(), bbox[3]]], float)
    allpoints = np.concatenate([p, corners, p.astype(np.float32).astype(float), corners.astype(np.float32).astype(float)])
    domain = [allpoints.min(0).tolist(), allpoints.max(0).tolist()]
    owned_modes = {m: domain for m in ['providerOriginal', 'actualLiteral', 'explicitLeftAssociatedF32ModelMatrix', 'explicitBalancedF32ModelMatrix']}
    rtpath = HERE / 'local' / PROPOSED.name / 'runtime-geometry.json.gz'
    assert ref(rtpath) in receipts[PROPOSED.name]['evidenceRefs']
    runtime = read(rtpath); assert [r['uid'] for r in runtime['rows']] == UIDS
    refs.extend([ref(terrainpath), ref(rtpath), ref(PHYSICAL / 'terrain-candidates.json')])
    current = read(manifest); models = {}; sources = {}
    for url in current['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url; refs.append(ref(path))
        for entry in read(path)['models']:
            assert entry['uid'] not in models; models[entry['uid']] = entry; sources[entry['uid']] = path.parent / entry['asset']
    assert set(models) == set(actors) and len(models) == 6645
    forms = {}; wanted = set(models); dependency_modules = inventories[0]['completeRecursiveProductionModuleClosure']['inputHashes']
    declared = read(FOLDERS[0] / 'input.json.gz')['declaredDependencyUIDSourceHashes']
    for inv in inventories:
        assert inv['completeRecursiveProductionModuleClosure']['inputHashes'] == dependency_modules
    for path, sha in {**dependency_modules, **declared, **runtime['inputHashes']}.items():
        file = ROOT / path; assert ref(file)['sha256'] == sha; refs.append(ref(file))
    for path in declared:
        wanted.update(re.findall(r'landsd/\d+:0', (ROOT / path).read_text()))
    for tile in current['tiles']:
        path = ROOT / '3d-viewer' / tile['url']; matches = [f for f in read(path)['buildings'] if f['uid'] in wanted]
        if matches:
            refs.append(ref(path))
            for f in matches:
                assert f['uid'] not in forms; forms[f['uid']] = f
    assert set(models).issubset(forms)
    claim = reservations.claim('twin-all-native-domain-' + str(uuid.uuid4()), ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
    assert claim['ok']; lease = claim['reservation']; last = time.monotonic()
    def pulse(force=False):
        nonlocal last
        if force or time.monotonic() - last >= 20:
            assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease); last = time.monotonic()
    try:
        strict = []; touched = []; tuple_rows = []
        for uid, a in actors.items():
            source = sources[uid]; pin = ref(source); prior = inputs[uid]
            assert validate_unchanged_actor(prior, a, models[uid], forms[uid], pin, pin['sha256']) == a
            proof = a['completeOriginalPOSITIONProof']
            assert proof['sourceSHA256'] == a['sourceSHA256'] == models[uid]['sha256'] == pin['sha256']
            assert proof['allOriginalPositionVerticesAccounted'] and proof['completeOriginalTriangles'] == a['completeFaces']
            assert proof['completeOriginalPositionVertices'] == a['completePositionVertices']
            # Independently validate every mesh union, including nominated overlaps.
            meshes = a['actualRenderMeshes']; assert meshes and all(m['wholePositionVerticesIncludingUnused'] is True for m in meshes)
            assert sum(m['completePositionVertices'] for m in meshes) == a['completePositionVertices']
            assert sum(m['completeIndexedFaces'] for m in meshes) == a['completeFaces']
            for field in NATIVE_MODES.values():
                boxes = [box(m[field]) for m in meshes]
                union = [[min(v[0][axis] for v in boxes) for axis in range(3)], [max(v[1][axis] for v in boxes) for axis in range(3)]]
                assert box(a[field]) == union
            pairproofs = []; native_modes = {'providerOriginal': proof['originalWholeSourceBounds'],
                'actualLiteral': a['completeLiteralBounds'], 'explicitLeftAssociatedF32ModelMatrix': a['completeLeftAssociatedF32Bounds'],
                'explicitBalancedF32ModelMatrix': a['completeBalancedF32Bounds']}
            overlap = False
            for mode, bounds in native_modes.items():
                try: pairproofs.append(dict(mode=mode, **strict_planar_separation(domain, bounds)))
                except AssertionError as error:
                    assert str(error) == 'Whole actual POSITION bounds overlap or touch; complete finite actor context required'
                    overlap = True; pairproofs.append(dict(mode=mode, closedWholeBoundsTouchOrOverlap=True, completeFiniteRegressionRequired=True))
            if overlap:
                touched.append(dict(uid=uid, sourceSHA256=a['sourceSHA256'], completeActualInventoryRow= a,
                    completeFourNativeModeBounds=native_modes, allDomainPairProofs=pairproofs, nativeReacceptance=False,
                    fullCurrentFiniteAndRegressionObligation=True))
            else:
                certificate = verify(owned_modes, [a]); assert certificate['completeForeignNativeActors'] == 1
                strict.append(dict(uid=uid, sourceSHA256=a['sourceSHA256'], originalAndActualModeDomainProofs=pairproofs,
                    strictActualSeparationCertificate=certificate))
            tuple_rows.append(dict(uid=uid, rawEntrySHA256=canonical(models[uid]), viewerFormSHA256=canonical(forms[uid]),
                source=pin, immutableActualRowSHA256=canonical(a)))
            refs.append(pin); pulse()
        assert len(strict) + len(touched) == 6645 and ref(manifest) == start
        refs.extend(ref(HERE / n) for n in ['actual_native_bounds_baseline_rebind_20261011.py',
            'complete_actual_native_position_bounds_separation_20261011.py', 'xl-popcorn-source-investigations-checkpoints-20261009.py'])
        unique = {r['path']: r for r in refs}
        assert all(ref(ROOT / r['path']) == r for r in unique.values()); pulse(True)
        result = dict(uids=UIDS, currentManifest=start, completeAlteredTerrainDomainBounds=domain,
            completeDeclaredTerrainBounds=bbox, originalAndFloat32TerrainRecordsIncluded=True,
            completeCurrentNativeActors=6645, completeFreshCurrentEntrySourceFormModuleTuples=tuple_rows,
            completeStrictlyDisjointActors=strict, fullFiniteRegressionNominations=touched,
            nativeReacceptance=False, physicalAccepted=False, currentAcceptance=False,
            sourceGeometryChanges=0, terrainProposalChanged=False, newlyInstalled=0, evidenceRefs=list(unique.values()))
        save(DOC / 'diagnostic.json.gz', result)
        spec = importlib.util.spec_from_file_location('twin_native_domain_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        m.freeze(BATCH, 'complete6645-current-actual-four-mode-native-whole-altered-terrain-domain-census-v1',
            [ROOT / r['path'] for r in unique.values()] + [DOC / 'diagnostic.json.gz'],
            dict(uids=UIDS, completeNativeActors=6645, strictDisjointActors=len(strict), fullFiniteRegressionUIDs=[r['uid'] for r in touched],
                nativeReacceptance=False, currentAcceptance=False, newlyInstalled=0))
        print(dict(strictDisjointActors=len(strict), nominatedUIDs=[r['uid'] for r in touched]), flush=True)
    finally: assert reservations.release(lease)['ok']

if __name__ == '__main__': main()
