"""Whole Stadium faithful transition/routing-restoration terrain domain versus exact current6645 native actors.

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
BATCH = 'government-xl-mongkok-stadium240332-whole-routing-mask-current6645-native-census-v1-20261011'
DOC = BASE / BATCH
FOLDERS = [BASE / n for n in [
    'government-xl-complete-current-native-actual-position-matrix-bounds-v2-20261011',
    'government-xl-complete-native-actual-position-post-block17-delta-v1-20261011',
    'government-xl-complete-native-actual-position-vancor-post-mount-delta-v1-20261011',
    'government-xl-complete-native-actual-position-evangel-post-elements-delta-v1-20261011']]
CANDIDATE = None  # Required explicit completed candidate batch CLI; no future placeholder evidence.
UIDS = ['landsd/240332:0', 'landsd/240527:0']
CURRENT = 'df35e9ba069dc8445ca873ba1a065cffafcd00e94813a3af040219121469830e'

def ref(p): return dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes()))
def canonical(x): return digest(json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())

def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument("--candidate-batch",required=True);args=parser.parse_args()
    assert args.candidate_batch in ["government-xl-mongkok-stadium240332-faithful-multisurface-transition-candidate-v1-20261011","government-xl-mongkok-stadium240332-faithful-multisurface-transition-candidate-v2-20261011"]
    CANDIDATE=BASE/args.candidate_batch
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
    candidate_receipt=read(CANDIDATE/'result.json')
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(candidate_receipt['jobId'],)).fetchone()==('complete',candidate_receipt)
    # Every frozen source/current/transitive binding, not only convenient outputs.
    for pin in candidate_receipt['evidenceRefs']:
        assert ref(ROOT/pin['path'])==pin;refs.append(pin)
    refs.append(ref(CANDIDATE/'result.json'))
    diagnostic=read(CANDIDATE/'diagnostic.json.gz')
    assert diagnostic['currentManifest']==start and diagnostic['terrainCandidateCreated'] and not diagnostic['terrainCandidateApproved'] and not diagnostic['currentAcceptance']
    assert diagnostic['completeUnchangedOriginalFaces']==14798 and diagnostic['completeUnchangedGeneratedJoins']==3
    terrainpath=CANDIDATE/'nonpublishing-faithful-terrain-patch.json.gz';terrain=read(terrainpath)
    groundpath=CANDIDATE/'complete-current-ground-and-parent-routing.json.gz';ground=read(groundpath)
    rtpath=CANDIDATE/'actual-native-attributes.json.gz';runtime=read(rtpath)
    for path in [terrainpath,groundpath,rtpath,CANDIDATE/'diagnostic.json.gz']:
        assert ref(path) in candidate_receipt['evidenceRefs'];refs.append(ref(path))
    assert ground['startEndAllInputsVerified'] and runtime['startEndAllInputsVerified']
    assert runtime['completeRenderedAndIndexedRolesAccounted'] and not runtime['allExcludedNonzeroProjectedFaces'] and not runtime['missingCentroidSamples']
    assert terrain['coarseCells']==ground['proposedCoarseRoutingCells']
    p=np.asarray(terrain['nativeMesh']['position'],float).reshape(-1,3)
    index=np.asarray(terrain['nativeMesh']['index'],np.uint32).reshape(-1,3)
    assert np.isfinite(p).all() and index.max()<len(p) and len(index)==runtime['completeActualDrawnCandidateFacets']
    # COMPLETE routing/coarse-restoration mask, not only new source/band bounds.
    bbox=ground['completeCoarseRoutingWorldBounds'];assert len(bbox)==4
    assert np.all(p[:,0]>=bbox[0]) and np.all(p[:,0]<=bbox[2]) and np.all(p[:,2]>=bbox[1]) and np.all(p[:,2]<=bbox[3])
    parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath)
    assert ground['inputHashes'][str(parentpath.relative_to(ROOT))]==ref(parentpath)['sha256']
    origin=parent['meta']['origin'];pg=parent['meta']['georef'];i0,j0,i1,j1=terrain['coarseCells']
    assert [pg['bE']+i0*pg['aE']-origin[0],origin[1]-(pg['bN']+j0*pg['aN']),pg['bE']+i1*pg['aE']-origin[0],origin[1]-(pg['bN']+j1*pg['aN'])]==bbox
    refs.append(ref(parentpath))
    corners=np.asarray([[bbox[0],p[:,1].min(),bbox[1]],[bbox[2],p[:,1].max(),bbox[3]]],float)
    allpoints=np.concatenate([p,corners,p.astype(np.float32).astype(float),corners.astype(np.float32).astype(float)])
    domain=[allpoints.min(0).tolist(),allpoints.max(0).tolist()]
    owned_modes={m:domain for m in ['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']}
    # Existing separation API labels reused conservatively; this is a compute
    # terrain domain, never a claim that generated pieces are government originals.
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
    for path, sha in {**dependency_modules, **declared, **ground['inputHashes'], **runtime['inputHashes']}.items():
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
    claim = reservations.claim('stadium-all-native-routing-mask-' + str(uuid.uuid4()), ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
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
            completeDeclaredTerrainBounds=bbox, completeRoutingAndCoarseRestorationMaskIncluded=True,
            separatelyLabelledComputeTerrainDomain=True, candidateBatch=args.candidate_batch,
            catalogueWorldBoundsNeverUsedForClearance=True, originalAndFloat32TerrainRecordsIncluded=True,
            completeCurrentNativeActors=6645, completeFreshCurrentEntrySourceFormModuleTuples=tuple_rows,
            completeStrictlyDisjointActors=strict, fullFiniteRegressionNominations=touched,
            nativeReacceptance=False, physicalAccepted=False, currentAcceptance=False,
            sourceGeometryChanges=0, terrainProposalChanged=False, newlyInstalled=0, evidenceRefs=list(unique.values()))
        save(DOC / 'diagnostic.json.gz', result)
        spec = importlib.util.spec_from_file_location('stadium_native_domain_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        m.freeze(BATCH, 'complete6645-current-actual-four-mode-native-whole-routing-and-restoration-mask-census-v1',
            [ROOT / r['path'] for r in unique.values()] + [DOC / 'diagnostic.json.gz'],
            dict(uids=UIDS, completeNativeActors=6645, strictDisjointActors=len(strict), fullFiniteRegressionUIDs=[r['uid'] for r in touched],
                nativeReacceptance=False, currentAcceptance=False, newlyInstalled=0))
        print(dict(strictDisjointActors=len(strict), nominatedUIDs=[r['uid'] for r in touched]), flush=True)
    finally: assert reservations.release(lease)['ok']

if __name__ == '__main__': main()
