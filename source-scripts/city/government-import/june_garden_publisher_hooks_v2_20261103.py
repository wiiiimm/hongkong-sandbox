"""Exact June Garden hooks, composing unchanged terrain/dependency publishers.

No CLI or publication call. The caller must authenticate source, terrain,
visual, reservation and current-input evidence before installing these hooks.
"""
import copy
import hashlib
from pathlib import Path
from original_coordinated_retained_contract_v1_20261027 import verify_metadata
from three_member_native_boundary_v1_20261027 import private_validator

P = 'landsd/227380:0'
SMALL = 'landsd/264492:0'
SOURCES = {
    P:'0ec881f882c5f52a34ba7d86f20b25a0903dcfcf8d8935ef949ab20569e99dfa',
    'landsd/264489:0':'ec140d51c93562e9a028af14fa4f65263cb05c145a44422cf8ff71f795495e39',
    'landsd/264491:0':'b283272706ea448412a8fa696144385725e8707519dea76fec5531d8f8b175ed',
    SMALL:'265d11ddab4f31ffcfcbd2f1826107465335f4bbf69ee8b6544ed08ddafcfb09',
    'landsd/264493:0':'61044861002c15c47ff5ef33ae279d0979bda4f72e0364396b5cd82d7324bb51',
    'landsd/264495:0':'ddc471e17f3b0460bac1ecd4deba4c4d5e2a54c3d95968fe344d8f85a7bb5478'}
SUPPORTS = dict.fromkeys(set(SOURCES)-{P,SMALL},P)
DESTINATIONS = {name:'city/data/government-native-june-garden-'+name+'-v1-20261103.json' for name in ['south','middle','north']}


def install(canonical, root, surface, original_entries, manifest_sha256):
    root = Path(root).resolve()
    assert {u:m['sha256'] for u,m in original_entries.items()} == SOURCES
    assert surface['allEffectiveMembersRequired'] and len(surface['members']) == 3
    members = copy.deepcopy(surface['members'])
    assert {m['member'] for m in members} == {'south','middle','north'}
    for m in members:
        assert m['replaces']['url'] == 'city/data/government-native-north-pair-'+m['member']+'-v1-20261027.json'
    manifest = root/'3d-viewer/city/data/manifest.json'
    assert hashlib.sha256(canonical.read_bytes(manifest)).hexdigest() == manifest_sha256
    parent = root/'3d-viewer/city/data/terrain.json'
    parent_raw = canonical.read_bytes(parent)
    original_terrain = canonical.stage_top_level_terrain
    original_dependencies = canonical.stage_dependencies
    original_guard = canonical.PUBLICATION_GUARD

    def terrain(plan, original, manifest_data, edits, report):
        entries = plan.get('topLevelTerrainPatches',[])
        assert len(entries) == 3 and len({e['source'] for e in entries}) == 3
        assert {e['source'] for e in entries} == {m['candidate']['path'] for m in members}
        for m in members:
            e = next(e for e in entries if e['source'] == m['candidate']['path'])
            assert e['sha256'] == m['candidate']['sha256'] and e['replaces'] == m['replaces']
            assert e['destination'] == DESTINATIONS[m['member']] and e['destination'] != m['replaces']['url']
            assert not e.get('replacesMany')
            assert not (root/'3d-viewer'/e['destination']).exists(), 'Never overwrite an installed terrain asset'
            assert hashlib.sha256(canonical.read_bytes(root/e['source'])).hexdigest() == e['sha256']
        assert canonical.read_bytes(parent) == parent_raw
        with private_validator():
            return original_terrain(plan,original,manifest_data,edits,report)

    def dependencies(root_argument,plan,manifest_data,edits,new_models,report):
        assert Path(root_argument).resolve() == root and set(new_models) == set(SOURCES)
        assert not plan.get('dependencyReviews'), 'No installed support migration permitted'
        verify_metadata(list(new_models.values()),SOURCES,SUPPORTS,original_entries,{P:None,SMALL:None})
        # Always retain every canonical installed-support check and its failure.
        return original_dependencies(root_argument,plan,manifest_data,edits,new_models,report)

    canonical.stage_top_level_terrain = terrain
    canonical.stage_dependencies = dependencies
    assert canonical.PUBLICATION_GUARD is original_guard
    return canonical
