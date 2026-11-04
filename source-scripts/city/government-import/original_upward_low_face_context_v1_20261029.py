"""Bind exact upward original faces from complete four-stream clearance proofs.

Only adapts the evidence schema used by the existing private terrain-return
constructor. It grants no terrain, source-role or installation approval.
"""
import argparse
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT / 'docs/astra-city/government-import'


def upward_ids(triangles, records):
    selected = []
    for row in records:
        i = row['sourceFace']
        triangle = triangles[i]
        assert np.array_equal(triangle, np.asarray(row['vertices'], dtype='<f8'))
        normal = np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
        length = float(np.linalg.norm(normal))
        if length and normal[1] > .35 * length and Fraction(row['minimumFiniteGapM']) < Fraction(-1, 2):
            selected.append(i)
    assert len(selected) == len(set(selected))
    return sorted(selected)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'attributes', 'low-faces', 'uid']:
        p.add_argument('--' + key, required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    out = BASE / a.batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, path):
        if batch not in pins:
            _, pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(a.runtime, BASE / a.runtime / 'selection.json.gz')
    source = next(r for r in selection['rows'] if r['uid'] == a.uid)
    runtime = take(a.runtime, HERE / 'local' / a.runtime / 'runtime-geometry.json.gz')
    groundrow = next(r for r in runtime['rows'] if r['uid'] == a.uid)
    attributes = take(a.attributes, BASE / a.attributes / 'attributes.json.gz')
    assert attributes['startEndAllInputsVerified']
    attr = next(r for r in attributes['rows'] if r['uid'] == a.uid)
    low = take(a.low_faces, BASE / a.low_faces / 'summary.json')
    assert low['uids'] == [a.uid]
    asset = ROOT / source['candidate']['path']
    assert digest(asset.read_bytes()) == source['sourceSHA256'] == attr['sourceSHA256'] == groundrow['sourceSHA256'] == low['sourceSHA256']
    refs.append(asset)
    original = decode_original_world_triangles(asset.read_bytes())
    index = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    worlds = {'original': original}
    for mode, field in [('literal', 'completeLiteralWorldPosition'), ('left', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('balanced', 'completeExplicitBalancedFloat32WorldPosition')]:
        worlds[mode] = np.asarray(attr[field], dtype='<f8').reshape(-1, 3)[index]
    captured = np.asarray(groundrow['position']).reshape(-1, 3)[np.asarray(groundrow['index']).reshape(-1, 3)]
    assert np.array_equal(worlds['literal'], captured)
    ground = np.asarray(groundrow['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    groundsha = digest(ground.tobytes())
    selected, mode_bindings = {}, []
    for mode, triangles in worlds.items():
        proof = take(a.low_faces, BASE / a.low_faces / (mode + '.json.gz'))
        assert proof['sourceWorldSHA256'] == digest(triangles.astype('<f8').tobytes())
        assert proof['groundSHA256'] == groundsha and proof['completeSourceFaces'] == len(triangles)
        selected[mode] = upward_ids(triangles, proof['rows'])
        mode_bindings.append(dict(mode=mode, sourceWorldSHA256=proof['sourceWorldSHA256'], groundSHA256=groundsha, sourceFaces=selected[mode]))
    ids = selected['original']
    assert ids and all(v == ids for v in selected.values()), 'Need the same actual upward conflicts in all four streams'
    delta = float(np.abs(original - worlds['literal']).max())
    assert delta <= 1e-9
    rows = []
    for i in ids:
        t = original[i]
        n = np.cross(t[1] - t[0], t[2] - t[0])
        rows.append(dict(face=i, vertices=t.tolist(), literalVertices=worlds['literal'][i].tolist(), normalYRatio=float(n[1] / np.linalg.norm(n)), projectedAreaM2=float(n[1] / 2), yRange=[float(t[:, 1].min()), float(t[:, 1].max())]))
    result = dict(uids=[a.uid], uid=a.uid, sourceSHA256=source['sourceSHA256'], rows=rows, allFourCoordinateBindings=mode_bindings, originalLiteralMaximumDeltaM=delta, completeDrawnGroundSHA256=groundsha, sourceGeometryChanges=0, sourcePoseChanges=0, terrainChanges=0, physicalAcceptance=False, installationApproved=False, qualification='Exact positive-normal original facets with rational finite-column gap below -0.5m in all four representations. Schema adaptation only; no role, terrain construction or publication approval.')
    save(out / 'summary.json', result)
    refs.append(HERE / 'exact_packed_world_geometry_20261009.py')
    module('upward_low_face_context_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'exact-four-stream-upward-original-ground-conflict-context', refs, result)
    print(dict(uid=a.uid, faces=ids), flush=True)


if __name__ == '__main__':
    main()
