"""Deterministically recover exact cached adjacent originals, with no modelling."""
import argparse
import uuid
import zipfile
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--lookup', required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / a.batch, HERE / 'local' / a.batch
    assert not doc.exists() and not local.exists()
    _, pins = authenticate(base / a.lookup)
    path = base / a.lookup / 'lookup.json'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    lookup = read(path)
    assert lookup['rows'] and all(r['matchCount'] == len(r['matchedOriginalModels']) == 1 for r in lookup['rows'])
    models = [r['matchedOriginalModels'][0] for r in lookup['rows']]
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s', (lookup['nativeCacheKey'],)).fetchone()[0] == lookup['nativeResultSHA256']
        sheet = db.execute('SELECT sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=%s', (lookup['nativeCacheKey'],)).fetchone()[0]
        prior = db.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1", (sheet,)).fetchone()[0]
    keys = ['native-model:' + lookup['nativeCacheKey'] + ':' + m['modelId'] for m in models]
    claim = reservations.claim(a.batch + '-' + str(uuid.uuid4()), keys, batch=a.batch, ttl=1800)
    assert claim['ok']
    lease = claim['reservation']
    refs = [Path(__file__), base / a.lookup / 'result.json', path]
    rows = []
    try:
        helper = module('exact_adjacent_source_recovery', HERE / 'xl-second-pass.py')
        directory, _ = helper.recovery.scan(dict(SHEETNO=sheet, Format_glTF=prior['sourceURL'], REVISIONDATE=prior['revision']), local / 'directory')
        assert directory['etag'] == prior['etag'] and directory['directorySHA256'] == prior['directorySHA256'], 'Pinned original directory changed'
        ids = {m['modelId'] for m in models}
        directory['models'] = [m for m in directory['models'] if m['modelId'] in ids]
        assert {m['modelId'] for m in directory['models']} == ids
        helper.acquire(directory, local / 'directory/zip-directory.bin', local / 'original', include_terrain=False)
        packed = local / 'packed'
        packed.mkdir()
        with zipfile.ZipFile(local / 'original' / (sheet + '.zip')) as z:
            for record, model in zip(lookup['rows'], models):
                assert reservations.owns(lease)
                converted = helper._convert_one(z, z.getinfo(model['sourceEntry']), local / 'decoded', packed, {}, dict(modelId=model['modelId']))
                assert converted['triangles'] == model['triangles']
                sha = model['asset']['sha256']
                raw = helper.recovery.canonical_bytes((packed / converted['asset']['asset']).read_bytes(), sha)
                assert digest(raw) == sha and len(raw) == model['asset']['bytes']
                asset = local / 'assets' / (sha + '.glb.gz')
                asset.parent.mkdir(exist_ok=True)
                asset.write_bytes(raw)
                tri = decode_original_world_triangles(raw)
                assert len(tri) == model['triangles']
                rows.append(dict(uid=record['uid'], currentForm=record['currentForm'], model=model,
                                 sourceSHA256=sha, asset=dict(path=str(asset.relative_to(ROOT)), sha256=sha),
                                 completeSourceFaces=len(tri), originalWorldSHA256=digest(tri.tobytes()),
                                 worldBounds=dict(min=tri.min((0, 1)).tolist(), max=tri.max((0, 1)).tolist())))
    finally:
        assert reservations.release(lease)['ok']
    result = dict(uids=lookup['uids'], relatedUIDs=lookup['relatedUIDs'], rows=rows,
                  nativeCacheKey=lookup['nativeCacheKey'], nativeResultSHA256=lookup['nativeResultSHA256'],
                  sourceGeometryChanges=0, sourceRecovered=True, installationApproved=False, permanentRejection=False,
                  qualification='Exact prior compressed original bytes recovered using existing government ETag/range/CRC acquisition and deterministic conversion. No AI geometry generation, support acceptance, identity approval or publication.')
    save(doc / 'summary.json', result)
    refs.extend(p for p in local.rglob('*') if p.is_file())
    refs.extend(HERE / n for n in ['xl-second-pass.py', 'exact_packed_world_geometry_20261009.py'])
    refs.extend(HERE.parent / n for n in ['citywide-native/download.py', 'citywide-native/convert.py', 'enhancement-screening/shape_prepare.py'])
    module('exact_adjacent_acquire_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'exact-explicit-adjacent-government-original-recovery', refs, result)
    print([(r['uid'], r['completeSourceFaces']) for r in rows], flush=True)


if __name__ == '__main__':
    main()
