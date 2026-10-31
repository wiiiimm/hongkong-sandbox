"""Account for exact dimensions of saved negative ground pairs; no acceptance.

All primitives and raw warnings remain. A line/point supplies no surface or root.
"""
import argparse
import sys
import uuid
from pathlib import Path

import numpy as np

from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_four_world_degenerate_partition_v1_20261026 import primitive_dimension
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['batch', 'runtime', 'attributes', 'clearance', 'uid']:
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--lease')
    args = parser.parse_args()
    base = ROOT / 'docs/astra-city/government-import'
    assert all(n.startswith('government-xl-') and '/' not in n
               for n in [args.batch, args.runtime, args.attributes, args.clearance])
    out, local = base / args.batch, HERE / 'local' / args.batch
    assert not out.exists()
    if not args.lease:
        assert not local.exists()
        claim = reservations.claim('negative-ground-dimensions-' + str(uuid.uuid4()),
                                   ['building:' + args.uid], batch=args.batch, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], local / 'reservation.json',
                                [sys.executable, __file__, *sys.argv[1:],
                                 '--lease', str(local / 'reservation.json')])
    lease = read(Path(args.lease))
    assert reservations.owns(lease) and 'building:' + args.uid in lease['resources']
    pins, refs = {}, [Path(__file__)]

    def take(batch, path):
        if batch not in pins:
            _, pins[batch] = authenticate(base / batch)
            refs.append(base / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selected = take(args.runtime, base / args.runtime / 'selection.json.gz')
    source = next(r for r in selected['rows'] if r['uid'] == args.uid)
    geometry = next(r for r in take(args.runtime, HERE / 'local' / args.runtime / 'runtime-geometry.json.gz')['rows'] if r['uid'] == args.uid)
    attr = next(r for r in take(args.attributes, base / args.attributes / 'attributes.json.gz')['rows'] if r['uid'] == args.uid)
    asset = ROOT / source['candidate']['path']
    assert digest(asset.read_bytes()) == source['sourceSHA256'] == geometry['sourceSHA256'] == attr['sourceSHA256']
    refs.append(asset)
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    worlds = {'original': decode_original_world_triangles(asset.read_bytes())}
    for mode, field in [('literal', 'completeLiteralWorldPosition'),
                        ('left', 'completeExplicitLeftAssociatedFloat32WorldPosition'),
                        ('balanced', 'completeExplicitBalancedFloat32WorldPosition')]:
        worlds[mode] = np.asarray(attr[field], dtype='<f8').reshape(-1, 3)[ix]
    ground = np.asarray(geometry['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    dimensions, rows = {}, []
    for mode, triangles in worlds.items():
        proof = take(args.clearance, base / args.clearance / (mode + '.json.gz'))
        assert proof['sourceWorldSHA256'] == digest(triangles.tobytes())
        assert proof['groundSHA256'] == digest(ground.tobytes())
        assert proof['completeSourceFaces'] == len(triangles) == source['triangles']
        faces = []
        for face in proof['rows']:
            i = face['sourceFace']
            assert np.array_equal(triangles[i], np.asarray(face['vertices'], dtype='<f8'))
            pairs = []
            for pair in face['negativeGroundPairProofs']:
                j = pair['groundFace']
                assert 0 <= j < len(ground)
                if j not in dimensions:
                    dimensions[j] = primitive_dimension(ground[j])
                pairs.append(dict(groundFace=j, exactPrimitiveDimension=dimensions[j],
                                  vertices=ground[j].tolist()))
            normal = np.cross(triangles[i][1] - triangles[i][0], triangles[i][2] - triangles[i][0])
            upward = face['absoluteNormalYRatio'] is not None and face['absoluteNormalYRatio'] >= .25 and normal[1] > 0
            faces.append(dict(sourceFace=i, upwardNonWall=bool(upward),
                              negativeGroundPairs=pairs,
                              hasNegativeGroundSurfacePair=any(p['exactPrimitiveDimension'] == 2 for p in pairs)))
        rows.append(dict(mode=mode, sourceWorldSHA256=proof['sourceWorldSHA256'],
                         groundSHA256=proof['groundSHA256'], faces=faces,
                         upwardFacesWithNegativeGroundSurfacePairs=[f['sourceFace'] for f in faces if f['upwardNonWall'] and f['hasNegativeGroundSurfacePair']],
                         upwardFacesWithOnlyNegativeLineOrPointPairs=[f['sourceFace'] for f in faces if f['upwardNonWall'] and not f['hasNegativeGroundSurfacePair']]))
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selected['manifestSHA256']
    assert reservations.owns(lease)
    result = dict(uids=[args.uid], sourceSHA256=source['sourceSHA256'], rows=rows,
                  rawGroundWarningsPreserved=True, noGroundOrSourcePrimitiveOmitted=True,
                  geometryChanges=0, physicalAcceptance=False, sourceRoleAccepted=False,
                  installationApproved=False, publication=False,
                  qualification='Exact rational primitive rank of every saved negative ground pair, bound to complete source/ground arrays in all four streams. Dimension zero/one is retained context, not a surface, terrain height, support or cap root. Raw finite-column warnings remain unchanged. Production native-terrain.js excludes zero projected determinant from its height field; no new geometric or acceptance exception is introduced.')
    save(out / 'summary.json', result)
    refs.extend([manifest, ROOT / '3d-viewer/city/native-terrain.js',
                 HERE / 'original_four_world_degenerate_partition_v1_20261026.py',
                 HERE / 'exact_original_shell_intersections_20261009.py',
                 HERE / 'exact_packed_world_geometry_20261009.py'])
    module('negative_ground_dimensions_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        args.batch, 'four-world-exact-negative-ground-primitive-dimensions',
        list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
