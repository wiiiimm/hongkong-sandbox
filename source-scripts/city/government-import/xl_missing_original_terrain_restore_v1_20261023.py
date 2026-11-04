"""Recover exact archived terrain for the remaining XL sources; no acceptance."""
from pathlib import Path, PurePosixPath
import io, os, sys, tarfile, zipfile
from run import ROOT, HERE, read, save, digest, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from dotenv import dotenv_values
sys.path.insert(0, str(HERE.parent / 'landmark-resume'))
from r2_snapshot import R2Store, verify_object, key_for

B = 'government-xl-missing-original-terrain-restore-v1-20261023'
BASE = ROOT / 'docs/astra-city/government-import'
D, LOCAL = BASE / B, HERE / 'local' / B
PRIOR = 'government-xl-all-200-original-terrain-batch-v2-20261022'
INSTALLED = 'government-xl-fu-wong-retained-original-installed-v7-20261023'


def main():
    assert not D.exists()
    refs, bound = [Path(__file__)], {}
    for name in [PRIOR, INSTALLED]:
        _, pins = authenticate(BASE / name)
        refs.append(BASE / name / 'result.json')
        bound[name] = pins
    def take(name, filename):
        p = BASE / name / filename
        assert digest(p.read_bytes()) == bound[name][str(p.relative_to(ROOT))]
        refs.append(p)
        return read(p)
    pending = {r['sourceKey'] for r in take(INSTALLED, 'full-xl-current-count.json')['rows'] if not r['installedVerified']}
    wanted = [r for r in take(PRIOR, 'summary.json')['rows'] if r['sourceKey'] in pending and r['status'] == 'source-terrain-recovery-required']
    groups = {}
    for row in wanted:
        groups.setdefault(row['nativeCacheKey'], []).append(row)
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        records = db.execute('SELECT i.cache_key,i.sheet,r.result_sha,r.result FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=ANY(%s)', (sorted(groups),)).fetchall()
    assert {r[0] for r in records} == set(groups)
    save(D / 'source-records.json', [dict(cacheKey=k, sheet=s, resultSHA256=h, terrain=r['terrain'], artifacts=r['artifacts']) for k, s, h, r in records])
    for k, v in dotenv_values(ROOT / '.env.modelling').items():
        if k.startswith('R2_') and v and v != '[SENSITIVE]':
            os.environ.setdefault(k, v)
    store, outcomes = R2Store('hk-sandbox-assets'), []
    for key, sheet, result_sha, result in sorted(records):
        folder = LOCAL / key
        folder.mkdir(parents=True, exist_ok=True)
        expected = {}
        for terrain in result['terrain']:
            assert terrain['sourceEntry'] in terrain['sourceHashes']
            for name, sha in terrain['sourceHashes'].items():
                path = PurePosixPath(name)
                assert not path.is_absolute() and '..' not in path.parts and '\\' not in name
                assert path.suffix in ['.gltf', '.bin']
                assert name not in expected or expected[name] == sha
                expected[name] = sha
        assert expected
        found, archives, error = {}, [], None
        def accept(name, raw):
            if name not in expected:
                return
            assert digest(raw) == expected[name], 'Archived terrain differs from pinned original source'
            path = folder / 'original-terrain' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                assert path.read_bytes() == raw
            else:
                path.write_bytes(raw)
            found[name] = dict(path=str(path.relative_to(ROOT)), sha256=expected[name])
        try:
            for artifact in result['artifacts']:
                assert artifact['kind'] == 'original-and-prepared-sheet'
                assert artifact['key'] == key_for(artifact['sha256'])
                assert 0 < artifact['bytes'] <= 100_000_000
                bundle = folder / (artifact['sha256'] + '.tar.gz')
                verify_object(store, artifact['key'], artifact['sha256'], artifact['bytes'], bundle)
                refs.append(bundle)
                archives.append(dict(path=str(bundle.relative_to(ROOT)), sha256=artifact['sha256']))
                with tarfile.open(bundle, 'r:gz') as tar:
                    for member in tar:
                        if not member.isfile() or not member.name.startswith('original/') or not member.name.endswith('.zip'):
                            continue
                        assert member.size <= 500_000_000
                        with tar.extractfile(member) as source, zipfile.ZipFile(io.BytesIO(source.read())) as archive:
                            names = archive.namelist()
                            for name in sorted(set(names) & set(expected)):
                                assert names.count(name) == 1 and archive.getinfo(name).file_size <= 100_000_000
                                accept(name, archive.read(name))
            assert set(found) == set(expected), dict(missing=sorted(set(expected) - set(found)))
            # Exact original glTF JSON and all source buffers are restored together.
            for terrain in result['terrain']:
                path = ROOT / found[terrain['sourceEntry']]['path']
                for buffer in read(path).get('buffers', []):
                    member = (path.parent / buffer['uri']).resolve()
                    assert member.is_relative_to((folder / 'original-terrain').resolve())
                    assert member.is_file() and str(member.relative_to(folder / 'original-terrain')) in found
        except Exception as exc:
            error = dict(type=type(exc).__name__, reason=str(exc))
        refs.extend(ROOT / r['path'] for r in found.values())
        row = dict(cacheKey=key, sheet=sheet, nativeResultSHA256=result_sha, uids=sorted(r['uid'] for r in groups[key]), sourceKeys=sorted(r['sourceKey'] for r in groups[key]), status='exact-original-terrain-restored' if error is None else 'terrain-cache-investigation', files=found, archives=archives, error=error, installationApproved=False, permanentRejection=False)
        save(D / (key + '.json'), row)
        outcomes.append(row)
        print(dict(sheet=sheet, status=row['status'], models=len(groups[key]), files=len(found)), flush=True)
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for key, _, result_sha, _ in records:
            assert db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s', (key,)).fetchone() == (result_sha,)
    summary = dict(rows=outcomes, selectedModels=len(wanted), sourceSheets=len(groups), restoredModels=sum(len(r['sourceKeys']) for r in outcomes if r['error'] is None), sourceGeometryChanges=0, installationApproved=False, permanentRejection=False, newlyInstalled=0, scriptExternalAICalls=0, qualification='Exact original terrain JSON/binary bytes recovered from checksum-verified immutable source bundles. No original model edits, terrain publication, current-scene approval or corruption inference. Full current identity/foundation/neighbour/runtime/browser acceptance remains separate.')
    save(D / 'summary.json', summary)
    module('missing_terrain_restore_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B, 'remaining-xl-exact-original-terrain-cache-recovery', refs + [D / 'source-records.json'], summary)


if __name__ == '__main__':
    main()
