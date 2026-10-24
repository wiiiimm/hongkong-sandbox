"""Prove closed terrain domains meet at one unchanged parent-grid vertex only.

Shared edges, area overlaps, children and non-flat point columns are rejected.
This changes no mesh, clearance tolerance or ordinary overlap admission rule.
"""
from fractions import Fraction as F
import numpy as np


def extent(node, root):
    c = node['coarseCells']; g = root['meta']['georef']; size = root['cell']
    assert len(c) == 4 and all(type(v) is int for v in c)
    assert g['aE'] == size and g['aN'] == -size
    return [g['bE'] + c[0]*size - 834500, 816500-g['bN'] + c[1]*size,
            g['bE'] + c[2]*size - 834500, 816500-g['bN'] + c[3]*size]


def mesh_column(node, bounds, point):
    assert not node.get('children'), 'Children require their own complete proof'
    mesh = node['nativeMesh']; positions = np.asarray(mesh['position'], dtype='<f8').reshape(-1, 3)
    indices = np.asarray(mesh['index'])
    assert indices.ndim == 1 and len(indices) % 3 == 0 and len(indices) > 0
    assert np.issubdtype(indices.dtype, np.integer) and indices.min() >= 0 and indices.max() < len(positions)
    assert np.isfinite(positions).all()
    rows = []
    for mode, p in [('literal', positions), ('float32', positions.astype('<f4').astype('<f8'))]:
        assert np.all(p[:, 0] >= bounds[0]) and np.all(p[:, 0] <= bounds[2])
        assert np.all(p[:, 2] >= bounds[1]) and np.all(p[:, 2] <= bounds[3])
        used = p[indices]
        corner = used[(used[:, 0] == point[0]) & (used[:, 2] == point[1])]
        assert len(corner), 'Closed mesh must contain the common point'
        heights = np.unique(corner[:, 1]); assert len(heights) == 1, 'Vertical or split point column'
        rows.append(dict(mode=mode, completeIndexedFaces=len(indices)//3,
                         point=[point[0], float(heights[0]), point[1]]))
    assert rows[0]['point'] == rows[1]['point']
    return rows


def verify(scope, candidate, root, old_by_url):
    assert not scope['touchingNativeUids'] and scope['positiveAreaTerrainOverlaps'] == 0
    contacts = scope['terrainContacts']; assert contacts
    assert set(old_by_url) == {r['url'] for r in contacts} and len(old_by_url) == len(contacts)
    bounds = extent(candidate, root); assert bounds == scope['regionalParentExtent']
    output = []
    for contact in contacts:
        old = old_by_url[contact['url']]; old_bounds = extent(old, root)
        assert old_bounds == contact['extent'] and contact['coarseOverlapAreaM2'] == 0
        assert len(contact['packedContacts']) == 1
        packed = contact['packedContacts'][0]
        assert packed['hierarchy'] == [] and packed['overlapAreaM2'] == 0
        assert packed['packedBounds'] == old_bounds
        xlo, xhi = max(bounds[0], old_bounds[0]), min(bounds[2], old_bounds[2])
        zlo, zhi = max(bounds[1], old_bounds[1]), min(bounds[3], old_bounds[3])
        assert xlo == xhi and zlo == zhi, 'Only a single shared corner is admitted'
        point = [xlo, zlo]
        new_rows = mesh_column(candidate, bounds, point)
        old_rows = mesh_column(old, old_bounds, point)
        g = root['meta']['georef']; size = F(root['cell'])
        col = (F(xlo)+834500-F(g['bE']))/size
        row = (F(zlo)-816500+F(g['bN']))/size
        assert col.denominator == row.denominator == 1
        col, row = int(col), int(row)
        assert 0 <= col < root['w'] and 0 <= row < root['h']
        parent = root['elev'][row*root['w']+col]
        assert np.isfinite(parent) and float(np.float32(parent)) == parent
        assert all(r['point'] == [xlo, parent, zlo] for r in new_rows + old_rows)
        output.append(dict(url=contact['url'], newBounds=bounds, oldBounds=old_bounds,
                           sharedPoint=[xlo, parent, zlo], parentGrid=[col, row],
                           newMeshModes=new_rows, unchangedOldMeshModes=old_rows,
                           noPositiveAreaOrSharedEdge=True, exactParentVertexAgreement=True))
    return dict(contract='exact-original-terrain-single-point-contact-v1', rows=output,
                sourceGeometryChanges=0, terrainGeometryChanges=0,
                installationApproved=False, publication=False)
