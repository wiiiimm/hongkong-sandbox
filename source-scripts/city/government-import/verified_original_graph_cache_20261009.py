"""Source-only exact graph reuse; all current physical/foreign gates are separate.

An immutable complete Neon receipt is mandatory. Exact input equality permits
reuse of the bulk candidate-pair scan; every credited path contact is still
recomputed from the current original triangles. No cached acceptance is returned.
"""
import copy
import hashlib
import json
from pathlib import Path
import numpy as np
from exact_original_shell_intersections_20261009 import intersection_points, rational_face
from unchanged_closed_column_role_v2_20261009 import canonical_sha

KERNEL = Path(__file__).with_name('exact_original_wall_contact_paths_20261009.py')
SOURCE_KEYS = ('sourceSHA256', 'positionTriangleStreamSHA256',
               'normalTriangleStreamSHA256', 'colourTriangleStreamSHA256',
               'rootMatrix', 'decodedWorldTrianglesSHA256', 'drawnGroundSHA256',
               'continuousFaceContextsSHA256')


def source_key(triangles, contexts, affected_faces, binding):
    tri = np.asarray(triangles, float)
    assert tri.ndim == 3 and tri.shape[1:] == (3, 3) and np.isfinite(tri).all()
    assert binding['decodedWorldTrianglesSHA256'] == hashlib.sha256(tri.tobytes()).hexdigest()
    assert binding['continuousFaceContextsSHA256'] == canonical_sha(contexts)
    assert len(contexts) == len(tri) and [c['sourceFace'] for c in contexts] == list(range(len(tri)))
    assert all(c['groundProjectionCovered'] and c['minimum'] for c in contexts)
    faces = list(affected_faces)
    assert faces and faces == sorted(set(faces)) and all(type(i) is int and 0 <= i < len(tri) for i in faces)
    assert faces == [i for i, c in enumerate(contexts) if c['minimum']['minimumGapM'] < -.5]
    source = {k: binding[k] for k in SOURCE_KEYS}
    assert all(source[k] is not None for k in SOURCE_KEYS)
    return {'completeSourceBinding': source, 'affectedOriginalFaces': faces,
            'completeOriginalFaceCount': len(tri),
            'exactGraphKernelSHA256': hashlib.sha256(KERNEL.read_bytes()).hexdigest()}


def envelope(triangles, contexts, affected_faces, binding, computed_graph):
    """Called only after the immutable complete graph kernel has actually run."""
    key = source_key(triangles, contexts, affected_faces, binding)
    assert computed_graph['sourceBinding'] == binding
    return {'schema': 'immutable-source-only-original-contact-graph-v1',
            'sourceOnlyKey': key, 'sourceOnlyKeySHA256': canonical_sha(key),
            'computedOriginalGraph': computed_graph,
            'sourceGeometryChanges': 0, 'installationApproved': False}


def replay(triangles, contexts, affected_faces, binding, cached, *,
           immutable_complete_result, expected_result, artifact_sha256):
    """Pure replay after the caller has read the exact complete job from Neon.

    The public file loader below provides that read; a caller's diagnosis or
    boolean is insufficient. Current actor fields are intentionally not reused.
    """
    assert immutable_complete_result == ('complete', expected_result), 'Missing or changed complete Neon receipt'
    assert expected_result['stage'] == 'immutable-original-contact-graph-cache-v1'
    assert expected_result['graphArtifact']['sha256'] == artifact_sha256
    assert expected_result['sourceGeometryChanges'] == 0 and expected_result['installationApproved'] is False
    key = source_key(triangles, contexts, affected_faces, binding)
    assert cached['schema'] == 'immutable-source-only-original-contact-graph-v1'
    assert cached['sourceOnlyKey'] == key
    assert cached['sourceOnlyKeySHA256'] == expected_result['sourceOnlyKeySHA256'] == canonical_sha(key)
    graph = copy.deepcopy(cached['computedOriginalGraph'])
    assert {k: graph['sourceBinding'][k] for k in SOURCE_KEYS} == key['completeSourceBinding']
    tri = np.asarray(triangles, float)
    normal = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    length = np.linalg.norm(normal, axis=1)
    ratio = np.divide(normal[:, 1], length, out=np.zeros(len(tri)), where=length > 0)
    walls = set(np.flatnonzero((length > 0) & (np.abs(ratio) <= .25)).tolist())
    roofs = {i for i, c in enumerate(contexts) if length[i] > 0 and ratio[i] > .25 and c['minimum']['minimumGapM'] >= -.5}
    assert graph['completeOriginalFaceInventory'] == list(range(len(tri)))
    assert graph['collapsedOriginalFacesExcludedFromPaths'] == np.flatnonzero(length == 0).tolist()
    assert graph['eligibleWallFaces'] == sorted(walls) and graph['clearOriginalRoofFaces'] == sorted(roofs)
    assert [p['sourceFace'] for p in graph['paths']] == list(affected_faces)
    checked = []
    for item in graph['paths']:
        path = item['originalWallContactRoofPath']
        assert path and path[0] == item['sourceFace'] and len(path) == len(set(path))
        assert all(type(i) is int and 0 <= i < len(tri) for i in path)
        assert all(i in walls for i in path[:-1]) and path[-1] in (walls | roofs)
        assert item['hasExactPositiveDimensionPathToClearRoof'] == (path[-1] in roofs)
        for i, j in zip(path, path[1:]):
            points = intersection_points(rational_face(tri[i]), rational_face(tri[j]))
            assert len(points) > 1, 'Cached path has a vertex-only, detached or stale original contact'
            checked.append([i, j])
    assert graph['allAffectedHaveExactContactRoofPaths'] == all(p['hasExactPositiveDimensionPathToClearRoof'] for p in graph['paths'])
    graph['sourceBinding'] = copy.deepcopy(binding)
    graph['verifiedSourceOnlyCacheReplay'] = {
        'jobId': expected_result['jobId'], 'sourceOnlyKeySHA256': canonical_sha(key),
        'bulkEligiblePairScanReused': True, 'creditedOriginalPathContactsRecomputed': checked,
        'currentForeignScopeReused': False, 'currentPhysicalAcceptanceReused': False,
        'installationApproved': False}
    return graph


def load_and_replay(triangles, contexts, affected_faces, binding, result_path):
    """Readonly production entry: fetch and compare the real fenced Neon job."""
    from run import ROOT, read, digest, connect
    result = read(result_path)
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        actual = con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                             (result['jobId'],)).fetchone()
    ref = result['graphArtifact']; path = ROOT / ref['path']
    raw = path.read_bytes(); assert digest(raw) == ref['sha256']
    # The immutable receipt pins the exact graph kernel and cache implementation.
    for item in result['evidenceRefs']:
        assert digest((ROOT / item['path']).read_bytes()) == item['sha256']
    assert any(r['path'] == str(KERNEL.relative_to(ROOT)) and r['sha256'] == digest(KERNEL.read_bytes()) for r in result['evidenceRefs'])
    assert any(r['path'] == str(Path(__file__).relative_to(ROOT)) and r['sha256'] == digest(Path(__file__).read_bytes()) for r in result['evidenceRefs'])
    return replay(triangles, contexts, affected_faces, binding, read(path),
                  immutable_complete_result=actual, expected_result=result,
                  artifact_sha256=digest(raw))
