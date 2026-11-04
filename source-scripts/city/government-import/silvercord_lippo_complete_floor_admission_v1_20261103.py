"""Private full-hierarchy validation of the exact completed source-floor return.

No publication registration, geometry modification or source acceptance.
"""
import copy
import sys
import uuid
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
import nested_coordinated_native_boundary_v1_20261027 as nested
import nested_terrain_patch_validation_v1_20261027 as validator
from fuying_five_member_terrain_stage_v1_20261029 import complete_boundary_validators
from fuying_whole_parent_five_boundary_v1_20261029 import finite_callback
from one_peking_nested_cycle_boundary_v3_20261101 import declare_roundoff

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-lippo-complete-floor-admission-v1-20261103'
CANDIDATE = 'government-xl-silvercord-lippo-complete-floor-candidate-v4-20261103'
GRAPH = 'government-xl-silvercord-lippo-graph-surface-diagnostic-v4-20261103'
LOCAL = HERE / 'local' / BATCH
POLICY = 'private-silvercord-lippo-exact-sixteen-member-floor-return-v1'
UIDS = ['landsd/233997:0', 'landsd/231645:0']


def marker(node):
    return node.get('nativeMesh', {}).get('source', {}).get('coordinatedBoundary')


def walk(nodes):
    for node in nodes:
        yield node
        yield from walk(node.get('patches', []))


def verify_exact_members(nodes, expected, proof_ref):
    """Every declared member must occur exactly once with its entire exact body."""
    found = []
    for node in walk(nodes):
        own = marker(node)
        if not own or own.get('policy') != POLICY:
            continue
        assert set(own) == {'policy', 'proof', 'member'} and own['proof'] == proof_ref
        name = own['member']
        assert name in expected, 'Unknown floor-return member'
        body = copy.deepcopy(node)
        body['nativeMesh']['source'].pop('coordinatedBoundary')
        assert body == expected[name], 'Floor-return member body changed'
        found.append(name)
    assert Counter(found) == Counter({name: 1 for name in expected}), 'Every exact member must be effective once'
    return len(found)


@contextmanager
def private_nested_contract(nodes, successor, root, proof_ref, edges):
    old_boundary = nested.coordinated_boundary
    old_effective = validator.validate_effective_coordinated_members
    callbacks = {name: [] for name in nodes}
    for a, b in edges:
        pair = {a: nodes[a], b: nodes[b]}
        callbacks[a].append(finite_callback(pair, a))
        callbacks[b].append(finite_callback(pair, b))
    assert all(callbacks.values())

    def dispatch(actual, parent):
        own = marker(actual)
        if not own or own.get('policy') != POLICY:
            return old_boundary(actual, parent)
        assert set(own) == {'policy', 'proof', 'member'} and own['proof'] == proof_ref
        name = own['member']
        assert name in nodes
        body = copy.deepcopy(actual)
        body['nativeMesh']['source'].pop('coordinatedBoundary')
        assert body == nodes[name]
        assert parent == (root if name == 'north' else successor), 'Different actual containing parent'
        return lambda x, y, z: any(check(x, y, z) for check in callbacks[name])

    def effective(children):
        ours = [n for n in children if marker(n) and marker(n).get('policy') == POLICY]
        ordinary = [n for n in children if not marker(n) or marker(n).get('policy') != POLICY]
        old_effective(ordinary)  # Preserve the original unknown-policy rejection.
        if ours:
            verify_exact_members(ours, {n: p for n, p in nodes.items() if n != 'north'}, proof_ref)

    nested.coordinated_boundary = dispatch
    validator.validate_effective_coordinated_members = effective
    try:
        yield
    finally:
        nested.coordinated_boundary = old_boundary
        validator.validate_effective_coordinated_members = old_effective


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease)
    assert not (BASE / BATCH).exists()
    proposal, _ = authenticate(BASE / CANDIDATE)
    graph, _ = authenticate(BASE / GRAPH)
    assert proposal['jobId'] == '458a0da1a2cf054ec39c382e4658ecf24819c743763e908b44848073255f5685'
    assert graph['jobId'] == '31d5d477784b974d92fa6c8128de9f74079a1bd774232eb2f88a9e1e5fefdfce'
    assert graph['allFiniteSeamsPassed'] and graph['allMemberSurfaceChecksPassed'] and graph['connectedMemberCount'] == 16
    assert graph['candidate'] == proposal['candidate']
    refs = [Path(__file__), BASE / CANDIDATE / 'result.json', BASE / GRAPH / 'result.json']

    def bound(ref):
        path = ROOT / ref['path']
        assert digest(path.read_bytes()) == ref['sha256']
        refs.append(path)
        return read(path)

    source = bound(proposal['candidate'])
    north = bound(proposal['additionalTopLevelPatch'])
    parent_path = ROOT / '3d-viewer' / proposal['replacedParent']['url']
    assert digest(parent_path.read_bytes()) == proposal['replacedParent']['sha256']
    prior = read(parent_path)
    root_path = ROOT / '3d-viewer/city/data/terrain.json'
    assert digest(root_path.read_bytes()) == proposal['additionalTopLevelPatch']['parentSHA256']
    root = read(root_path)
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_sha = digest(manifest_path.read_bytes())
    assert manifest_sha == proposal['currentManifestSHA256']
    manifest = read(manifest_path)
    refs += [parent_path, root_path, manifest_path]
    assert len(prior['patches']) == 18 and len(source['patches']) == 30
    for field in ['w', 'h', 'cell', 'elev', 'renderedElev', 'vegetation', 'coarseCells']:
        assert source[field] == prior[field], 'Retained full parent grid changed'
    ids = [12, 15, 17] + list(range(18, 30))
    nodes = {str(i): copy.deepcopy(source['patches'][i]) for i in ids}
    nodes['north'] = north
    assert len(nodes) == 16
    out = BASE / BATCH
    members = {}
    for name, node in nodes.items():
        before = copy.deepcopy(node['nativeMesh'])
        node['nativeMesh']['source'].pop('coordinatedBoundary', None)
        node['nativeMesh']['source'].pop('numericalCoverageGap', None)
        declare_roundoff(node)
        assert node['nativeMesh']['position'] == before['position'] and node['nativeMesh']['index'] == before['index']
        path = out / ('member-' + name + '-unmarked.json')
        save(path, node)
        members[name] = dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))
        refs.append(path)
    proof = dict(policy=POLICY, immutableCandidate=proposal['candidate'], priorParent=dict(path=str(parent_path.relative_to(ROOT)), sha256=proposal['replacedParent']['sha256']),
                 root=dict(path=str(root_path.relative_to(ROOT)), sha256=digest(root_path.read_bytes())), candidateJobId=proposal['jobId'], graphJobId=graph['jobId'], members=members,
                 qualification='Private exact candidate bindings; no source or publication approval.')
    proof_path = out / 'private-graph-proof.json'
    save(proof_path, proof)
    proof_ref = dict(path=str(proof_path.relative_to(ROOT)), sha256=digest(proof_path.read_bytes()))
    refs.append(proof_path)
    successor = copy.deepcopy(source)
    marked = {}
    for name, node in nodes.items():
        node = copy.deepcopy(node)
        node['nativeMesh']['source']['coordinatedBoundary'] = dict(policy=POLICY, proof=proof_ref, member=name)
        marked[name] = node
        if name != 'north':
            successor['patches'][int(name)] = node
    for i in range(30):
        if i not in ids:
            assert successor['patches'][i] == source['patches'][i]
    effective = list(root.get('patches', []))
    replaced = 0
    for record in manifest.get('terrainPatches', []):
        path = ROOT / '3d-viewer' / record['url']
        refs.append(path)
        if record['url'] == proposal['replacedParent']['url']:
            assert read(path) == prior
            effective.append(successor)
            replaced += 1
        else:
            effective.append(read(path))
    assert replaced == 1
    validator.check_patch_overlap(marked['north'], effective)
    effective.append(marked['north'])
    verify_exact_members(effective, nodes, proof_ref)
    edges = [tuple(r['members']) for r in graph['edges']]
    assert len(edges) == 22
    refs.extend(HERE / n for n in ['nested_terrain_patch_validation_v1_20261027.py', 'nested_native_terrain_validation_v1_20261027.py', 'nested_coordinated_native_boundary_v1_20261027.py', 'fuying_five_member_terrain_stage_v1_20261029.py', 'fuying_whole_parent_five_boundary_v1_20261029.py', 'one_peking_nested_cycle_boundary_v3_20261101.py'])
    input_pins = {path: digest(path.read_bytes()) for path in refs}
    status, failure = 'private-complete-terrain-validator-passed', None
    try:
        # One existing whole-scene policy context; only the exact new private
        # hierarchy uses the nested contract. Other policies retain their guards.
        with complete_boundary_validators():
            with private_nested_contract(nodes, successor, root, proof_ref, edges):
                validator.validate_grid(root)
                validator.validate_patch(successor, root)
                validator.validate_patch(marked['north'], root)
                from coordinated_native_boundary import validate_effective_coordinated_members
                validate_effective_coordinated_members([n for n in effective if marker(n) is None or marker(n).get('policy') != POLICY])
                verify_exact_members(effective, nodes, proof_ref)
    except AssertionError as error:
        status, failure = 'private-complete-terrain-investigation', str(error)
    save(out / 'unapproved-successor-terrain.json', successor)
    save(out / 'unapproved-north-root-cell.json', marked['north'])
    assert reservations.owns(lease) and digest(manifest_path.read_bytes()) == manifest_sha
    for path, sha in input_pins.items():
        assert digest(path.read_bytes()) == sha, 'Private terrain input changed: ' + str(path.relative_to(ROOT))
    for path in [root_path, parent_path]:
        expected = proposal['additionalTopLevelPatch']['parentSHA256'] if path == root_path else proposal['replacedParent']['sha256']
        assert digest(path.read_bytes()) == expected
    result = dict(uids=UIDS, currentManifestSHA256=manifest_sha, status=status, failure=failure,
                  privateTerrainValidatorPassed=failure is None, exactEffectiveMembers=16, finiteEdges=22,
                  retainedFullParentGridUnchanged=True, originalCandidateRenderedGeometryUnchanged=True, allUnrelatedChildrenUnchanged=True,
                  sourceGeometryChanges=0, sourcePoseChanges=0, sourceRoleAccepted=False, physicalAcceptance=False, installationApproved=False, publication=False,
                  qualification='Private full nested-grid/coverage/overlap/coarse-cell/boundary validation and all existing effective top-level terrain policies. Exactly fifteen nested members plus one actual top-level root cell are present once. No publisher registration or source/terrain approval is inferred; any canonical failure remains an investigation.')
    save(out / 'summary.json', result)
    module('silvercord_lippo_complete_admission_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'private-exact-full-floor-hierarchy-and-all-effective-terrain-policy-validation', list(dict.fromkeys(refs)), result)
    print(result, flush=True)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        proposal = read(BASE / CANDIDATE / 'summary.json')
        retained = read(ROOT / '3d-viewer' / proposal['replacedParent']['url'])['meta']['targetUids']
        keys = {'building:' + u for u in retained + UIDS} | {'terrain:' + proposal['replacedParent']['url'], 'immutable-source-proof:' + BATCH}
        claim = reservations.claim('silvercord-lippo-private-complete-admission-' + str(uuid.uuid4()), sorted(keys), batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
