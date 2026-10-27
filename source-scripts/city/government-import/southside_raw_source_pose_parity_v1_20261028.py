"""Check cached government glTF transforms against exact indexed packed originals."""
import argparse
import gzip
import subprocess
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-southside-raw-source-pose-parity-v1-20261028'
DOC, LOCAL = BASE/BATCH, HERE/'local'/BATCH
LEASE = LOCAL/'reservation.json'
CAP = BASE/'government-xl-southside-project-original-recovery-v1-20261028'
UIDS = {'landsd/311759:0', 'landsd/311763:0', 'landsd/330243:0', 'landsd/330244:0', 'landsd/315025:0'}


def owned():
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists() and {'building:' + u for u in UIDS} <= set(lease['resources'])
    _, pins = authenticate(CAP)
    path = CAP/'selection.json.gz'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    rows = [r for r in read(path)['rows'] if r['uid'] in UIDS]
    assert {r['uid'] for r in rows} == UIDS
    requested = {r['modelId'] + '.gltf': r['uid'] for r in rows}
    files = subprocess.check_output(['rg', '--files', '--hidden', '--no-ignore', '-g', '*.gltf', 'source-scripts/city'], cwd=ROOT, text=True).splitlines()
    found = {u: [] for u in UIDS}
    for name in files:
        uid = requested.get(Path(name).name)
        if uid:
            found[uid].append(ROOT/name)
    assert all(len(v) == 1 for v in found.values()), 'Raw source absent/ambiguous; do not choose an unverified replacement'
    conversion = module('southside_raw_parity_converter', HERE.parent/'citywide-native/convert.py')
    context = module('southside_raw_parity_context', HERE/'pending-context.py')
    refs = [Path(__file__), CAP/'result.json', path, Path(conversion.__file__), Path(context.__file__),
            HERE/'exact_packed_world_geometry_20261009.py', Path(conversion._packer.__file__)]
    report = []
    for row in rows:
        gltf = found[row['uid']][0]
        data = read(gltf)
        refs.append(gltf)
        for buffer in data['buffers']:
            member = (gltf.parent/buffer['uri']).resolve()
            assert member.is_relative_to(ROOT.resolve())
            refs.append(member)
        expected = ROOT/row['candidate']['path']
        assert digest(expected.read_bytes()) == row['sourceSHA256']
        refs.append(expected)
        glb, stats = conversion._packer.pack(gltf)
        packed = gzip.compress(glb, mtime=0)
        repacked_sha = digest(packed)
        # Repacking is a private parity test, not source geometry correction.
        out = LOCAL/'repacked'/(repacked_sha + '.glb.gz')
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(packed); refs.append(out)
        raw = context.triangles(gltf)
        original = decode_original_world_triangles(expected.read_bytes())
        same_shape = raw.shape == original.shape
        delta = np.max(abs(raw-original), axis=(0, 1)).tolist() if same_shape else None
        report.append(dict(uid=row['uid'], modelId=row['modelId'], indexedSourceSHA256=row['sourceSHA256'],
                           cachedRawGLTF=dict(path=str(gltf.relative_to(ROOT)), sha256=digest(gltf.read_bytes())),
                           repackedSHA256=repacked_sha, exactRepackedAssetMatches=repacked_sha == row['sourceSHA256'],
                           rawFaces=len(raw), packedFaces=len(original), triangleOrderAndCountMatch=same_shape,
                           maximumRawToPackedCoordinateDeltaM=delta,
                           rawWorldBounds=[raw.min((0, 1)).tolist(), raw.max((0, 1)).tolist()],
                           packedWorldBounds=[original.min((0, 1)).tolist(), original.max((0, 1)).tolist()],
                           recordedBaseHeight=row['source']['building']['baseHeightHKPD']))
        assert stats['triangles'] == row['triangles']
        assert reservations.owns(lease)
    result = dict(uids=sorted(UIDS), rows=report, sourceGeometryChanges=0, modelGeometryChanges=0,
                  allFiveRepackedAssetsMatch=all(r['exactRepackedAssetMatches'] for r in report),
                  allRawWorldPosesMatchPacked=all(r['triangleOrderAndCountMatch'] and max(r['maximumRawToPackedCoordinateDeltaM']) < 1e-8 for r in report),
                  identityAccepted=False, physicalAccepted=False, installationApproved=False,
                  qualification='Cached raw government glTF/node transforms independently decoded and repacked with the existing geometry-only packer, compared with exact indexed assets. Raw buffers and transforms retained. A matching pose rules out this packing/decoding path as the source of observed offsets for these five units; it does not prove completeness of the source scene, identify missing structural parts or authorize translation, new geometry, identity/physical acceptance or installation.')
    save(DOC/'summary.json', result)
    assert reservations.owns(lease)
    module('southside_raw_source_pose_parity_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'cached-raw-government-gltf-and-indexed-packed-world-pose-parity', list(dict.fromkeys(refs)), result)
    print(dict(allFiveRepackedAssetsMatch=result['allFiveRepackedAssetsMatch'], allWorldPosesMatch=result['allRawWorldPosesMatchPacked']), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    if args.owned:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    claim = reservations.claim('southside-raw-source-pose-parity-' + str(uuid.uuid4()),
                               ['building:' + u for u in sorted(UIDS)], batch=BATCH, ttl=3600)
    assert claim['ok']
    execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])


if __name__ == '__main__':
    main()
