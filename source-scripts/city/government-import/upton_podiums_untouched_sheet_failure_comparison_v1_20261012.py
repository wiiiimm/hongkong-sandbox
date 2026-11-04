"""Original 11-SW-7A terrain diagnostic; no terrain/model publication or edits."""
import argparse
import ast
import importlib.util
import json
import subprocess
import sys
import time
import uuid
import zlib
from pathlib import Path

import numpy as np
from run import ROOT, HERE, read, save, digest, connect, reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse
from exact_original_paired_finite_clearance_v3_20261011 import verify as paired

B = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-upton-podiums-untouched-sheet-failures-v1-20261012'
DOC = B / BATCH
LOCAL = HERE / 'local' / BATCH
CAP = B / 'government-xl-upton-three-original-complete-current-runtime-capture-v4-20261012'
FINITE = B / 'government-xl-upton-three-original-complete-current-finite-ground-v5-20261012'
CACHE = HERE / 'local/government-xl-50-second-20260913'
SHEET = CACHE / 'sheets/11-SW-7A'
MANIFEST = ROOT / '3d-viewer/city/data/manifest.json'
CURRENT = '2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
UIDS = ['landsd/338946:0', 'landsd/12728:0', 'landsd/12662:0']
FREEZER = HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py'
METHOD = B / (BATCH + '-proposal') / 'METHOD.md'


def ref(p):
    return dict(path=str(p.resolve().relative_to(ROOT)), sha256=digest(p.read_bytes()))


def load_module(p, name):
    spec = importlib.util.spec_from_file_location(name, p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def code_paths():
    folders = [HERE, HERE.parent / 'shared-modelling', HERE.parent / 'citywide-native',
               ROOT / 'docs/astra-city/mui-wo-buildings/review', HERE.parent / 'assembly-support-review']
    pending = [Path(__file__), FREEZER, HERE / 'pending-context.py',
               HERE.parent / 'assembly-support-review/native_terrain.py']
    seen = set()
    while pending:
        p = pending.pop().resolve()
        if p in seen:
            continue
        seen.add(p)
        for node in ast.walk(ast.parse(p.read_text())):
            names = ([node.module] if isinstance(node, ast.ImportFrom) and node.module else
                     [n.name for n in node.names] if isinstance(node, ast.Import) else [])
            for name in names:
                for folder in folders:
                    candidate = folder / (name.replace('.', '/') + '.py')
                    if candidate.is_file():
                        pending.append(candidate)
    return sorted(seen)


def run_owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease) and not DOC.exists()
    refs = {r['path']: r for r in [ref(p) for p in code_paths()] + [ref(METHOD), ref(MANIFEST)]}
    assert refs[str(MANIFEST.relative_to(ROOT))]['sha256'] == CURRENT
    last = time.monotonic()

    def pulse(force=False):
        nonlocal last
        if force or time.monotonic() - last > 20:
            assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease)
            last = time.monotonic()

    for folder, jid in [(CAP, '4af6addb43b6b94fd2e5e61c868fbd62c84d06a365dc2e19b79d6856ce054502'),
                        (FINITE, '7b2c30c7df3cca9f42d7d3e8cee90f98525d0939c49ad396d900a256d8f4f325')]:
        result = read(folder / 'result.json')
        assert result['jobId'] == jid
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', result)
        for r in result['evidenceRefs'] + [ref(folder / 'result.json')]:
            assert ref(ROOT / r['path']) == r
            assert r['path'] not in refs or refs[r['path']] == r
            refs[r['path']] = r
            pulse()
    before = None
    def review_state():
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            return con.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id', (UIDS + ['landsd/254809:0'],)).fetchall()
    before = review_state()
    source = read(SHEET / 'recovery.json')['source']
    assert source['sheet'] == '11-SW-7A' and source['terrainGeometryIncluded']
    directories = read(CACHE / 'source-directories.json')
    assert source['directorySHA256'] == directories['11-SW-7A']['directorySHA256'] == '69d5f9f3635581f732caae3e71ce503c4dd8f50e21053e0042795cd5b78d01aa'
    assert source['sourceETag'] == directories['11-SW-7A']['etag']
    directory = SHEET / 'directory/zip-directory.bin'
    assert digest(directory.read_bytes()) == source['directorySHA256']
    for p in [SHEET / 'recovery.json', CACHE / 'source-directories.json', directory]:
        refs[ref(p)['path']] = ref(p)
    gltfs = []
    for entry in source['entries']:
        if not entry['name'].startswith('TERRAIN(TB)/'):
            continue
        p = SHEET / 'terrain' / entry['name']
        raw = p.read_bytes()
        assert len(raw) == entry['bytes'] and digest(raw) == entry['sha256']
        assert zlib.crc32(raw) & 0xffffffff == entry['sourceCRC32']
        refs[ref(p)['path']] = ref(p)
        if p.suffix == '.gltf':
            gltfs.append(p)
    assert len(gltfs) == 1
    decoder = load_module(HERE / 'pending-context.py', 'upton_untouched_decoder')
    full = decoder.triangles(gltfs[0])
    assert full.ndim == 3 and full.shape[1:] == (3, 3) and np.isfinite(full).all()
    pulse(True)
    diagnostic = read(FINITE / 'diagnostic.json.gz')
    assert ref(FINITE / 'diagnostic.json.gz')['sha256'] == '8d9ca62b3e9b59a404538573a3b09a30ea74a9be4e5c7b28bd015089a5209468'
    selection = read(CAP / 'selection.json.gz')['rows']
    attributes = read(CAP / 'actual-render-geometry.json.gz')['rows']
    assert [r['uid'] for r in selection] == [r['uid'] for r in attributes] == UIDS
    DOC.mkdir(parents=True)
    inventory = dict(sheet='11-SW-7A', sourceReceipt=ref(SHEET / 'recovery.json'),
                     completeUnfilteredSourceFacets=len(full), completeWorldSHA256=digest(full.tobytes()),
                     completeBounds=[full.min((0, 1)).tolist(), full.max((0, 1)).tolist()],
                     noAreaSlopeDegenerateFilter=True)
    out = []
    for selected, attrs, actor in zip(selection[1:], attributes[1:], diagnostic['actors'][1:]):
        assert selected['uid'] == attrs['uid'] == actor['uid']
        asset = ROOT / selected['candidate']['path']
        assert ref(asset)['sha256'] == selected['sourceSHA256'] == actor['sourceSHA256']
        refs[ref(asset)['path']] = ref(asset)
        original = decode_original_world_triangles(asset.read_bytes())
        bounds_proof = packed_world_bounds(asset.read_bytes())
        assert bounds_proof['worldTrianglesSHA256'] == digest(original.tobytes())
        assert bounds_proof['allOriginalPositionVerticesAccounted']
        index = np.asarray(attrs['completeOriginalIndex'], dtype=np.uint32).reshape(-1, 3)
        worlds = {'original': original}
        vertices = {'original': np.asarray(bounds_proof['originalWholeSourceBounds'])}
        for mode, key in [('literal', 'completeLiteralWorldPosition'), ('explicitLeftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('explicitBalancedF32', 'completeExplicitBalancedFloat32WorldPosition')]:
            all_positions = np.asarray(attrs[key], dtype=float).reshape(-1, 3)
            worlds[mode] = all_positions[index]
            vertices[mode] = np.array([all_positions.min(0), all_positions.max(0)])
        lo = np.min([v[0] for v in vertices.values()], 0) - 1
        hi = np.max([v[1] for v in vertices.values()], 0) + 1
        xz = full[:, :, [0, 2]]
        ids = np.flatnonzero(np.all(xz.max(1) >= lo[[0, 2]], 1) & np.all(xz.min(1) <= hi[[0, 2]], 1))
        ground = full[ids]
        assert len(ground)
        ground_sha = digest(ground.tobytes())
        save(DOC / (selected['uid'].replace('/', '-').replace(':', '-') + '-source-roi.json.gz'), dict(selectedWholeSheetFaceIDs=ids.tolist(), allOriginalTriplets=ground.tolist(), wholeSourceFaces=len(full), strictDisjointOmittedFacets=len(full)-len(ids), allFourUnusedPOSITIONBounds={k:v.tolist() for k,v in vertices.items()}, originalUnusedPOSITIONProof=bounds_proof, completeGroundSHA256=ground_sha))
        cache = {}
        for mode, world in worlds.items():
            binding = actor['allFourStreamBindings'][mode]
            assert digest(world.tobytes()) == binding['wholeWorldSHA256']
            saved = actor['distinctCompleteFiniteProofs'][binding['wholeWorldSHA256']]
            failure_ids = saved['ordinaryFailingFaces']
            key = (binding['wholeWorldSHA256'], ground_sha, tuple(failure_ids))
            reused = key in cache
            if not reused:
                rows = []
                for face_id in failure_ids:
                    first = coarse(world[face_id], ground)
                    second = None if first['existingOrdinaryClearanceBoundProved'] else paired(world[face_id], ground)
                    final = first if second is None else second
                    assert final['sourceFaceSHA256'] == digest(world[face_id].tobytes()) and final['completeCurrentGroundSHA256'] == ground_sha
                    rows.append(dict(face=face_id, coarse=first, paired=second, projectionCovered=final['groundProjectionCovered'], ordinaryBoundProved=final['existingOrdinaryClearanceBoundProved']))
                    pulse()
                    if len(rows) % 20 == 0:
                        save(LOCAL / (selected['uid'].replace('/', '-').replace(':', '-') + '-' + mode + '-progress.json.gz'), dict(complete=False, rows=rows, wholeWorldSHA256=key[0], wholeGroundSHA256=key[1]))
                        print(json.dumps(dict(uid=selected['uid'], mode=mode, testedFailures=len(rows), expectedFailures=len(failure_ids))), flush=True)
                cache[key] = rows
            out.append(dict(uid=selected['uid'], mode=mode, wholeWorldSHA256=key[0], wholeGroundSHA256=key[1], rawCurrentFailedRowsVerbatim=[saved['allWholeFacetProofs'][i] for i in failure_ids], currentUncoveredIDs=saved['coverageFailingFaces'], sourceOnlyFailureComparison=cache[key], exactWholeTupleReuse=reused, noGradeRootOrAcceptanceCredit=True))
            pulse(True)
    save(DOC / 'source-only-failure-comparison.json.gz', dict(rows=out, wholeSourceInventory=inventory, all23OriginalCrossingsRetained=True, originalCurrentNegativesRetained=True, towerTerrainProofNotRepeated=True, noGeometryChanges=True, installationApproved=False))
    for r in refs.values():
        assert ref(ROOT / r['path']) == r
        pulse()
    assert review_state() == before
    load_module(FREEZER, 'upton_sheet_freezer').freeze(BATCH, 'upton-original-unfiltered-sheet-failure-comparison-v1', [ROOT/r['path'] for r in refs.values()], dict(uids=UIDS, sourceOnly=True, originalCurrentFailuresRetained=True, newlyInstalled=0, physicalAccepted=False))
    assert review_state() == before


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    if args.owned:
        return run_owned()
    assert not DOC.exists() and not LOCAL.exists()
    controlled = UIDS + ['landsd/254809:0']
    claim = reservations.claim('upton-original-sheet-' + str(uuid.uuid4()), ['building:'+u for u in controlled] + ['terrain-patch:'+u for u in controlled], batch=BATCH, ttl=3600)
    assert claim['ok'], claim
    save(LOCAL / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(LOCAL / 'reservation.json'), '--ttl', '3600', '--', sys.executable, __file__, '--owned'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
