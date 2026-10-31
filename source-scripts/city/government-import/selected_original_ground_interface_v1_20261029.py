"""Measure selected source/ground interfaces without granting role or root credit."""
import argparse
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from exact_original_triangle_pair_column_gap_20261010 import verify


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'attributes', 'uid']:
        p.add_argument('--' + key, required=True)
    p.add_argument('--face', type=int, action='append', required=True)
    a = p.parse_args()
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert a.batch.startswith('government-xl-') and '/' not in a.batch and not out.exists()
    ids = sorted(a.face)
    assert len(ids) == len(set(ids))
    pins, refs = {}, [Path(__file__)]

    def take(batch, path):
        if batch not in pins:
            _, pins[batch] = authenticate(base / batch)
            refs.append(base / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(a.runtime, base / a.runtime / 'selection.json.gz')
    source = next(r for r in selection['rows'] if r['uid'] == a.uid)
    runtime = take(a.runtime, HERE / 'local' / a.runtime / 'runtime-geometry.json.gz')
    captured = next(r for r in runtime['rows'] if r['uid'] == a.uid)
    attributes = take(a.attributes, base / a.attributes / 'attributes.json.gz')
    assert attributes['startEndAllInputsVerified']
    attr = next(r for r in attributes['rows'] if r['uid'] == a.uid)
    asset = ROOT / source['candidate']['path']
    assert digest(asset.read_bytes()) == source['sourceSHA256'] == captured['sourceSHA256'] == attr['sourceSHA256']
    refs.append(asset)
    original = decode_original_world_triangles(asset.read_bytes())
    assert all(0 <= i < len(original) for i in ids)
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    worlds = dict(original=original)
    for mode, field in [('literal', 'completeLiteralWorldPosition'), ('left', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('balanced', 'completeExplicitBalancedFloat32WorldPosition')]:
        worlds[mode] = np.asarray(attr[field], dtype='<f8').reshape(-1, 3)[ix]
    assert np.array_equal(worlds['literal'], np.asarray(captured['position']).reshape(-1, 3)[np.asarray(captured['index']).reshape(-1, 3)])
    ground = np.asarray(captured['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    lo, hi = ground[:, :, [0, 2]].min(1), ground[:, :, [0, 2]].max(1)
    rows = []
    for mode, triangles in worlds.items():
        proof = exact_finite_contacts(triangles, ids, ground, list(range(len(ground))))
        positive = [r for r in proof['contacts'] if r['dimension'] > 0 and r['sourcePrimitiveDimensionA'] == r['sourcePrimitiveDimensionB'] == 2]
        faces = []
        for i in ids:
            t = triangles[i]
            n = np.cross(t[1] - t[0], t[2] - t[0])
            length = float(np.linalg.norm(n))
            assert length > 0
            point = t[int(np.argmax(t[:, 1]))]
            candidates = np.flatnonzero(np.all(lo <= point[[0, 2]], axis=1) & np.all(hi >= point[[0, 2]], axis=1))
            exposed = [dict(groundFace=int(j), proof=verify(np.repeat(point[None, :], 3, axis=0), ground[j])) for j in candidates]
            gaps = [Fraction(r['proof']['exactMinimumFiniteColumnGapM']) for r in exposed if r['proof']['exactClosedHorizontalProjectionsMeet']]
            assert gaps
            faces.append(dict(sourceFace=i, signedNormalYRatio=float(n[1] / length), sourceVertices=t.tolist(), positiveFiniteSurfaceContacts=sum(r['sourceFaceA'] == i for r in positive), highestOriginalVertex=point.tolist(), highestVertexMinimumGapM=str(min(gaps)), highestVertexAboveEveryGroundFacet=min(gaps) > 0, highestVertexProofs=exposed))
        record = dict(mode=mode, sourceWorldSHA256=digest(triangles.astype('<f8').tobytes()), completeGroundSHA256=digest(ground.tobytes()), completeGroundFaces=len(ground), contactProof=proof, faces=faces)
        save(out / (mode + '.json.gz'), record)
        rows.append(dict(mode=mode, faces=[{k: v for k, v in f.items() if k not in ['highestVertexProofs', 'sourceVertices']} for f in faces]))
    result = dict(uids=[a.uid], sourceSHA256=source['sourceSHA256'], sourceFaces=ids, rows=rows, allSelectedFacesIntersectAndRemainExposed=all(f['positiveFiniteSurfaceContacts'] > 0 and f['highestVertexAboveEveryGroundFacet'] for r in rows for f in r['faces']), sourceGeometryChanges=0, sourcePoseChanges=0, structuralRootAccepted=False, physicalAcceptance=False, installationApproved=False, qualification='Exact selected original facets against all drawn ground facets, with inclusive exposed-point checks in all four source representations. No face-role, basement, structural/root, whole-source or installation approval follows.')
    save(out / 'summary.json', result)
    refs.extend([HERE / 'exact_packed_world_geometry_20261009.py', HERE / 'exact_original_finite_triangle_contacts_20261010.py', HERE / 'exact_original_triangle_pair_column_gap_20261010.py'])
    module('selected_original_ground_interface', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'selected-four-world-original-drawn-ground-interface-context', refs, result)
    print(dict(uid=a.uid, selectedFaces=len(ids), allIntersectAndExposed=result['allSelectedFacesIntersectAndRemainExposed']), flush=True)


if __name__ == '__main__':
    main()
