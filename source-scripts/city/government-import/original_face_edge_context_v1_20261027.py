"""Exact represented-edge context for selected original faces; no role approval.

Point contacts, nearby vertices and partial edges do not join components. An open
edge here means unmatched in this representation, not a hole in the real building.
"""
from collections import defaultdict
from pathlib import Path
import argparse
import numpy as np


def inspect_faces(triangles, faces):
    tri = np.asarray(triangles, dtype='<f8')
    assert tri.ndim == 3 and tri.shape[1:] == (3, 3) and len(tri)
    assert np.isfinite(tri).all()
    assert faces == sorted(set(faces)) and faces
    assert all(type(i) is int and 0 <= i < len(tri) for i in faces)
    cross = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    size = np.linalg.norm(cross, axis=1)
    edges = defaultdict(list)
    face_edges = {}
    for i, vertices in enumerate(tri):
        if size[i] == 0:
            continue
        v = [tuple(p) for p in vertices]
        keys = {tuple(sorted((a, b))) for a, b in zip(v, v[1:] + v[:1]) if a != b}
        face_edges[i] = keys
        for key in keys:
            edges[key].append(i)
    component_by_face, components = {}, []
    for root in sorted(face_edges):
        if root in component_by_face:
            continue
        component_id = len(components)
        members, stack = [], [root]
        component_by_face[root] = component_id
        while stack:
            i = stack.pop()
            members.append(i)
            for edge in face_edges[i]:
                for j in edges[edge]:
                    if j not in component_by_face:
                        component_by_face[j] = component_id
                        stack.append(j)
        components.append(sorted(members))

    def describe(i):
        return dict(sourceFace=i, vertices=tri[i].tolist(),
                    signedNormalY=float(cross[i, 1] / size[i]) if size[i] else None,
                    doubleAreaM2=float(size[i]))

    rows = []
    for i in faces:
        row = describe(i)
        cid = component_by_face.get(i)
        row['componentId'] = cid
        row['edgeNeighbours'] = [describe(j) for j in sorted({
            j for edge in face_edges.get(i, ()) for j in edges[edge] if j != i})]
        row['edgeIncidenceCounts'] = sorted(len(edges[e]) for e in face_edges.get(i, ()))
        rows.append(row)
    selected_components = sorted({component_by_face[i] for i in faces if i in component_by_face})
    summaries = []
    for cid in selected_components:
        members = components[cid]
        keys = {edge for i in members for edge in face_edges[i]}
        summaries.append(dict(componentId=cid, sourceFaces=members,
                              bounds=[tri[members].min((0, 1)).tolist(), tri[members].max((0, 1)).tolist()],
                              upwardFaces=sum(bool(cross[i, 1] > .25 * size[i]) for i in members),
                              downwardFaces=sum(bool(cross[i, 1] < -.25 * size[i]) for i in members),
                              unmatchedRepresentedEdges=sum(len(edges[e]) == 1 for e in keys),
                              nonManifoldRepresentedEdges=sum(len(edges[e]) > 2 for e in keys)))
    return dict(contract='exact-represented-whole-edge-context-v1', completeSourceFaces=len(tri),
                rows=rows, components=summaries, sourceGeometryChanges=0, sourcePoseChanges=0,
                groundRootCredit=False, sourceRoleAccepted=False, physicalAcceptance=False,
                installationApproved=False, publication=False)


def main():
    from run import ROOT, HERE, read, save, digest, reservations
    from china_ferry_current_foundations_v1_20261020 import authenticate
    from exact_packed_world_geometry_20261009 import decode_original_world_triangles
    from primrose_compound_foundation_v2_20261015 import module
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'low-faces', 'uid', 'lease']:
        p.add_argument('--' + key, required=True)
    p.add_argument('--faces', required=True, help='Comma-separated exact original face indices')
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    lease = read(Path(a.lease))
    assert reservations.owns(lease), 'An independently owned live lease is required'
    assert 'building:' + a.uid in lease['resources']
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, filename):
        if batch not in pins:
            _, pins[batch] = authenticate(base / batch)
            refs.append(base / batch / 'result.json')
        path = base / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    source = next(r for r in take(a.runtime, 'selection.json.gz')['rows'] if r['uid'] == a.uid)
    low = take(a.low_faces, 'original.json.gz')
    asset = ROOT / source['candidate']['path']
    raw = asset.read_bytes()
    assert digest(raw) == source['sourceSHA256']
    refs.extend([asset, HERE / 'exact_packed_world_geometry_20261009.py'])
    tri = decode_original_world_triangles(raw)
    assert len(tri) == source['triangles'] == low['completeSourceFaces']
    assert digest(tri.astype('<f8').tobytes()) == low['sourceWorldSHA256']
    faces = [int(i) for i in a.faces.split(',')]
    negative = {r['sourceFace']: r for r in low['rows']}
    assert set(faces) <= set(negative), 'Every selected face must belong to the complete negative partition'
    result = inspect_faces(tri, faces)
    for row in result['rows']:
        row['existingGroundDiagnostic'] = negative[row['sourceFace']]
    result.update(uids=[a.uid], sourceSHA256=source['sourceSHA256'],
                  sourceWorldSHA256=low['sourceWorldSHA256'], groundSHA256=low['groundSHA256'],
                  worldsInspected=['original'], qualification='Topology only. Normal orientation and edge '
                  'connectivity do not establish a floor, underside, solid interior or acceptable burial. '
                  'No partial-contact or proximity bridges; other represented worlds remain separate evidence.')
    assert reservations.owns(lease)
    save(out / 'context.json.gz', result)
    summary = {k: v for k, v in result.items() if k not in ['rows', 'components']}
    summary.update(selectedFaces=faces, selectedComponents=len(result['components']))
    save(out / 'summary.json', summary)
    module('face_edge_context_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'exact-original-selected-face-edge-context-no-role-approval', refs, summary)
    print(summary, flush=True)


if __name__ == '__main__':
    main()
