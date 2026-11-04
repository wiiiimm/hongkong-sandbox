"""Restore one unchanged prepared original from its authenticated sheet bundle."""
import os
import shutil
import sys
import tarfile
from pathlib import Path
from dotenv import dotenv_values
from run import ROOT, HERE, read, save, digest, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

sys.path.insert(0, str(HERE.parent / 'landmark-resume'))
from r2_snapshot import R2Store, verify_object


def main():
    batch = 'government-xl-oceanwalk-neighbour32653-restored-v1-20261029'
    base = ROOT / 'docs/astra-city/government-import'
    out, local = base / batch, HERE / 'local' / batch
    assert not out.exists()
    assert not local.exists() or (local.is_dir() and not any(local.iterdir()))
    lookup = base / 'government-xl-oceanwalk81743-neighbour32653-lookup-v1-20261029'
    _, pins = authenticate(lookup)
    path = lookup / 'lookup.json'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    source = read(path)
    row, = source['rows']
    model, = row['matchedOriginalModels']
    assert row['uid'] == 'landsd/32653:0' and model['modelId'] == 'B144962595101063C0'
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        sha, record = db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s', (source['nativeCacheKey'],)).fetchone()
    assert sha == source['nativeResultSHA256']
    assert next(m for m in record['models'] if m['modelId'] == model['modelId']) == model
    artifact, = [a for a in record['artifacts'] if a['kind'] == 'original-and-prepared-sheet']
    assert artifact['key'] == 'astra-modelling/objects/sha256/' + artifact['sha256'][:2] + '/' + artifact['sha256']
    assert 0 < artifact['bytes'] < 32_000_000
    assert shutil.disk_usage(ROOT).free >= 3 * 1024**3 + 2 * artifact['bytes']
    for name, value in dotenv_values(ROOT / '.env.modelling').items():
        if name.startswith('R2_') and value:
            os.environ.setdefault(name, value)
    local.mkdir(parents=True, exist_ok=True)
    bundle = local / (artifact['sha256'] + '.tar.gz')
    verify_object(R2Store('hk-sandbox-assets'), artifact['key'], artifact['sha256'], artifact['bytes'], bundle)
    asset = model['asset']
    assert asset['asset'] == 'assets/' + asset['sha256'] + '.glb.gz'
    assert asset['bytes'] == 1523
    with tarfile.open(bundle, 'r:gz') as archive:
        member, = [m for m in archive.getmembers() if m.name == 'converted/' + asset['asset']]
        assert member.isfile() and member.size == asset['bytes']
        with archive.extractfile(member) as stream:
            raw = stream.read(asset['bytes'] + 1)
    assert len(raw) == asset['bytes'] and digest(raw) == asset['sha256']
    triangles = decode_original_world_triangles(raw)
    import numpy as np
    assert len(triangles) == model['triangles'] == 60 and np.isfinite(triangles).all()
    target = local / asset['asset']
    target.parent.mkdir()
    with target.open('xb') as stream:
        stream.write(raw)
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s', (source['nativeCacheKey'],)).fetchone()[0] == sha
    result = dict(uids=[row['uid']], nativeCacheKey=source['nativeCacheKey'], nativeResultSHA256=sha,
                  sourceSHA256=asset['sha256'], recoveredBytes=len(raw), originalFaces=60,
                  sourceGeometryChanges=0, installationApproved=False, publication=False,
                  acquisitionFloorBytes=3 * 1024**3, acquisitionGuardChanged=False,
                  qualification='Exact original prepared bytes restored from checksum-verified immutable sheet bundle. Identity, placement, support and publication remain unapproved.')
    save(out / 'source-record.json', dict(model=model, artifact=artifact))
    module('neighbour_restore_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        batch, 'exact-cached-original-neighbour-byte-recovery',
        [Path(__file__), lookup / 'result.json', path, bundle, target, HERE.parent / 'landmark-resume/r2_snapshot.py', HERE / 'exact_packed_world_geometry_20261009.py'], result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
