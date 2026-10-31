"""Revision-fenced government terrain recovery; exact original member hashes only."""
import argparse, hashlib, json, subprocess, sys, uuid, zipfile
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0, str(HERE.parent / 'citywide-source'))
from discover import scan
sys.path.insert(0, str(HERE.parent / 'citywide-native'))
from download import acquire, safe

B = 'government-xl-missing-original-terrain-restore-v3-20261023'
BASE = ROOT / 'docs/astra-city/government-import'
D, LOCAL = BASE / B, HERE / 'local' / B
PRIOR = 'government-xl-missing-original-terrain-restore-v1-20261023'
LEASE = LOCAL / 'reservation.json'


def owned():
    assert not D.exists()
    lease = read(LEASE)
    assert reservations.owns(lease)
    _, pins = authenticate(BASE / PRIOR)
    p = BASE / PRIOR / 'source-records.json'
    assert digest(p.read_bytes()) == pins[str(p.relative_to(ROOT))]
    records = read(p)
    refs = [Path(__file__), BASE / PRIOR / 'result.json', p,
            HERE.parent / 'citywide-source/discover.py',
            HERE.parent / 'citywide-native/download.py',
            HERE.parent / 'landmark-acquisition/acquire.py']
    keys = [r['cacheKey'] for r in records]
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        native = {key: dict(sourceSHA=source_sha, resultSHA=result_sha) for key, source_sha, result_sha in db.execute('SELECT i.cache_key,i.source_sha,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=ANY(%s)', (keys,)).fetchall()}
        directories = db.execute('SELECT sheet,result FROM astra_modelling.city_source_directories WHERE sheet=ANY(%s) ORDER BY sheet,created_at DESC', ([r['sheet'] for r in records],)).fetchall()
    outcomes = []
    for record in sorted(records, key=lambda r: r['sheet']):
        assert reservations.owns(lease)
        key, sheet = record['cacheKey'], record['sheet']
        assert native[key]['resultSHA'] == record['resultSHA256']
        folder = LOCAL / key
        folder.mkdir(parents=True, exist_ok=True)
        files, error, received = {}, None, 0
        try:
            priors = [r for s, r in directories if s == sheet and hashlib.sha256(json.dumps([r['sourceURL'], r['etag'], r['directorySHA256']], separators=(',', ':')).encode()).hexdigest() == native[key]['sourceSHA']]
            assert priors, 'Pinned source directory not available'
            prior = priors[0]
            save(folder / 'pinned-directory.json', prior)
            current, _ = scan(dict(SHEETNO=sheet, Format_glTF=prior['sourceURL'], REVISIONDATE=prior['revision']), folder / 'directory')
            assert (current['etag'], current['directorySHA256']) == (prior['etag'], prior['directorySHA256']), 'Source revision changed; historical approval must not transfer'
            # Existing acquisition verifies ETag, ranges, source CRCs and dependencies.
            current['models'] = []
            download = acquire(current, folder / 'directory/zip-directory.bin', folder / 'download', include_terrain=True)
            received = read(folder / 'download/transfer.json')['receivedBytes']
            expected = {}
            for terrain in record['terrain']:
                for name, sha in terrain['sourceHashes'].items():
                    safe(name)
                    assert Path(name).suffix in ['.gltf', '.bin']
                    assert name not in expected or expected[name] == sha
                    expected[name] = sha
            assert expected
            with zipfile.ZipFile(folder / 'download' / (sheet + '.zip')) as archive:
                names = archive.namelist()
                for name, sha in sorted(expected.items()):
                    assert names.count(name) == 1 and archive.getinfo(name).file_size < 100_000_000
                    raw = archive.read(name)
                    assert digest(raw) == sha, 'Original terrain member differs from pinned native source'
                    path = folder / 'original-terrain' / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(raw)
                    files[name] = dict(path=str(path.relative_to(ROOT)), sha256=sha)
            for terrain in record['terrain']:
                path = ROOT / files[terrain['sourceEntry']]['path']
                for buffer in read(path).get('buffers', []):
                    member = (path.parent / buffer['uri']).resolve()
                    assert member.is_relative_to((folder / 'original-terrain').resolve())
                    assert str(member.relative_to(folder / 'original-terrain')) in files
        except Exception as exc:
            error = dict(type=type(exc).__name__, reason=str(exc))
        assert reservations.owns(lease)
        row = dict(cacheKey=key, sheet=sheet, nativeSourceSHA256=native[key]['sourceSHA'], nativeResultSHA256=record['resultSHA256'], status='exact-original-terrain-restored' if error is None else 'source-recovery-investigation', files=files, error=error, receivedBytes=received, installationApproved=False, permanentRejection=False)
        save(D / (key + '.json'), row)
        outcomes.append(row)
        refs.extend(p for p in folder.rglob('*') if p.is_file())
        print(dict(sheet=sheet, status=row['status'], files=len(files), error=error), flush=True)
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for key, value in native.items():
            assert db.execute('SELECT i.source_sha,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s', (key,)).fetchone() == (value['sourceSHA'], value['resultSHA'])
    summary = dict(uids=read(BASE / PRIOR / 'result.json')['uids'], rows=outcomes, sourceSheets=len(records), restoredSheets=sum(r['error'] is None for r in outcomes), receivedBytes=sum(r['receivedBytes'] for r in outcomes), originalTerrainPaths=[q['path'] for r in outcomes if r['error'] is None for n, q in r['files'].items() if n.endswith('.gltf')], sourceGeometryChanges=0, newlyInstalled=0, installationApproved=False, permanentRejection=False, scriptExternalAICalls=0, qualification='Original government terrain recovered through existing ETag/directory/range/CRC-fenced downloader under original-source leases. Every requested JSON/binary SHA matches the exact native source result. No terrain/model geometry processing, placement approval, publication or source-corruption inference.')
    save(D / 'summary.json', summary)
    module('missing_terrain_source_restore_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B, 'revision-fenced-government-original-terrain-recovery', refs, summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--owned', action='store_true')
    if parser.parse_args().owned:
        return owned()
    assert not D.exists() and not LOCAL.exists()
    prior = BASE / 'government-xl-all-200-original-terrain-batch-v2-20261022'
    _, pins = authenticate(prior)
    p = prior / 'summary.json'
    assert digest(p.read_bytes()) == pins[str(p.relative_to(ROOT))]
    rows = [r for r in read(p)['rows'] if r['status'] == 'source-terrain-recovery-required']
    claim = reservations.claim(B + '-' + str(uuid.uuid4()), sorted({'building:' + r['uid'] for r in rows} | {'immutable-source-proof:' + B}), batch=B, ttl=3600)
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
