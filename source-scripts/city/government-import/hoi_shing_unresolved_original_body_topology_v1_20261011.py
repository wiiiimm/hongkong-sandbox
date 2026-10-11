"""Describe all unresolved Hoi Shing source bodies without assigning roles.

Only exact original source coordinates and the completed source-only graph are
used. Boundary topology is a research lead, never a support or visual exemption.
No current geometry, terrain, review state or publication is changed.
"""
from collections import defaultdict
import importlib.util
import json
from pathlib import Path

import numpy as np

from run import ROOT, HERE, read, save, digest, connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-hoi-shing-unresolved-original-body-topology-v1-20261011'
DOC = BASE / BATCH
GRAPH = BASE / 'xl-terrain-recovery-20261011-hoi-shing-complete-original-edge-contact-graph-v1'
RIMS = BASE / 'xl-terrain-recovery-20261011-hoi-shing-derived-ground-original-rim-graph-v1'
EXPECTED = {
    'landsd/318801:0': 'fc22e0aa4c2869e520e0336fb3e2ef1d6f1bb246529824af010465bb382e0e55',
    'landsd/318830:0': 'cb52942f086f38d8d95a346e83538003c90f9aaa772811ac13d3485e1ae27b7f',
}


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def main():
    assert not DOC.exists()
    receipts = {}
    references = [ref(Path(__file__)), ref(HERE / 'exact_packed_world_geometry_20261009.py')]
    for folder in [GRAPH, RIMS]:
        receipt = read(folder / 'result.json')
        with connect() as connection:
            connection.execute('SET TRANSACTION READ ONLY')
            assert connection.execute(
                'SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                (receipt['jobId'],),
            ).fetchone() == ('complete', receipt)
        assert ref(folder / 'diagnostic.json.gz') in receipt['evidenceRefs']
        references.extend([ref(folder / 'result.json'), ref(folder / 'diagnostic.json.gz')])
        receipts[folder.name] = receipt

    graph = read(GRAPH / 'diagnostic.json.gz')
    rims = read(RIMS / 'diagnostic.json.gz')
    assert graph['uids'] == rims['uids'] == list(EXPECTED)
    assert rims['sourceOnly'] and not rims['currentAcceptance']
    worlds = []
    for uid, sha in EXPECTED.items():
        paths = [r for r in graph['evidenceRefs'] if r['sha256'] == sha and r['path'].endswith('.glb.gz')]
        assert len(paths) == 1
        path = ROOT / paths[0]['path']
        assert ref(path) == paths[0]
        worlds.append(decode_original_world_triangles(path.read_bytes()))
        references.append(ref(path))
    world = np.concatenate(worlds)
    assert world.shape == (19374, 3, 3) and np.isfinite(world).all()
    assert digest(world.tobytes()) == graph['binding']['completeOriginalWorldSHA256'] == rims['completeOriginalWorldSHA256']
    components = graph['components']
    unresolved = rims['unresolvedSourceBodies']
    assert len(components) == 145 and len(unresolved) == 18
    rows = []
    for body_id in unresolved:
        body = components[body_id]
        ids = body['globalOriginalFaces']
        triangles = world[ids]
        edges = defaultdict(list)
        for source_id, triangle in zip(ids, triangles):
            for a, b in zip(triangle, np.roll(triangle, -1, axis=0)):
                aa, bb = tuple(map(float, a)), tuple(map(float, b))
                edges[tuple(sorted((aa, bb)))].append({'face': source_id, 'directedVertices': [aa, bb]})
        boundary = [{'vertices': list(edge), 'occurrences': occurrences}
                    for edge, occurrences in sorted(edges.items()) if len(occurrences) == 1]
        normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
        assert np.all(np.any(normals != 0, axis=1))
        bounds = [triangles.min((0, 1)).tolist(), triangles.max((0, 1)).tolist()]
        assert bounds == body['bounds']
        rows.append({
            'originalBody': body_id,
            'actorUID': body['actorUID'],
            'completeGlobalOriginalFaces': ids,
            'completeBodyWorldSHA256': digest(triangles.tobytes()),
            'completeBounds': bounds,
            'dimensionsM': (np.asarray(bounds[1]) - bounds[0]).tolist(),
            'completeBoundaryEdges': boundary,
            'nonmanifoldEdges': [{'vertices': list(edge), 'occurrences': occurrences}
                                 for edge, occurrences in sorted(edges.items()) if len(occurrences) > 2],
            'exactHorizontalFaces': [i for i, n in zip(ids, normals) if n[0] == 0 and n[2] == 0],
            'exactVerticalFaces': [i for i, n in zip(ids, normals) if n[1] == 0],
            'completeOriginalRimDiagnostic': rims['allOriginalOrdinaryRimSamples'][body_id],
            'roleAssigned': False,
            'rootOrBridgeCredit': False,
        })
    assert sum(len(r['completeGlobalOriginalFaces']) for r in rows) == rims['unresolvedSourceBodyFaces'] == 1031
    for reference in references:
        assert ref(ROOT / reference['path']) == reference
    result = {
        'uids': list(EXPECTED),
        'completeOriginalWorldSHA256': digest(world.tobytes()),
        'completeOriginalFaces': 19374,
        'unresolvedBodies': unresolved,
        'unresolvedFaces': 1031,
        'rows': rows,
        'sourceOnly': True,
        'historicalDerivedTerrainNotCurrentGround': True,
        'roleAssigned': False,
        'rootOrBridgeCredit': False,
        'currentAcceptance': False,
        'newlyInstalled': 0,
        'sourceGeometryChanges': 0,
        'evidenceRefs': references,
        'qualification': 'Complete exact original boundary topology describes research leads only. No open boundary or face orientation proves architectural function, visible mounting, grade contact, support, exposure or acceptance. Historical derived-ground failures and all current identity/foreign/native/runtime obligations remain.',
    }
    save(DOC / 'diagnostic.json.gz', result)
    freezer_path = HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py'
    spec = importlib.util.spec_from_file_location('hoi_topology_freezer', freezer_path)
    freezer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(freezer)
    freezer.freeze(BATCH, 'complete-unresolved-original-body-topology-source-only-v1',
                   [ROOT / r['path'] for r in references] + [DOC / 'diagnostic.json.gz', freezer_path],
                   {'uids': list(EXPECTED), 'unresolvedBodies': unresolved, 'unresolvedFaces': 1031,
                    'currentAcceptance': False, 'newlyInstalled': 0, 'sourceGeometryChanges': 0})
    print(json.dumps([{'body': r['originalBody'], 'uid': r['actorUID'],
                       'faces': len(r['completeGlobalOriginalFaces']),
                       'boundaryEdges': len(r['completeBoundaryEdges']),
                       'dimensionsM': r['dimensionsM']} for r in rows]))


if __name__ == '__main__':
    main()
