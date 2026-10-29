"""Recover already-indexed prepared bytes from a cached original glTF only.

The output must match the existing native asset SHA/size exactly. This is not
new source acquisition, geometry simplification, optimisation or acceptance.
"""
import argparse
import gzip
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['batch', 'lookup', 'raw-root']: p.add_argument('--' + name, required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    out, local = base / a.batch, HERE / 'local' / a.batch
    assert not out.exists()
    lookup_dir = base / a.lookup
    _, pins = authenticate(lookup_dir)
    path = lookup_dir / 'lookup.json'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    rows = read(path)['rows']
    assert 0 < len(rows) <= 20 and len(rows) == len({r['uid'] for r in rows})
    assert all(len(r['matches']) == 1 for r in rows)
    raw_root = (ROOT / a.raw_root).resolve()
    assert raw_root.is_relative_to(ROOT / 'source-scripts/city') and raw_root.is_dir()
    leasepath = local / 'reservation.json'
    if not a.owned:
        assert not local.exists()
        resources = ['building:' + r['uid'] for r in rows] + ['native-model:' + r['matches'][0]['sourceKey'] for r in rows]
        claim = reservations.claim('cached-raw-exact-recovery-' + str(uuid.uuid4()), sorted(resources), batch=a.batch, ttl=1800)
        assert claim['ok']
        return execute_reserved(claim['reservation'], leasepath, [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(leasepath)
    assert reservations.owns(lease)
    converter = module('cached_raw_original_converter', HERE.parent / 'citywide-native/convert.py')
    headers = module('cached_raw_exact_header', HERE.parent / 'enhancement-screening/shape_prepare.py')
    refs, restored = [Path(__file__), lookup_dir / 'result.json', path], []
    for row in rows:
        match = row['matches'][0]
        model = match['model']
        assert model['candidate']['uid'] == row['uid']
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            sha, native = db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s', (match['nativeCacheKey'],)).fetchone()
        assert sha == match['nativeResultSHA256'] and next(m for m in native['models'] if m['modelId'] == model['modelId']) == model
        source = raw_root / converter.safe_member(model['sourceEntry'])
        assert source.resolve().is_relative_to(raw_root) and source.name == model['modelId'] + '.gltf'
        data = read(source)
        source_refs = [source]
        for buffer in data['buffers']:
            member = source.parent / converter.safe_member(buffer['uri'])
            assert member.resolve().is_relative_to(raw_root) and 0 < buffer['byteLength'] < 64 * 1024**2
            assert member.stat().st_size >= buffer['byteLength']
            source_refs.append(member)
        original_hashes = {str(f.relative_to(ROOT)): digest(f.read_bytes()) for f in source_refs}
        converter.validate_geometry(data, source.parent)
        glb, stats = converter._packer.pack(source)
        asset = model['asset']
        assert stats['triangles'] == model['triangles'] and stats['vertices'] == asset['indexedVertices']
        assert stats['decodedGeometryBytes'] == asset['decodedGeometryBytes'] and len(glb) == asset['glbBytes']
        raw = headers.canonical_bytes(gzip.compress(glb, mtime=0), asset['sha256'])
        assert digest(raw) == asset['sha256'] and len(raw) == asset['bytes']
        triangles = decode_original_world_triangles(raw)
        assert len(triangles) == model['triangles'] and np.isfinite(triangles).all()
        bounds = np.array([triangles.min((0, 1)), triangles.max((0, 1))])
        assert np.max(np.abs(bounds - np.asarray(model['worldBounds']))) < 1e-6
        target = local / 'assets' / (asset['sha256'] + '.glb.gz')
        target.parent.mkdir(exist_ok=True)
        with target.open('xb') as stream: stream.write(raw)
        target.chmod(0o444)
        for name, sha in original_hashes.items(): assert digest((ROOT / name).read_bytes()) == sha
        refs.extend([*source_refs, target])
        restored.append(dict(uid=row['uid'], modelId=model['modelId'], asset=dict(path=str(target.relative_to(ROOT)), sha256=asset['sha256'], bytes=len(raw)),
            originalTriangles=len(triangles), originalWorldBounds=bounds.tolist(), sourceFiles=original_hashes,
            expandedAttributeVerification=stats, nativeCacheKey=match['nativeCacheKey'], nativeResultSHA256=match['nativeResultSHA256']))
        print(dict(uid=row['uid'], exactPreparedSHA256=asset['sha256'], bytes=len(raw), originalFaces=len(triangles)), flush=True)
    result = dict(uids=[r['uid'] for r in rows], rows=restored, sourceRecovered=True,
                  downloads=0, archiveAcquisitionCalls=0, acquisitionGuardChanged=False,
                  sourceGeometryChanges=0, sourcePoseChanges=0, installationApproved=False, publication=False,
                  qualification='Cached original GLTF/buffers repacked through the unchanged existing bit-preserving packer. Every expanded attribute, scene/node/material transform, full face count and final prepared asset SHA/size are verified. Exact existing native bytes only; no new geometry recipe/variant, download, source pose/scale change, identity or placement approval.')
    save(out / 'summary.json', result)
    refs.extend(converter.converter_dependencies())
    refs.append(Path(headers.__file__))
    assert reservations.owns(lease)
    module('cached_raw_exact_recovery_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'exact-indexed-prepared-original-recovered-from-cached-gltf', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
