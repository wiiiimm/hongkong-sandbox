"""Private contract for the six exact conserved Southside terrain strips.

Legacy pair checks still govern ordinary vertices. The only additional boundary
witnesses are exact, shared-original-face twins from the frozen diagnostic. This
does not approve source identity, physical placement, publication or installation.
"""
import copy
import gzip
import hashlib
import json
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
import sys

import numpy as np

INTEGRATION = Path(__file__).resolve().parents[1] / 'island-detail-integration'
if str(INTEGRATION) not in sys.path:
    sys.path.insert(0, str(INTEGRATION))
import coordinated_native_boundary as legacy
from finite_layered_seam_coverage_v1_20261028 import bidirectional_layer_coverage

POLICY = 'southside-six-conserved-original-strips-v1'
UID = 'landsd/315025:0'


def marker(node):
    return node.get('nativeMesh', {}).get('source', {}).get('coordinatedBoundary')


def reference(ref):
    assert set(ref) == {'path', 'sha256'}
    path = (legacy.ROOT / ref['path']).resolve()
    assert path.is_relative_to(legacy.ROOT.resolve())
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == ref['sha256'], 'Partition evidence changed'
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


@lru_cache(maxsize=1)
def load(path, sha):
    # One cache lives only inside a private diagnostic process. Authenticate all
    # evidence before caching; the owning worker must keep inputs immutable.
    proof = reference(dict(path=path, sha256=sha))
    assert set(proof) == {'policy', 'parent', 'partition', 'twins', 'layers', 'seams', 'members', 'pairs'}
    assert proof['policy'] == POLICY
    part, twins, layers, seams = [reference(proof[k]) for k in ['partition', 'twins', 'layers', 'seams']]
    assert part['uids'] == twins['uids'] == layers['uids'] == seams['uids'] == [UID]
    assert part['allNodeBudgetsPassed'] and not part['missingParentFaces'] and not part['heightDriftViolations']
    assert part['maximumSourcePlaneHeightDriftM'] < .01
    assert part['maximumRuntimeVertexDisplacementM'] < .001
    assert part['maximumParentAreaConservationErrorM2'] < 1e-8
    assert twins['legacyNegativeVertices'] == 22 and twins['allLegacyNegativeVerticesHaveExactOppositeSourceFaceTwins']
    assert layers['allFiveBidirectionalLayerProofsPassed'] and layers['legacyNegativeResultsPreserved']
    assert set(proof['members']) == set(map(str, range(6)))
    assert len(proof['pairs']) == len(seams['pairs']) == len(layers['pairs']) == 5
    parent = reference(proof['parent'])
    nodes, tables = {}, {}
    strips = {str(s['strip']): s for s in part['strips']}
    assert set(strips) == set(proof['members'])
    for name, member in proof['members'].items():
        assert set(member) == {'before', 'candidate', 'canonicalSHA256'}
        assert member['before'] == member['candidate'], 'This contract covers new partitions only'
        node = reference(member['candidate'])
        assert not marker(node) and not node['nativeMesh'].get('sourceOverlap')
        assert legacy.canonical_sha(node) == member['canonicalSHA256']
        assert node['meta']['targetUids'] == [UID]
        assert node['meta']['parentSha256'] == proof['parent']['sha256']
        data = reference(strips[name]['asset'])
        assert node['nativeMesh']['position'] == data['position'] and node['nativeMesh']['index'] == data['index']
        triangles = legacy.triangles(node)
        assert len(triangles) == len(data['parentFaceIndices']) <= 25000
        g = parent['meta']['georef']
        a, b, c, d = node['coarseCells']
        assert all(type(i) is int for i in [a, b, c, d]) and 0 <= a < c < parent['w'] and 0 <= b < d < parent['h']
        assert legacy.bounds(node) == (g['bE'] + a*g['aE'] - 834500, 816500-g['bN']-b*g['aN'],
                                       g['bE'] + c*g['aE'] - 834500, 816500-g['bN']-d*g['aN'])
        table = {}
        for face, original in zip(triangles, data['parentFaceIndices']):
            assert type(original) is int and 0 <= original < part['parentRuntimeFaces']
            for point in face:
                table.setdefault(tuple(point), set()).add(original)
        nodes[name], tables[name] = node, table
    callbacks = {name: [] for name in nodes}
    expected_negatives = []
    for j, pair_ref in enumerate(proof['pairs']):
        names = [str(j), str(j+1)]
        pair = reference(pair_ref)
        assert set(pair['members']) == set(names) and pair['parent'] == proof['parent']
        assert pair['members'] == {name: proof['members'][name] for name in names}
        assert seams['pairs'][j]['pair'] == layers['pairs'][j]['pair'] == names
        left, right = [legacy.bounds(nodes[name]) for name in names]
        assert left[2] == right[0] and left[1] == right[1] and left[3] == right[3]
        import shapely
        edit = shapely.from_wkt(pair['editRegionWKT'])
        lo, hi = edit.bounds[1], edit.bounds[3]
        curves = [legacy.seam_segments(legacy.triangles(nodes[name]), 0, left[2], lo, hi) for name in names]
        assert bidirectional_layer_coverage(*curves)['passed'], 'A finite seam layer is missing'
        for side in seams['pairs'][j]['sides']:
            name = side['member']
            assert name in names and side['finitePairConstructionPassed'] and side['ordinaryBoundaryRemaining'] == 0
            temporary = copy.deepcopy(nodes[name])
            temporary['nativeMesh']['source']['coordinatedBoundary'] = dict(policy=legacy.POLICY, proof=pair_ref, member=name)
            callback = legacy.coordinated_boundary(temporary, parent)
            allowed_twins = set()
            for failure in side['failures']:
                point = tuple(failure['position'])
                mate = next(n for n in names if n != name)
                assert point[0] == left[2] and lo <= point[2] <= hi
                common = tables[name].get(point, set()) & tables[mate].get(point, set())
                assert common, 'No identical opposite-side original-face witness'
                assert failure['reason'] == 'No finite same-triangle boundary-height witness'
                try:
                    callback(*point)
                except AssertionError as exc:
                    assert str(exc) == failure['reason']
                else:
                    raise AssertionError('Legacy negative no longer reproduced')
                expected_negatives.append((tuple(names), name, point, tuple(sorted(common))))
                allowed_twins.add(point)
            callbacks[name].append((callback, frozenset(allowed_twins)))
    actual_negatives = [(tuple(r['pair']), r['own'], tuple(r['position']), tuple(r['sameOriginalMasterFaceIDs'])) for r in twins['rows']]
    assert len(expected_negatives) == len(actual_negatives) == 22
    assert sorted(expected_negatives) == sorted(actual_negatives), 'Twin roster differs from legacy negatives'
    return proof, parent, nodes, callbacks


def checked(node, parent=None):
    own = marker(node)
    assert set(own) == {'policy', 'proof', 'member'} and own['policy'] == POLICY
    proof, root, nodes, callbacks = load(own['proof']['path'], own['proof']['sha256'])
    assert own['member'] in nodes
    assert legacy.canonical_sha(node) == proof['members'][own['member']]['canonicalSHA256'], 'Partition body changed'
    if parent is not None:
        assert parent == root, 'Partition root changed'
    return own, proof, nodes, callbacks


@contextmanager
def private_validator():
    """Compose with the current outer validator; no canonical source edits."""
    old_boundary, old_effective = legacy.coordinated_boundary, legacy.validate_effective_coordinated_members
    load.cache_clear()

    def boundary(node, parent):
        own = marker(node)
        if not own or own.get('policy') != POLICY:
            return old_boundary(node, parent)
        own, _, _, callbacks = checked(node, parent)

        def allows(x, y, z):
            point = (x, y, z)
            for callback, twins in callbacks[own['member']]:
                if point in twins or callback(x, y, z):
                    return True
            return False
        return allows

    def effective(nodes):
        old_effective([n for n in nodes if not marker(n) or marker(n).get('policy') != POLICY])
        for node in nodes:
            own = marker(node)
            if not own or own.get('policy') != POLICY:
                continue
            own, proof, candidates, _ = checked(node)
            for name, candidate in candidates.items():
                matches = [n for n in nodes if n['coarseCells'] == candidate['coarseCells'] and
                           legacy.canonical_sha(n) == proof['members'][name]['canonicalSHA256']]
                assert len(matches) == 1, 'All six exact partition members must appear exactly once'
                assert marker(matches[0]) == dict(policy=POLICY, proof=own['proof'], member=name), 'Partition markers disagree'

    legacy.coordinated_boundary, legacy.validate_effective_coordinated_members = boundary, effective
    try:
        yield
    finally:
        legacy.coordinated_boundary, legacy.validate_effective_coordinated_members = old_boundary, old_effective
        load.cache_clear()
