"""Acquire one current government terrain revision; preserve old source identity."""
import argparse
import hashlib
import json
import subprocess
import sys
import uuid
import zipfile
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify
sys.path.insert(0, str(HERE.parent / 'citywide-source'))
from discover import scan
sys.path.insert(0, str(HERE.parent / 'citywide-native'))
from download import acquire, safe

B = 'government-xl-nam-cheong-fresh-terrain-context-v1-20261023'
BASE = ROOT / 'docs/astra-city/government-import'
D, LOCAL = BASE / B, HERE / 'local' / B
LEASE = LOCAL / 'reservation.json'
UID = 'landsd/268867:0'
CAP = 'government-xl-nam-cheong-fu-yun-joint-current-v1-20261023-runtime'


def owned():
    assert not D.exists()
    lease = read(LEASE)
    assert reservations.owns(lease)
    _, pins = authenticate(BASE / CAP)
    selection = BASE / CAP / 'selection.json.gz'
    assert digest(selection.read_bytes()) == pins[str(selection.relative_to(ROOT))]
    row = next(r for r in read(selection)['rows'] if r['uid'] == UID)
    refs = [Path(__file__), BASE / CAP / 'result.json', selection]
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        source_sha, result_sha = db.execute('SELECT i.source_sha,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s', (row['native']['cacheKey'],)).fetchone()
        assert result_sha == row['native']['resultSha']
        directories = db.execute('SELECT result FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC', ('11-NW-13D',)).fetchall()
    priors = [r for (r,) in directories if hashlib.sha256(json.dumps([r['sourceURL'], r['etag'], r['directorySHA256']], separators=(',', ':')).encode()).hexdigest() == source_sha]
    assert priors
    prior = priors[0]
    save(LOCAL / 'pinned-directory.json', prior)
    current, _ = scan(dict(SHEETNO='11-NW-13D', Format_glTF=prior['sourceURL'], REVISIONDATE=prior['revision']), LOCAL / 'directory')
    fresh = dict(current, models=[])
    record = acquire(fresh, LOCAL / 'directory/zip-directory.bin', LOCAL / 'download', include_terrain=True)
    assert reservations.owns(lease)
    assert record['sourceETag'] == current['etag'] and record['directorySHA256'] == current['directorySHA256']
    files = {}
    with zipfile.ZipFile(LOCAL / 'download/11-NW-13D.zip') as z:
        for member in record['entries']:
            name = safe(member['name'])
            assert name.startswith('TERRAIN') and Path(name).suffix in ['.gltf', '.bin']
            assert z.namelist().count(name) == 1 and z.getinfo(name).file_size == member['bytes'] < 100_000_000
            raw = z.read(name)
            assert digest(raw) == member['sha256']
            path = LOCAL / 'terrain' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            files[name] = dict(path=str(path.relative_to(ROOT)), sha256=member['sha256'])
    paths = [ROOT / f['path'] for n, f in files.items() if n.endswith('.gltf')]
    assert paths
    for path in paths:
        for buffer in read(path).get('buffers', []):
            member = (path.parent / buffer['uri']).resolve()
            assert member.is_relative_to((LOCAL / 'terrain').resolve())
            assert str(member.relative_to(LOCAL / 'terrain')) in files
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256']
    refs.append(asset)
    face = decode_original_world_triangles(asset.read_bytes())[11390]
    decoder = module('fresh_nam_terrain_decoder', HERE / 'xl-second-pass.py')
    decoder.LOCAL = LOCAL
    proofs, terrain_rows = [], []
    for path in paths:
        ground = decoder.terrain_triangles(path)
        xz = ground[:, :, [0, 2]]
        ids = np.flatnonzero(np.all(xz.max(1) >= face[:, [0, 2]].min(0), axis=1) & np.all(xz.min(1) <= face[:, [0, 2]].max(0), axis=1))
        terrain_rows.append(dict(path=str(path.relative_to(ROOT)), completeFaces=len(ground), inclusiveCandidates=len(ids)))
        proofs.extend(dict(path=str(path.relative_to(ROOT)), originalTerrainFace=int(i), proof=verify(face, ground[i])) for i in ids)
    gaps = [Fraction(r['proof']['exactMinimumFiniteColumnGapM']) for r in proofs if r['proof']['exactClosedHorizontalProjectionsMeet']]
    assert gaps
    save(D / 'exact-wall-proofs.json.gz', proofs)
    result = dict(uids=[UID], sourceSHA256=row['sourceSHA256'], sourceFace=11390,
                  oldSourceETag=prior['etag'], freshSourceETag=current['etag'],
                  oldDirectorySHA256=prior['directorySHA256'], freshDirectorySHA256=current['directorySHA256'],
                  archiveChanged=(prior['etag'], prior['directorySHA256']) != (current['etag'], current['directorySHA256']),
                  sourceFiles=files, sourceTerrainPaths=[str(p.relative_to(ROOT)) for p in paths], terrainRows=terrain_rows,
                  exactMinimumGapM=str(min(gaps)), minimumGapM=float(min(gaps)), unchangedWallClearancePass=min(gaps) >= Fraction(-1, 2),
                  sourceGeometryChanges=0, oldTerrainApprovalTransferred=False, installationApproved=False, permanentRejection=False,
                  qualification='Fresh revision-fenced government terrain is a separate immutable source identity. Exact wall-only compatibility diagnostic, no approval of remaining geometry, neighbour placement, publication or old terrain.')
    save(D / 'summary.json', result)
    refs.extend(p for p in LOCAL.rglob('*') if p.is_file() and p != LEASE)
    refs.extend(HERE / n for n in ['xl-second-pass.py', 'exact_packed_world_geometry_20261009.py', 'exact_original_triangle_pair_column_gap_20261010.py'])
    refs.extend([HERE.parent / 'citywide-source/discover.py', HERE.parent / 'citywide-native/download.py', HERE.parent / 'landmark-acquisition/acquire.py'])
    module('fresh_nam_terrain_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B, 'fresh-government-terrain-exact-wall-context', refs, result)
    print({k: result[k] for k in ['archiveChanged', 'minimumGapM', 'unchangedWallClearancePass']}, flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--owned', action='store_true')
    if p.parse_args().owned:
        return owned()
    assert not D.exists() and not LOCAL.exists()
    claim = reservations.claim(B + '-' + str(uuid.uuid4()), ['building:' + UID, 'immutable-source-proof:' + B], batch=B, ttl=3600)
    assert claim['ok']
    lease = claim['reservation']
    try:
        save(LEASE, json.loads(json.dumps(lease, default=str)))
        subprocess.run([sys.executable, str(HERE / 'bounded_reserved_runner_v2_20261022.py'), str(LEASE), sys.executable, __file__, '--owned'], cwd=ROOT, check=True)
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
