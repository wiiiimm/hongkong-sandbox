"""Replay the existing strict finite terrain-edge guard without editing meshes."""
import numpy as np
from original_terrain_point_contact_v1_20261025 import extent
from coordinated_native_boundary_v1_20261023 import seam_segments, seam_comparison_report

CONTRACT = 'existing-finite-native-shared-edge-context-v1'


def rendered_triangles(node, bounds):
    assert not node.get('patches') and not node.get('children')
    mesh = node['nativeMesh']
    positions = np.asarray(mesh['position'], dtype='<f4').astype('<f8').reshape(-1, 3)
    indices = mesh['index']
    assert indices and len(indices) % 3 == 0
    assert all(type(i) is int and 0 <= i < len(positions) for i in indices)
    assert np.isfinite(positions).all()
    assert np.all(positions[:, 0] >= bounds[0]) and np.all(positions[:, 0] <= bounds[2])
    assert np.all(positions[:, 2] >= bounds[1]) and np.all(positions[:, 2] <= bounds[3])
    return positions[np.asarray(indices).reshape(-1, 3)]


def verify(scope, candidate, root, old_by_url):
    assert not scope['touchingNativeUids'] and scope['positiveAreaTerrainOverlaps'] == 0
    contacts = scope['terrainContacts']
    assert contacts and len(contacts) == len(old_by_url)
    assert set(old_by_url) == {r['url'] for r in contacts}
    for node in [candidate, *old_by_url.values()]:
        a, b, c, d = node['coarseCells']
        assert all(type(v) is int for v in [a, b, c, d])
        assert 0 <= a < c < root['w'] and 0 <= b < d < root['h']
    bounds = extent(candidate, root)
    assert bounds == scope['regionalParentExtent']
    current = rendered_triangles(candidate, bounds)
    rows = []
    for c in contacts:
        old = old_by_url[c['url']]
        assert old['meta']['parentTerrain'] == candidate['meta']['parentTerrain']
        assert old['meta']['parentSha256'] == candidate['meta']['parentSha256']
        other = extent(old, root)
        assert other == c['extent'] and c['coarseOverlapAreaM2'] == 0
        packed = c['packedContacts']
        assert len(packed) == 1 and packed[0]['hierarchy'] == []
        assert packed[0]['overlapAreaM2'] == 0 and packed[0]['packedBounds'] == other
        xlo, xhi = max(bounds[0], other[0]), min(bounds[2], other[2])
        zlo, zhi = max(bounds[1], other[1]), min(bounds[3], other[3])
        assert (xlo == xhi and zlo < zhi) or (zlo == zhi and xlo < xhi)
        axis, coordinate, start, end = ((0, xlo, zlo, zhi) if xlo == xhi else (2, zlo, xlo, xhi))
        previous = rendered_triangles(old, other)
        left = seam_segments(current, axis, coordinate, start, end)
        right = seam_segments(previous, axis, coordinate, start, end)
        report = seam_comparison_report(left, right, start, end)
        assert report['passed'] and report['toleranceM'] == .01
        rows.append(dict(url=c['url'], axis=axis, coordinate=coordinate, interval=[start, end],
            completeCandidateFaces=len(current), completeOldFaces=len(previous),
            candidateFiniteSegments=len(left), oldFiniteSegments=len(right), comparison=report))
    return dict(contract=CONTRACT, rows=rows, sourceGeometryChanges=0, terrainGeometryChanges=0,
        installationApproved=False, publication=False)
