"""Run canonical terrain staging for the exact parent and north cell, without apply.

This retains the complete existing terrain validators and source-byte bindings.
It is terrain-only evidence: not a production policy registration, model review,
full publisher approval, or permission to publish anything.
"""
import copy
import sys
import uuid
from contextlib import contextmanager
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from silvercord_lippo_complete_floor_admission_v1_20261103 import (
    POLICY, marker, private_nested_contract, verify_exact_members)
from fuying_five_member_terrain_stage_v1_20261029 import complete_boundary_validators
import nested_terrain_patch_validation_v1_20261027 as validator
import coordinated_native_boundary as root_contract

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-lippo-two-descriptor-terrain-dry-run-v1-20261103'
LOCAL = HERE/'local'/BATCH
ADMISSION = 'government-xl-silvercord-lippo-complete-floor-admission-v1-20261103'
GRAPH = 'government-xl-silvercord-lippo-graph-surface-diagnostic-v4-20261103'
CANDIDATE = 'government-xl-silvercord-lippo-complete-floor-candidate-v4-20261103'


@contextmanager
def exact_two_descriptor_validators(pub, nodes, successor, root, proof_ref, edges):
    """One whole-scene context, plus strict exact membership at both levels."""
    old_grid, old_patch = pub.validate_grid, pub.validate_patch
    with complete_boundary_validators():
        old_effective = root_contract.validate_effective_coordinated_members
        def effective(children):
            # The complete effective hierarchy must contain all sixteen once.
            # Ordinary/unknown policies still run through their existing gate.
            verify_exact_members(children, nodes, proof_ref)
            return old_effective([n for n in children if not marker(n) or marker(n).get('policy') != POLICY])
        root_contract.validate_effective_coordinated_members = effective
        pub.validate_grid, pub.validate_patch = validator.validate_grid, validator.validate_patch
        try:
            with private_nested_contract(nodes, successor, root, proof_ref, edges):
                yield
        finally:
            root_contract.validate_effective_coordinated_members = old_effective
            pub.validate_grid, pub.validate_patch = old_grid, old_patch


def owned():
    lease = read(LOCAL/'reservation.json')
    assert reservations.owns(lease) and not (BASE/BATCH).exists()
    refs, pins = [Path(__file__)], {}
    def take(batch, filename):
        if batch not in pins:
            pins[batch] = authenticate(BASE/batch)[1]
            refs.append(BASE/batch/'result.json')
        path = BASE/batch/filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    admission = take(ADMISSION,'summary.json')
    assert admission['privateTerrainValidatorPassed'] and admission['exactEffectiveMembers'] == 16
    assert admission['finiteEdges'] == 22 and not admission['publication']
    proof = take(ADMISSION,'private-graph-proof.json')
    proof_ref = dict(path=str((BASE/ADMISSION/'private-graph-proof.json').relative_to(ROOT)),
                     sha256=digest((BASE/ADMISSION/'private-graph-proof.json').read_bytes()))
    nodes = {name:take(ADMISSION,Path(ref['path']).name) for name,ref in proof['members'].items()}
    assert len(nodes) == 16
    graph = take(GRAPH,'summary.json')
    assert graph['allFiniteSeamsPassed'] and graph['allMemberSurfaceChecksPassed']
    edges = [tuple(r['members']) for r in graph['edges']]
    assert len(edges) == 22
    candidate = take(CANDIDATE,'summary.json')
    successor = take(ADMISSION,'unapproved-successor-terrain.json')
    north = take(ADMISSION,'unapproved-north-root-cell.json')
    manifest_path = ROOT/'3d-viewer/city/data/manifest.json'
    root_path = ROOT/'3d-viewer/city/data/terrain.json'
    prior_path = ROOT/'3d-viewer'/candidate['replacedParent']['url']
    assert digest(manifest_path.read_bytes()) == admission['currentManifestSHA256'] == candidate['currentManifestSHA256']
    assert digest(root_path.read_bytes()) == proof['root']['sha256']
    assert digest(prior_path.read_bytes()) == proof['priorParent']['sha256'] == candidate['replacedParent']['sha256']
    root, original = read(root_path), read(manifest_path)
    refs += [manifest_path,root_path,prior_path]
    for item in original['terrainPatches']:
        refs.append(ROOT/'3d-viewer'/item['url'])
    input_hashes = {p:digest(p.read_bytes()) for p in refs}
    entries=[]
    for filename,suffix,node in [('unapproved-successor-terrain.json','parent',successor),
                                 ('unapproved-north-root-cell.json','north',north)]:
        path = BASE/ADMISSION/filename
        entry = dict(source=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),
            destination='city/data/'+BATCH+'-'+suffix+'.json',resolution=node['cell'],area='Private exact original source floor return')
        if suffix == 'parent':
            entry['replaces'] = candidate['replacedParent']
        entries.append(entry)
    plan = dict(areas=[],topLevelTerrainPatches=entries)
    pub = module('silvercord_two_descriptor_unchanged_canonical_stager',HERE.parent/'island-detail-integration/publish.py')
    pub.PINNED_INPUTS.clear()
    manifest, edits, report = copy.deepcopy(original), {}, {}
    old_grid,old_patch = pub.validate_grid,pub.validate_patch
    with exact_two_descriptor_validators(pub,nodes,successor,root,proof_ref,edges):
        pub.stage_top_level_terrain(plan,original,manifest,edits,report)
        pub.verify_inputs()
    assert (pub.validate_grid,pub.validate_patch) == (old_grid,old_patch)
    assert set(edits) == {ROOT/'3d-viewer'/e['destination'] for e in entries}
    assert all(edits[ROOT/'3d-viewer'/e['destination']] == (ROOT/e['source']).read_bytes() for e in entries)
    assert original == read(manifest_path) and len(report['topLevelTerrainPatches']) == 2
    assert report['replacedTerrainPatches'] == [dict(url=candidate['replacedParent']['url'],
        sha256=candidate['replacedParent']['sha256'],oldAssetRetained=True)]
    for p,h in input_hashes.items():
        assert digest(p.read_bytes()) == h
    assert reservations.owns(lease)
    save(BASE/BATCH/'plan.json',plan)
    save(BASE/BATCH/'terrain-dry-run-report.json',report)
    result = dict(uids=['landsd/233997:0','landsd/231645:0'],canonicalTwoDescriptorTerrainStagingPassed=True,
        exactEffectiveMembers=16,finiteEdges=22,stagedInMemoryAssets=2,publicFilesWritten=0,
        allOrdinaryTerrainGuardsPreserved=True,contextRestored=True,fullPublisherDryRunPassed=False,
        productionPolicyRegistered=False,physicalAcceptance=False,installationApproved=False,publication=False,
        sourceGeometryChanges=0,sourcePoseChanges=0)
    save(BASE/BATCH/'summary.json',result)
    refs += [HERE/n for n in ['silvercord_lippo_complete_floor_admission_v1_20261103.py',
        'fuying_five_member_terrain_stage_v1_20261029.py','nested_terrain_patch_validation_v1_20261027.py',
        'nested_native_terrain_validation_v1_20261027.py','nested_coordinated_native_boundary_v1_20261027.py']]
    refs.append(HERE.parent/'island-detail-integration/publish.py')
    module('silvercord_two_descriptor_terrain_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH,'canonical-two-descriptor-exact-floor-return-terrain-staging-without-publication',list(dict.fromkeys(refs)),result)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE/BATCH).exists()
        replacement = read(BASE/CANDIDATE/'summary.json')['replacedParent']
        parent = read(ROOT/'3d-viewer'/replacement['url'])
        resources = {'building:'+u for u in parent['meta']['targetUids']+['landsd/233997:0','landsd/231645:0']}
        resources |= {'terrain:'+replacement['url'],'terrain:city/data/terrain.json','immutable-source-proof:'+BATCH}
        claim = reservations.claim('silvercord-two-descriptor-terrain-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600)
        assert claim['ok'],claim
        execute_reserved(claim['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
