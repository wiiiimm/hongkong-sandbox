"""Exact primitive dimensions for a complete source cap-path partition; diagnostic only."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face, cross, sub


def primitive_dimension(face):
    f = rational_face(face)
    if any(cross(sub(f[1], f[0]), sub(f[2], f[0]))):
        return 2
    return int(len(set(f)) > 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ['batch', 'runtime', 'attributes', 'cap-paths', 'uid']:
        ap.add_argument('--' + name, required=True)
    a = ap.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, filename):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        path = base / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(a.runtime, 'selection.json.gz')
    source = next(r for r in selection['rows'] if r['uid'] == a.uid)
    attrs = take(a.attributes, 'attributes.json.gz')
    assert attrs['startEndAllInputsVerified']
    attr = next(r for r in attrs['rows'] if r['uid'] == a.uid)
    caps = take(a.cap_paths, 'summary.json')
    assert caps['uids'] == [a.uid]
    asset = ROOT / source['candidate']['path']
    sha = digest(asset.read_bytes())
    assert sha == source['sourceSHA256'] == attr['sourceSHA256'] == caps['sourceSHA256']
    refs.append(asset)
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    worlds = {'original': decode_original_world_triangles(asset.read_bytes())}
    for mode, field in [('literal', 'completeLiteralWorldPosition'),
                        ('left', 'completeExplicitLeftAssociatedFloat32WorldPosition'),
                        ('balanced', 'completeExplicitBalancedFloat32WorldPosition')]:
        worlds[mode] = np.asarray(attr[field]).reshape(-1, 3)[ix]
    assert len(caps['rows']) == 4 and set(worlds) == {r['mode'] for r in caps['rows']}
    rows = []
    for row in caps['rows']:
        triangles = worlds[row['mode']]
        assert digest(np.asarray(triangles).tobytes()) == row['sourceWorldSHA256']
        partition = row['completeGroundClearancePartition']
        assert len(triangles) == partition['completeSourceFaces']
        dimensions = [primitive_dimension(f) for f in triangles]
        nonrendering = [i for i, d in enumerate(dimensions) if d < 2]
        assert nonrendering == partition['nonrenderingSourceFaces']
        negative = set(partition['negativeSourceFaces'])
        exceptions = set(partition['negativeNonWallFaces'])
        assert exceptions <= set(nonrendering), 'A real surface needs separate interpretation'
        paths = partition['paths']
        assert len(paths) == len({p['sourceFace'] for p in paths})
        assert {p['sourceFace'] for p in paths} == negative - exceptions
        assert all(p['hasExactSharedEdgeClearCapPath'] for p in paths)
        assert not row['initialSharedEdgeUnresolvedFaces']
        for p in paths:
            assert p['originalPath'][0] == p['sourceFace']
            assert all(dimensions[i] == 2 for i in p['originalPath']), 'Degenerate bridge forbidden'
        rows.append(dict(mode=row['mode'], completeSourceFaces=len(triangles),
                         sourceWorldSHA256=row['sourceWorldSHA256'],
                         nonrenderingDimensions={str(i): dimensions[i] for i in nonrendering},
                         negativeNonWallDimensions={str(i): dimensions[i] for i in sorted(exceptions)},
                         renderingNegativeFacesWithExistingCapPaths=len(paths),
                         noDegenerateCapPathBridge=True,
                         rawAllAffectedHavePaths=partition['allAffectedHavePaths']))
    result = dict(uids=[a.uid], sourceSHA256=sha, rows=rows,
                  rawAllFourCompleteGroundClearCapPaths=caps['allFourCompleteGroundClearCapPaths'],
                  allNegativeNonWallPrimitivesExactlyBelowSurfaceDimension=True,
                  sourceGeometryChanges=0, physicalAcceptance=False, identityAccepted=False,
                  installationApproved=False, publication=False,
                  qualification='Exact rational rank in each complete coordinate stream. Original nonrendering primitives remain in the asset and grant no support, bridge, contact or cap credit. Existing cap paths are bound without changing raw failures; identity, authored-interface and browser review remain separate.')
    save(out / 'summary.json', result)
    refs.extend(HERE / n for n in ['exact_packed_world_geometry_20261009.py',
                                  'exact_original_shell_intersections_20261009.py'])
    module('degenerate_partition_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'complete-original-four-world-exact-primitive-dimension-partition', refs, result)
    print(dict(uid=a.uid, modes=len(rows), rawCapAcceptance=caps['allFourCompleteGroundClearCapPaths'], installationApproved=False), flush=True)


if __name__ == '__main__':
    main()
