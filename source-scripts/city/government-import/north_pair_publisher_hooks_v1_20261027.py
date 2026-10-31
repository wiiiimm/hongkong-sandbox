"""Exact North pair publisher hooks; no CLI, approval, or publication call.

The caller must enforce its reviewed-source/visual/reservation guards. These
hooks preserve canonical terrain and dependency checks and commit/rollback code.
"""
import copy
import json
from pathlib import Path

from original_availability_overlay_v1_20261027 import stage as stage_overlay
from original_independent_atomic_contract_v1_20261027 import verify_existing_atomic_group
from three_member_native_boundary_v1_20261027 import private_validator

SOURCES = {
    'landsd/182397:0': 'f16aa7f57a9b89962a6e1f3183e4dea922c7dbcb173515e608deae1ddc4b48b1',
    'landsd/309340:0': 'a8d145aaefe5aff04cd0f3d36b51ddf03baa951cb24d30504f0e9de272f12f0a'}
EXISTING = 'landsd/272986:0'


def install(canonical, root, surface, overlay, original_entries):
    root = Path(root).resolve()
    assert {u: m['sha256'] for u, m in original_entries.items()} == SOURCES
    assert overlay['uid'] == EXISTING and overlay['activationGroup'] == sorted([*SOURCES, EXISTING])
    assert surface['allEffectiveMembersRequired'] and len(surface['members']) == 3
    expected_members = copy.deepcopy(surface['members'])
    parent_path = root / '3d-viewer/city/data/terrain.json'
    parent_raw = canonical.read_bytes(parent_path)
    current_manifest = root / '3d-viewer/city/data/manifest.json'
    import hashlib
    assert hashlib.sha256(canonical.read_bytes(current_manifest)).hexdigest() == surface['currentManifest']['sha256']
    original_terrain = canonical.stage_top_level_terrain
    original_dependencies = canonical.stage_dependencies
    original_guard = canonical.PUBLICATION_GUARD

    def terrain(plan, original, manifest, edits, report):
        entries = plan.get('topLevelTerrainPatches', [])
        assert len(entries) == 3
        assert {e['source'] for e in entries} == {m['candidate']['path'] for m in expected_members}
        for member in expected_members:
            matches = [e for e in entries if e['source'] == member['candidate']['path']]
            assert len(matches) == 1
            entry = matches[0]
            assert entry['sha256'] == member['candidate']['sha256']
            assert entry['replaces'] == member['replaces'] and not entry.get('replacesMany')
            source = root / entry['source']
            assert hashlib.sha256(canonical.read_bytes(source)).hexdigest() == entry['sha256']
        assert canonical.read_bytes(parent_path) == parent_raw
        # Canonical native validation still runs for every surface. Only the
        # already-tested exact chain dispatcher is active during this call.
        with private_validator():
            return original_terrain(plan, original, manifest, edits, report)

    def dependencies(root_argument, plan, manifest, edits, new_models, report):
        assert Path(root_argument).resolve() == root
        assert set(new_models) == set(SOURCES)
        assert not plan.get('dependencyReviews'), 'No support metadata migration is part of this route'
        # Never substitute availability validation for retained-support checks.
        original_dependencies(root_argument, plan, manifest, edits, new_models, report)
        old_path = root / '3d-viewer' / overlay['url']
        before = json.loads(canonical.read_bytes(old_path))
        before_entry = next(m for m in before['models'] if m['uid'] == EXISTING)
        after = json.loads(canonical.read_bytes(root / overlay['source']))
        after_entry = next(m for m in after['models'] if m['uid'] == EXISTING)
        verify_existing_atomic_group(list(new_models.values()), SOURCES, original_entries, dict.fromkeys(SOURCES),
                                     {EXISTING: before_entry}, {EXISTING: after_entry})
        result = stage_overlay(root, overlay, manifest, edits, canonical.read_bytes)
        report.setdefault('availabilityCatalogueUpdates', []).append(result)

    canonical.stage_top_level_terrain = terrain
    canonical.stage_dependencies = dependencies
    assert canonical.PUBLICATION_GUARD is original_guard
    return canonical
