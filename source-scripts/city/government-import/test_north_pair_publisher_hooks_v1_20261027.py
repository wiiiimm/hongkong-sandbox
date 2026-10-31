import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

import north_pair_publisher_hooks_v1_20261027 as hooks
import three_member_native_boundary_v1_20261027 as chain


class ExactPublisherHooks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        folder = self.root / '3d-viewer/city/data'
        folder.mkdir(parents=True)
        (folder / 'terrain.json').write_text('{}')
        manifest = folder / 'manifest.json'
        manifest.write_text('{}')
        self.calls = []
        def terrain(*args):
            self.calls.append('canonical-terrain')
            raise RuntimeError('canonical terrain rejection')
        def dependencies(*args):
            self.calls.append('canonical-dependencies')
            raise RuntimeError('existing fallback support rejection')
        self.guard = object()
        self.canonical = SimpleNamespace(read_bytes=Path.read_bytes, stage_top_level_terrain=terrain,
                                         stage_dependencies=dependencies, PUBLICATION_GUARD=self.guard)
        self.originals = {u: {'uid': u, 'sha256': sha} for u, sha in hooks.SOURCES.items()}
        self.overlay = {'uid': hooks.EXISTING, 'activationGroup': sorted([*hooks.SOURCES, hooks.EXISTING])}
        members = []
        self.plan = {'topLevelTerrainPatches': []}
        for i in range(3):
            name = f'candidate-{i}.json'
            (self.root / name).write_text('{}')
            candidate = {'path': name, 'sha256': hashlib.sha256(b'{}').hexdigest()}
            replaces = {'url': f'old-{i}.json', 'sha256': str(i) * 64, 'retainedUids': []}
            members.append({'candidate': candidate, 'replaces': replaces})
            self.plan['topLevelTerrainPatches'].append({'source': name, 'sha256': candidate['sha256'], 'replaces': replaces})
        self.surface = {'allEffectiveMembersRequired': True, 'members': members,
                        'currentManifest': {'sha256': hashlib.sha256(manifest.read_bytes()).hexdigest()}}

    def install(self):
        return hooks.install(self.canonical, self.root, self.surface, self.overlay, self.originals)

    def test_retained_support_failure_propagates_before_overlay(self):
        c = self.install()
        manifest, edits, report = {}, {}, {}
        with self.assertRaisesRegex(RuntimeError, 'existing fallback support rejection'):
            c.stage_dependencies(self.root, {}, manifest, edits, self.originals, report)
        self.assertEqual(self.calls, ['canonical-dependencies'])
        self.assertEqual((manifest, edits, report), ({}, {}, {}))

    def test_commit_guard_is_unchanged(self):
        self.assertIs(self.install().PUBLICATION_GUARD, self.guard)

    def test_terrain_rejection_propagates_and_dispatcher_restores(self):
        old_boundary = chain.legacy.coordinated_boundary
        old_effective = chain.legacy.validate_effective_coordinated_members
        c = self.install()
        with self.assertRaisesRegex(RuntimeError, 'canonical terrain rejection'):
            c.stage_top_level_terrain(self.plan, {}, {}, {}, {})
        self.assertEqual(self.calls, ['canonical-terrain'])
        self.assertIs(chain.legacy.coordinated_boundary, old_boundary)
        self.assertIs(chain.legacy.validate_effective_coordinated_members, old_effective)

    def test_missing_member_rejected(self):
        c = self.install()
        self.plan['topLevelTerrainPatches'].pop()
        with self.assertRaises(AssertionError):
            c.stage_top_level_terrain(self.plan, {}, {}, {}, {})
        self.assertFalse(self.calls)

    def test_changed_candidate_rejected(self):
        c = self.install()
        (self.root / 'candidate-1.json').write_text('{"changed":true}')
        with self.assertRaises(AssertionError):
            c.stage_top_level_terrain(self.plan, {}, {}, {}, {})
        self.assertFalse(self.calls)

    def test_changed_parent_rejected(self):
        c = self.install()
        (self.root / '3d-viewer/city/data/terrain.json').write_text('{"changed":true}')
        with self.assertRaises(AssertionError):
            c.stage_top_level_terrain(self.plan, {}, {}, {}, {})
        self.assertFalse(self.calls)

    def test_unknown_source_rejected(self):
        self.originals['landsd/182397:0']['sha256'] = '0' * 64
        with self.assertRaises(AssertionError):
            self.install()

    def test_support_migration_is_not_part_of_route(self):
        c = self.install()
        with self.assertRaises(AssertionError):
            c.stage_dependencies(self.root, {'dependencyReviews': [{}]}, {}, {}, self.originals, {})
        self.assertFalse(self.calls)

    def test_wrong_existing_peer_rejected(self):
        self.overlay['uid'] = 'landsd/other:0'
        with self.assertRaises(AssertionError):
            self.install()


if __name__ == '__main__':
    unittest.main()
