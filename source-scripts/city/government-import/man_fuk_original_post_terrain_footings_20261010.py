"""Candidate-only terrain correction at four unchanged original post footings.

Leave the two higher vertices next to installed Man Oi unchanged. Only the
five measured near-footing repeated vertices change, never source geometry.
This is explicitly a changed terrain proposal; every physical gate must run.
"""
import copy
import hashlib
import numpy as np
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

SOURCE = '22b458321ca483c53324ee152cb27c382e5ac4dfd745974f169b1c551ac8a6c1'
POSITION = '23a1931086404739c49de69356bc7dce8907afbbcc169d88bc3c12c179b5dfa1'
INDEX = 'e6d01f8707b778eb0078e6ebade95258c02f8ee323026f174b1ed25c1c751450'
VERTICES = np.asarray([
    [1924.67578125, 39.05465316772461, -2940.19140625],
    [1932.5, 39.508056640625, -2938.003662109375],
    [1937.44140625, 39.796844482421875, -2936.7578125],
    [1946.4510498046875, 41.178794860839844, -2934.3271484375],
    [1947.60546875, 41.357879638671875, -2934.0703125],
])
POST_FACES = [list(range(start, start + 16)) for start in [263, 279, 295, 311]]


def sha(a):
    return hashlib.sha256(a.tobytes()).hexdigest()


def propose(patch, source):
    assert hashlib.sha256(source).hexdigest() == SOURCE, 'Complete original source changed'
    original = decode_original_world_triangles(source)
    assert original.shape == (10661, 3, 3)
    feet = [original[faces] for faces in POST_FACES]
    bottom = float(feet[0][:, :, 1].min())
    assert bottom == 39.994998931884766
    assert all(float(f[:, :, 1].min()) == bottom and
               float(f[:, :, 1].max()) == 43.053001403808594 for f in feet)
    p = np.asarray(patch['nativeMesh']['position'], np.float64).reshape(-1, 3)
    index = np.asarray(patch['nativeMesh']['index'], np.uint32).reshape(-1, 3)
    assert sha(p) == POSITION and sha(index) == INDEX, 'Complete prior terrain changed'
    changed = []
    by_vertex = []
    rendered = p.astype(np.float32).astype(np.float64)
    for v in VERTICES:
        ids = np.flatnonzero(np.all(rendered == v, axis=1))
        assert len(ids) > 0, 'Measured repeated terrain vertex absent'
        changed.extend(ids.tolist())
        by_vertex.append(dict(renderedBefore=v.tolist(),
                              completeRawBefore=p[ids].tolist(), records=ids.tolist()))
    changed = sorted(changed)
    assert len(changed) == len(set(changed))
    after = p.copy()
    after[changed, 1] = bottom
    assert np.array_equal(after[:, [0, 2]], p[:, [0, 2]])
    other = np.setdiff1d(np.arange(len(p)), changed)
    assert np.array_equal(after[other], p[other])
    assert float(np.abs(after[:, 1] - p[:, 1]).max()) < 1.37
    incident = np.flatnonzero(np.any(np.isin(index, changed), axis=1)).tolist()
    out = copy.deepcopy(patch)
    out['nativeMesh']['position'] = after.reshape(-1).tolist()
    assert out['nativeMesh']['index'] == patch['nativeMesh']['index']
    proof = dict(contract='man-fuk-four-original-post-terrain-footings-v1',
        sourceSHA256=SOURCE, completeOriginalFaces=10661,
        completeOriginalPostFaces=POST_FACES, originalFootingHeightHKPD=bottom,
        priorWholeTerrainPositionSHA256=POSITION, wholeTerrainIndexSHA256=INDEX,
        newWholeTerrainPositionSHA256=sha(after), changedVertices=by_vertex,
        changedTerrainVertexRecords=changed, changedIncidentTerrainFaces=incident,
        maximumAbsoluteVerticalChangeM=float(np.abs(after[:, 1] - p[:, 1]).max()),
        allTerrainHorizontalCoordinatesUnchanged=True, allTerrainIndicesUnchanged=True,
        allOtherTerrainVerticesUnchanged=True, higherManOiSideVerticesUnchanged=True,
        terrainProposalChanged=True, exactSameSurfaceClaim=False, sourceGeometryChanges=0,
        physicalAccepted=False, rootCredit=False, installationApproved=False,
        qualification='Set five measured near-footing terrain vertices to the common exact original post bottom. Preserve the two higher vertices toward Man Oi. Complete original and actual rendered finite clearance, strict footing roots, foundation, all current basic/native neighbours and runtime remain mandatory.')
    out['nativeMesh']['source']['manFukOriginalPostTerrainFootings'] = proof
    return out, proof
