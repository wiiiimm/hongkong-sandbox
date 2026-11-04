"""Recover pinned government terrain for explicit original sources, without model edits."""
import argparse
import json
import uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, connect, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'capture', 'source-directory']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--uid', action='append', required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / args.batch, HERE / 'local' / args.batch
    assert not doc.exists() and not local.exists()
    cap = base / args.capture
    _, pins = authenticate(cap)
    refs = [Path(__file__), cap / 'result.json']
    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selected = take(cap / 'selection.json.gz')['rows']
    wanted = set(args.uid)
    rows = [r for r in selected if r['uid'] in wanted]
    assert len(rows) == len(wanted) == len(args.uid)
    assert len({r['native']['cacheKey'] for r in rows}) == 1
    runtime = {r['uid']: r for r in take(HERE / 'local' / cap.name / 'runtime-geometry.json.gz')['rows']}
    directorypath = ROOT / args.source_directory
    assert directorypath.resolve().is_relative_to(ROOT)
    directory = read(directorypath)
    key = rows[0]['native']['cacheKey']
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        sheet, source_sha, result_sha, native = db.execute('SELECT i.sheet,i.source_sha,r.result_sha,r.result FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s', (key,)).fetchone()
    assert all(r['native']['resultSha'] == result_sha for r in rows)
    assert directory['sheet'] == sheet
    expected = digest(json.dumps([directory['sourceURL'], directory['etag'], directory['directorySHA256']], separators=(',', ':')).encode())
    assert expected == source_sha, 'Cached directory does not identify the exact native source revision'
    refs.append(directorypath)
    for row in rows:
        model = next(m for m in native['models'] if m['modelId'] == row['modelId'])
        assert model['asset']['sha256'] == row['sourceSHA256'] == runtime[row['uid']]['sourceSHA256']
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256']
        refs.append(asset)
        tile = ROOT / '3d-viewer' / row['source']['tile']
        assert next(b for b in read(tile)['buildings'] if b['uid'] == row['uid']) == row['source']['building']
        refs.append(tile)
    claim = reservations.claim(args.batch + '-' + str(uuid.uuid4()), ['source-terrain:' + sheet] + ['building:' + uid for uid in sorted(wanted)], batch=args.batch, ttl=3600)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        save(local / 'reservation.json', json.loads(json.dumps(lease, default=str)))
        decoder = module('selected_original_terrain_recovery', HERE / 'xl-second-pass.py')
        decoder.LOCAL = local
        recovery = decoder.source_sheet(sheet, [], directory, {}, [])
        paths = [ROOT / name for name in recovery['terrainPaths']]
        assert paths
        for record in native.get('terrain', []):
            for name, sha in record.get('sourceHashes', {}).items():
                matches = [p.parent / Path(name).name for p in paths if p.name == Path(record['sourceEntry']).name]
                assert len(matches) == 1 and digest(matches[0].read_bytes()) == sha
        ground = np.concatenate([decoder.terrain_triangles(path) for path in paths])
        for proofpath in (local / 'terrain-repairs').glob('*/proof.json'):
            proof = read(proofpath)
            assert proof['state'] == 'prepared-geometry-only' and proof['sourceGeometryChanged'] is False
            assert proof['geometryProof']['sourcePositionsAndIndicesPreserved']
        final = module('selected_recovered_foundation', HERE / 'xl-final-script-pass.py')
        results = []
        for row in rows:
            uid = row['uid']
            g = runtime[uid]
            tri = np.asarray(g['position']).reshape(-1, 3)[np.asarray(g['index']).reshape(-1, 3)]
            lo, hi = tri.min((0, 1)), tri.max((0, 1))
            subset = ground[(ground[:, :, 0].max(1) >= lo[0]-10) & (ground[:, :, 0].min(1) <= hi[0]+10) & (ground[:, :, 2].max(1) >= lo[2]-10) & (ground[:, :, 2].min(1) <= hi[2]+10)]
            building = row['source']['building']
            foundation = final.foundation_context(tri, subset, Polygon(building['rings'][0], building['rings'][1:]))
            result = dict(uid=uid, sourceSHA256=row['sourceSHA256'], nativeResultSHA256=result_sha, status='original-terrain-checked', sourceTerrainPaths=recovery['terrainPaths'], originalTerrainFoundation=foundation, installationApproved=False)
            save(doc / (uid.split('/')[1] + '.json'), result)
            results.append(result)
            print(dict(uid=uid, faces=foundation['triangles'], covered=foundation['completeTerrainTriangles'], buried=foundation['fullyBuriedTriangles']), flush=True)
        assert reservations.owns(lease)
        save(doc / 'source-recovery.json', dict(sheet=sheet, sourceSHA256=source_sha, nativeCacheKey=key, nativeResultSHA256=result_sha, recovery=recovery, priorTerrainOutcomes=native.get('terrain', [])))
        result = dict(uids=sorted(wanted), rows=results, terrainFaces=len(ground), originalSourceRevisionVerified=True, installationApproved=False, publication=False, sourceGeometryChanges=0, scriptExternalAICalls=0)
        save(doc / 'summary.json', result)
        refs.extend(path for path in local.rglob('*') if path.is_file() and path.name != 'reservation.json')
        refs.extend([HERE / 'xl-second-pass.py', HERE / 'xl-final-script-pass.py'])
        module('selected_recovery_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'pinned-selected-original-terrain-recovery', list(dict.fromkeys(refs)), result)
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
