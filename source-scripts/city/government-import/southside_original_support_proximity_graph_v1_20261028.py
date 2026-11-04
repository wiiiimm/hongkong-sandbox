"""Optimistic finite-original proximity paths for the four Southland source units.

One metre is an intentionally generous diagnostic radius, NOT new support credit.
Whole units and the whole podium are over-connected by this graph. No path even
under these assumptions is useful negative evidence; a path is not acceptance.
"""
import argparse
from collections import deque
from fractions import Fraction
import subprocess
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_distance_20261009 import triangle_distance

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-southside-original-support-proximity-graph-v1-20261028'
DOC, LOCAL = BASE/BATCH, HERE/'local'/BATCH
LEASE = LOCAL/'reservation.json'
CAP = BASE/'government-xl-southside-project-original-recovery-v1-20261028'
EXTRA = BASE/'government-xl-southside-additional-original-support-lookup-v1-20261028'
INFRA = BASE/'government-xl-southside-original-infrastructure-recovery-v1-20261028'
SURFACE = BASE/'government-xl-southside-source-bound-surface-contract-v1-20261028'
TARGETS = ['landsd/311759:0', 'landsd/311763:0', 'landsd/330243:0', 'landsd/330244:0']
RADIUS = 1.0


def owned():
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists()
    refs, pins = [Path(__file__), HERE/'exact_packed_world_geometry_20261009.py',
                  HERE/'exact_original_triangle_distance_20261009.py',
                  HERE/'exact_original_shell_intersections_20261009.py'], {}
    for batch in [CAP, EXTRA, INFRA, SURFACE]:
        _, bound = authenticate(batch)
        refs.append(batch/'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(CAP/'selection.json.gz')
    assert {'building:' + r['uid'] for r in selection['rows']} <= set(lease['resources'])
    units, geometry = {}, {}
    for row in selection['rows']:
        path = ROOT/row['candidate']['path']
        assert digest(path.read_bytes()) == row['sourceSHA256']
        refs.append(path)
        tri = decode_original_world_triangles(path.read_bytes())
        assert len(tri) == row['triangles']
        uid = row['uid']; geometry[uid] = tri
        units[uid] = dict(kind='original-building', sourceSHA256=row['sourceSHA256'],
                          sourceKey=row['native']['cacheKey'] + '/' + row['modelId'],
                          worldBounds=[tri.min((0, 1)).tolist(), tri.max((0, 1)).tolist()], unknownGeometry=False)
    extra = take(EXTRA/'lookup.json')
    assert extra['unknownBoundsRetained'] == 0
    for row in extra['additionalOriginalUnits']:
        key = 'unrecovered:' + row['sourceKey']
        units[key] = dict(kind='additional-original-building', sourceKey=row['sourceKey'],
                          worldBounds=row['model']['worldBounds'], unknownGeometry=True)
    infrastructure = take(INFRA/'summary.json')
    assert infrastructure['recoveredUnits'] == infrastructure['packedUnits'] == 15 and not infrastructure['errors']
    for row in infrastructure['originalUnits']:
        key = row['sourceUnitKey']
        units[key] = dict(kind='original-infrastructure', sourceKey=key, worldBounds=row['worldBounds'],
                          asset=row['packedOriginal'], expectedWorldSHA256=row['originalWorldSHA256'], unknownGeometry=False)
    surface = take(SURFACE/'summary.json')
    assert surface['singleNodeSurfaceContractPassed']
    terrainpath = ROOT/surface['candidate']['path']
    node = take(terrainpath)
    mesh = node['nativeMesh']
    terrain = np.asarray(mesh['position'], dtype='<f4').astype('<f8').reshape(-1, 3)[np.asarray(mesh['index']).reshape(-1, 3)]
    geometry['terrain-root'] = terrain
    units['terrain-root'] = dict(kind='private-ground-diagnostic-root', sourceSHA256=digest(terrainpath.read_bytes()),
                                 worldBounds=[terrain.min((0, 1)).tolist(), terrain.max((0, 1)).tolist()], unknownGeometry=False)
    roots = {'landsd/315025:0', 'terrain-root'}
    tests = subprocess.run([sys.executable, str(HERE/'test_exact_original_triangle_distance_20261009.py')],
                           cwd=ROOT, capture_output=True, text=True)
    save(DOC/'tests.json', dict(exitCode=tests.returncode, stdout=tests.stdout, stderr=tests.stderr))
    assert tests.returncode == 0
    refs.append(HERE/'test_exact_original_triangle_distance_20261009.py')
    graph = {key: set() for key in units}; pairs = []; checked = set(); queue = deque(TARGETS); expanded = set()

    def load(key):
        if key not in geometry:
            record = units[key]; path = ROOT/record['asset']['path']
            assert digest(path.read_bytes()) == record['asset']['sha256']
            refs.append(path)
            tri = decode_original_world_triangles(path.read_bytes())
            assert digest(tri.astype('<f8').tobytes()) == record['expectedWorldSHA256']
            geometry[key] = tri
        return geometry[key]

    while queue:
        own = queue.popleft()
        if own in expanded or own in roots or units[own]['unknownGeometry']:
            continue
        expanded.add(own)
        for peer in units:
            if own == peer or frozenset([own, peer]) in checked:
                continue
            checked.add(frozenset([own, peer]))
            low, high = np.asarray(units[own]['worldBounds'])
            other_low, other_high = np.asarray(units[peer]['worldBounds'])
            if np.any(other_low > high+RADIUS) or np.any(other_high < low-RADIUS):
                pairs.append(dict(pair=[own, peer], entireUnitsAxisSeparatedBeyondRadius=True, proximityEdge=False))
                continue
            if units[peer]['unknownGeometry']:
                graph[own].add(peer); graph[peer].add(own)
                pairs.append(dict(pair=[own, peer], unknownPeerRetainedAsPossibleEdge=True, proximityEdge=True))
                continue
            a, b = load(own), load(peer)
            # The radius expansion must be exact for the dyadic coordinates;
            # no rounded broad-phase rejection may supply negative evidence.
            for values in [a.min((0, 1)), a.max((0, 1))]:
                assert all(Fraction(float(v+1))-Fraction(float(v)) == 1 and Fraction(float(v))-Fraction(float(v-1)) == 1 for v in values)
            lo, hi = b.min(1), b.max(1)
            witness, tested = None, 0
            for i, face in enumerate(a):
                candidates = np.flatnonzero(np.all(hi >= face.min(0)-RADIUS, axis=1) & np.all(lo <= face.max(0)+RADIUS, axis=1))
                for j in candidates:
                    tested += 1
                    assert tested <= 1000000, 'Pair compute bound reached; retain investigation, no negative result'
                    proof = triangle_distance(face, b[j])
                    if Fraction(proof['exactSquaredDistanceM2']) <= 1:
                        witness = dict(sourceFaceA=int(i), sourceFaceB=int(j), exactDistanceProof=proof)
                        break
                if witness:
                    break
                if i % 2000 == 0:
                    save(DOC/'progress.json', dict(pair=[own, peer], completedSourceFaces=i, exactCandidatePairs=tested, installationApproved=False))
                assert reservations.owns(lease)
            found = witness is not None
            pairs.append(dict(pair=[own, peer], completeFaces=[len(a), len(b)], exactCandidatePairs=tested,
                              allOriginalPrimitivesIncluded=True, completeNegativeScan=not found,
                              proximityEdge=found, firstSufficientWitness=witness))
            if found:
                graph[own].add(peer); graph[peer].add(own)
                if peer not in expanded and peer not in roots:
                    queue.append(peer)
            print(dict(pair=[own, peer], proximityEdge=found, exactCandidatePairs=tested), flush=True)
    summaries = []
    for target in TARGETS:
        visited = {target}; pending = [target]
        while pending:
            current = pending.pop()
            for peer in graph[current] - visited:
                visited.add(peer); pending.append(peer)
        summaries.append(dict(uid=target, optimisticPathToAssumedRoot=bool(visited & roots),
                              reachedRootUnits=sorted(visited & roots),
                              reachableUnknownSourceUnits=sorted(u for u in visited if units[u]['unknownGeometry']),
                              reachableUnits=sorted(visited)))
    result = dict(uids=TARGETS, diagnosticRadiusM=RADIUS, assumedRootUnits=sorted(roots), units=units,
                  sourceUnitPairs=pairs, targets=summaries, sourceGeometryChanges=0,
                  identityAccepted=False, physicalAccepted=False, installationApproved=False,
                  qualification='Optimistic whole-unit proximity graph, not a support contract. Any finite original primitive within1m creates a possible edge; whole podium assumed rooted; all39 building/infrastructure source units or conservative unknown bounds plus current private ground considered. Positive witnesses stop only their pair scan; negative pairs include every original primitive and exact radius broad-phase checks. Unknown possible peers block a completeness conclusion. A root path does not prove structural support; no root path is scoped negative evidence only, not permanent rejection or permission to edit geometry.')
    save(DOC/'summary.json', result)
    assert reservations.owns(lease)
    module('southside_original_support_proximity_graph_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'optimistic-original-source-proximity-root-path-investigation', list(dict.fromkeys(refs)), result)
    print(summaries, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    if args.owned:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    authenticate(CAP); authenticate(INFRA)
    rows = read(CAP/'selection.json.gz')['rows']
    resources = {'building:' + r['uid'] for r in rows}
    resources.update('source-infrastructure:' + r['sheet'] for r in read(INFRA/'summary.json')['originalUnits'])
    resources.add('terrain:city/data/terrain.json')
    claim = reservations.claim('southside-original-support-proximity-' + str(uuid.uuid4()), sorted(resources), batch=BATCH, ttl=3600)
    assert claim['ok']
    execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])


if __name__ == '__main__':
    main()
