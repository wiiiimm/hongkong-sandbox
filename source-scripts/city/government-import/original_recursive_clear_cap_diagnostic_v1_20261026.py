"""Expand exact internal contacts beyond the initially affected wall facets.

Diagnostic only. A path is connectivity to an already proven clear upward
facet, not footing, support, physical-role or publication approval.
"""
import argparse
from collections import deque
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts


def expand(tri, negative, initial):
    normal = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    size = np.linalg.norm(normal, axis=1)
    real = set(map(int, np.flatnonzero(size > 0)))
    walls = {i for i in real if abs(normal[i, 1]) <= .25 * size[i]}
    eligible = walls | (real - set(negative))
    caps = {i for i in eligible if normal[i, 1] > .25 * size[i]}
    scans = {}
    def neighbours(i):
        if i not in scans:
            scan = exact_finite_contacts(tri, [i], tri, range(len(tri)))
            assert scan['allPairsExamined'] and not scan['sourceFacesOmitted']
            scans[i] = [c for c in scan['contacts'] if c['sourceFaceB'] != i
                        and c['dimension'] > 0
                        and c['sourcePrimitiveDimensionA'] == c['sourcePrimitiveDimensionB'] == 2]
        return sorted({c['sourceFaceB'] for c in scans[i]} & eligible)
    rows = []
    for start in initial:
        assert start in walls and start in negative
        queue, parents, end = deque([start]), {start: None}, None
        while queue:
            i = queue.popleft()
            if i in caps:
                end = i
                break
            for j in neighbours(i):
                if j not in parents:
                    parents[j] = i
                    queue.append(j)
        path = []
        if end is not None:
            while end is not None:
                path.append(end)
                end = parents[end]
            path.reverse()
        rows.append(dict(sourceFace=start, hasPositiveFiniteClearCapPath=bool(path),
                         originalFacePath=path, visitedFaces=sorted(parents)))
    return dict(rows=rows, exactPositiveContactsByScannedFace={str(i): c for i, c in sorted(scans.items())},
                allUnresolvedHavePaths=all(r['hasPositiveFiniteClearCapPath'] for r in rows),
                completeSourceFaces=len(tri), sourceWorldSHA256=digest(tri.tobytes()))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'runtime', 'attributes', 'clearance', 'uid']:
        p.add_argument('--' + k, required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    def take(batch, path):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selection = take(a.runtime, base / a.runtime / 'selection.json.gz')
    row = next(r for r in selection['rows'] if r['uid'] == a.uid)
    attributes = take(a.attributes, base / a.attributes / 'attributes.json.gz')
    assert attributes['startEndAllInputsVerified']
    attr = next(r for r in attributes['rows'] if r['uid'] == a.uid)
    asset = ROOT / row['candidate']['path']
    raw = asset.read_bytes()
    assert digest(raw) == row['sourceSHA256'] == attr['sourceSHA256']
    refs.append(asset)
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    worlds = dict(original=decode_original_world_triangles(raw), **{
        n: np.asarray(attr[k], dtype='<f8').reshape(-1, 3)[ix] for n, k in [
            ('literal', 'completeLiteralWorldPosition'),
            ('left', 'completeExplicitLeftAssociatedFloat32WorldPosition'),
            ('balanced', 'completeExplicitBalancedFloat32WorldPosition')]})
    rows = []
    for mode, tri in worlds.items():
        prior = take(a.clearance, base / a.clearance / (mode + '-cap-paths.json.gz'))
        assert digest(tri.tobytes()) == prior['sourceWorldSHA256']
        unresolved = [r['sourceFace'] for r in prior['proof']['paths'] if not r['hasExactSharedEdgeClearCapPath']]
        detail = expand(tri, prior['proof']['negativeSourceFaces'], unresolved)
        save(out / (mode + '.json.gz'), detail)
        summary = dict(mode=mode, initialUnresolved=len(unresolved),
                       resolved=sum(r['hasPositiveFiniteClearCapPath'] for r in detail['rows']),
                       unresolved=[r['sourceFace'] for r in detail['rows'] if not r['hasPositiveFiniteClearCapPath']],
                       exactScannedFaces=len(detail['exactPositiveContactsByScannedFace']))
        rows.append(summary)
        print(summary, flush=True)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    result = dict(uids=[a.uid], sourceSHA256=row['sourceSHA256'], rows=rows,
                  installationApproved=False, physicalAcceptance=False, publication=False,
                  sourceGeometryChanges=0, sourcePoseChanges=0,
                  qualification='Recursive exact positive-dimensional original surface contacts, including intermediate unaffected facets. Caps exclude every complete-ground negative face. Raw prior cap failures retained. No support, ground root or physical acceptance follows from source connectivity.')
    save(out / 'summary.json', result)
    refs.extend(HERE / n for n in ['exact_packed_world_geometry_20261009.py',
                'exact_original_finite_triangle_contacts_20261010.py',
                'exact_original_shell_intersections_20261009.py', 'exact_original_component_contacts_20261009.py'])
    module('recursive_cap_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'original-recursive-positive-finite-clear-cap-diagnostic', refs, result)


if __name__ == '__main__':
    main()
