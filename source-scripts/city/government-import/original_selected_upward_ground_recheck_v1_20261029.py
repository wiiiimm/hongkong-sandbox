"""Recheck only nominated upward facets against a new complete drawn ground.

This is a bounded follow-up, never a replacement for whole-source acceptance.
"""
import argparse
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'attributes', 'context']:
        parser.add_argument('--' + key, required=True)
    a = parser.parse_args()
    base = ROOT / 'docs/astra-city/government-import'
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    out = base / a.batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, path):
        if batch not in pins:
            _, pins[batch] = authenticate(base / batch)
            refs.append(base / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    context = take(a.context, base / a.context / 'summary.json')
    uid = context['uid']
    assert context['uids'] == [uid] and context['installationApproved'] is False
    selection = take(a.runtime, base / a.runtime / 'selection.json.gz')
    source = next(r for r in selection['rows'] if r['uid'] == uid)
    runtime = take(a.runtime, HERE / 'local' / a.runtime / 'runtime-geometry.json.gz')
    captured = next(r for r in runtime['rows'] if r['uid'] == uid)
    attrs = take(a.attributes, base / a.attributes / 'attributes.json.gz')
    assert attrs['startEndAllInputsVerified']
    attr = next(r for r in attrs['rows'] if r['uid'] == uid)
    asset = ROOT / source['candidate']['path']
    assert digest(asset.read_bytes()) == context['sourceSHA256'] == source['sourceSHA256'] == captured['sourceSHA256'] == attr['sourceSHA256']
    refs.append(asset)
    original = decode_original_world_triangles(asset.read_bytes())
    index = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    worlds = dict(original=original)
    for mode, field in [('literal', 'completeLiteralWorldPosition'), ('left', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('balanced', 'completeExplicitBalancedFloat32WorldPosition')]:
        worlds[mode] = np.asarray(attr[field], dtype='<f8').reshape(-1, 3)[index]
    assert np.array_equal(worlds['literal'], np.asarray(captured['position']).reshape(-1, 3)[np.asarray(captured['index']).reshape(-1, 3)])
    ids = [r['face'] for r in context['rows']]
    assert ids and len(ids) == len(set(ids))
    assert np.array_equal(original[ids], np.asarray([r['vertices'] for r in context['rows']]))
    ground = np.asarray(captured['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    low, high = ground[:, :, [0, 2]].min(1), ground[:, :, [0, 2]].max(1)
    rows = []
    for mode, triangles in worlds.items():
        faces = []
        for i in ids:
            triangle = triangles[i]
            xz = triangle[:, [0, 2]]
            candidates = np.flatnonzero(np.all(high >= xz.min(0), axis=1) & np.all(low <= xz.max(0), axis=1))
            proofs = [dict(groundFace=int(j), proof=verify(triangle, ground[j])) for j in candidates]
            gaps = [Fraction(r['proof']['exactMinimumFiniteColumnGapM']) for r in proofs if r['proof']['exactClosedHorizontalProjectionsMeet']]
            assert gaps
            faces.append(dict(sourceFace=i, inclusiveCandidateGroundFaces=list(map(int, candidates)), proofs=proofs, minimumFiniteGapM=str(min(gaps)), clearanceLimitPassed=min(gaps) >= Fraction(-1, 2)))
        record = dict(mode=mode, sourceWorldSHA256=digest(triangles.astype('<f8').tobytes()), completeDrawnGroundSHA256=digest(ground.tobytes()), completeDrawnGroundFaces=len(ground), rows=faces)
        save(out / (mode + '.json.gz'), record)
        rows.append(dict(mode=mode, faces=[dict(sourceFace=r['sourceFace'], minimumFiniteGapM=r['minimumFiniteGapM'], clearanceLimitPassed=r['clearanceLimitPassed']) for r in faces]))
    result = dict(uids=[uid], sourceSHA256=source['sourceSHA256'], sourceFaces=ids, rows=rows, allSelectedFacetsClear=all(f['clearanceLimitPassed'] for r in rows for f in r['faces']), sourceGeometryChanges=0, sourcePoseChanges=0, physicalAcceptance=False, installationApproved=False, qualification='Only exact nominated facets rechecked against every inclusive ground candidate, including vertical/collapsed terrain primitives. All other source facets, projection coverage, neighbours, original roles, visible terrain return and publication remain separate obligations.')
    save(out / 'summary.json', result)
    refs.extend([HERE / 'exact_packed_world_geometry_20261009.py', HERE / 'exact_original_triangle_pair_column_gap_20261010.py'])
    module('selected_upward_ground_recheck', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'bounded-four-stream-selected-original-upward-ground-recheck', refs, result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
