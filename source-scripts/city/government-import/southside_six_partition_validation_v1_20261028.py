"""Exercise exact six-strip private boundary contract, retaining all other gates."""
import argparse
import copy
import sys
import uuid
from pathlib import Path

from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
import southside_partition_boundary_v1_20261028 as boundary

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-southside-six-partition-validation-v1-20261028'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
LEASE = LOCAL / 'reservation.json'
PREFIX = 'government-xl-southside-'
UID = boundary.UID


def ref(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))


def owned():
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists()
    refs = [Path(__file__), Path(boundary.__file__), HERE / 'finite_layered_seam_coverage_v1_20261028.py',
            HERE / 'coordinated_native_boundary_v1_20261023.py', HERE / 'finite_native_boundary_strip_v1_20261023.py',
            Path(boundary.legacy.__file__)]
    pins = {}
    batches = dict(partition=PREFIX+'six-strip-partition-diagnostic-v1-20261028',
                   twins=PREFIX+'partition-boundary-twins-v1-20261028',
                   layers=PREFIX+'all-layer-seam-proof-v1-20261028',
                   seams=PREFIX+'partition-existing-seams-v1-20261028',
                   children=PREFIX+'partition-node-contracts-v1-20261028')
    for batch in batches.values():
        _, bound = authenticate(BASE / batch)
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha
        refs.append(BASE / batch / 'result.json')

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    children = take(BASE / batches['children'] / 'summary.json')
    assert children['allSixCoverageAndBudgetChecksPassed']
    rootpath = ROOT / '3d-viewer/city/data/terrain.json'
    parent = read(rootpath)
    refs.append(rootpath)
    pairs, members = [], {}
    for j in range(5):
        path = BASE / batches['seams'] / ('pair-' + str(j) + '.json')
        pair = take(path)
        assert pair['parent'] == ref(rootpath)
        pairs.append(ref(path))
        for name, member in pair['members'].items():
            assert name not in members or members[name] == member
            members[name] = member
            take(ROOT / member['candidate']['path'])
    proof = dict(policy=boundary.POLICY, parent=ref(rootpath), members=members, pairs=pairs)
    for key in ['partition', 'twins', 'layers', 'seams']:
        path = BASE / batches[key] / 'summary.json'
        take(path)
        proof[key] = ref(path)
    proofpath = DOC / 'exact-six-member-boundary-proof.json'
    save(proofpath, proof)
    producer = module('southside_six_partition_overlap', HERE / 'sham_shui_po_pool_shared_terrain_v2_20261016.py')
    validator = module('southside_six_partition_native_validator', HERE.parent / 'island-detail-integration/native_terrain_validation.py')
    refs.extend([Path(producer.__file__), Path(validator.__file__)])
    nodes = []
    for name, member in sorted(members.items()):
        node = take(ROOT / member['candidate']['path'])
        node['nativeMesh']['source']['coordinatedBoundary'] = dict(policy=boundary.POLICY, proof=ref(proofpath), member=name)
        sources = [Path(__file__), Path(boundary.__file__), proofpath, rootpath, ROOT / member['candidate']['path']]
        for source in node['meta']['source']['nativeSources']:
            path = ROOT / source['path']
            assert digest(path.read_bytes()) == source['sha256']
            sources.append(path)
            if path.suffix == '.gltf':
                sources.extend(p for p in path.parent.iterdir() if p.suffix == '.bin')
        refs.extend(sources)
        producer.DOC = DOC / ('strip-' + name)
        producer.overlap_proof(node, list(dict.fromkeys(sources)))
        nodes.append(node)
    results, tests = [], []
    with boundary.private_validator():
        for node in nodes:
            assert reservations.owns(lease)
            try:
                validator.validate_native_mesh(node, parent)
                passed, error = True, None
            except AssertionError as exc:
                passed, error = False, str(exc)
            result = dict(member=boundary.marker(node)['member'], fullPrivateNativeValidatorPassed=passed, failure=error)
            results.append(result)
            print(result, flush=True)
            save(DOC / 'progress.json', dict(members=results, installationApproved=False))
        boundary.legacy.validate_effective_coordinated_members(nodes)
        tests.append('all-six-exact-members-present')

        def rejects(name, operation):
            try:
                operation()
            except AssertionError:
                tests.append(name)
            else:
                raise AssertionError('Adversarial check unexpectedly accepted: ' + name)

        rejects('missing-sixth-member', lambda: boundary.legacy.validate_effective_coordinated_members(nodes[:-1]))
        rejects('duplicate-member', lambda: boundary.legacy.validate_effective_coordinated_members(nodes + [nodes[0]]))
        changed = copy.deepcopy(nodes[0])
        changed['nativeMesh']['position'][1] += .1
        rejects('changed-geometry', lambda: boundary.legacy.coordinated_boundary(changed, parent))
        changed = copy.deepcopy(nodes[0])
        changed['meta']['targetUids'].append('landsd/1:0')
        rejects('changed-target-roster', lambda: boundary.legacy.coordinated_boundary(changed, parent))
        changed = copy.deepcopy(nodes[-1])
        boundary.marker(changed)['member'] = '0'
        rejects('wrong-member-marker', lambda: boundary.legacy.validate_effective_coordinated_members(nodes[:-1] + [changed]))
        changed_parent = copy.deepcopy(parent)
        changed_parent['elev'][0] += .1
        rejects('changed-root', lambda: boundary.legacy.coordinated_boundary(nodes[0], changed_parent))
        callback = boundary.legacy.coordinated_boundary(nodes[0], parent)
        x0, z0, _, _ = boundary.legacy.bounds(nodes[0])
        assert not callback(x0, 9999, z0), 'External root edge cannot use partition credit'
        tests.append('external-edge-retains-root-rule')
    result = dict(uids=[UID], members=results, adversarialChecksPassed=tests,
                  allSixPrivateNativeValidatorsPassed=all(r['fullPrivateNativeValidatorPassed'] for r in results),
                  allSixEffectiveMembersRequired=True, productionGuardChanges=False,
                  sourceGeometryChanges=0, identityAccepted=False, physicalAccepted=False,
                  installationApproved=False, fullCurrentMapAcceptance=False,
                  qualification='Private six-strip boundary contract only. Original full validator used with exact conserved partition witnesses and fresh child overlap proofs. External root rules unchanged; legacy negative results remain preserved. Current map regressions, original-model identity/physical checks and desktop/mobile acceptance still required.')
    save(DOC / 'summary.json', result)
    assert reservations.owns(lease)
    module('southside_six_partition_validation_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'private-six-conserved-original-strips-full-native-validation', list(dict.fromkeys(refs)), result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    if args.owned:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    claim = reservations.claim('southside-six-partition-validation-' + str(uuid.uuid4()), ['building:' + UID], batch=BATCH, ttl=3600)
    assert claim['ok']
    execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])


if __name__ == '__main__':
    main()
