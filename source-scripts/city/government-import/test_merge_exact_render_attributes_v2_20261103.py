import copy
import unittest
from merge_exact_render_attributes_v2_20261103 import MANIFEST, add_current_hash, verify_row


class ExactAttributeReuse(unittest.TestCase):
    def setUp(self):
        self.source = dict(uid='x', sourceSHA256='a', source=dict(building=dict(uid='x', base=2)),
                           candidate=dict(entry=dict(sha256='a', rootTranslation=[-1, 0, 1])))
        self.original = dict(uid='x', building=copy.deepcopy(self.source['source']['building']),
                             entry=copy.deepcopy(self.source['candidate']['entry']))
        self.attr = dict(uid='x', sourceSHA256='a', completeOriginalIndex=[0, 1, 2],
                         completeLiteralWorldPosition=[0, 2, 0, 1, 2, 0, 0, 2, 1])
        self.geometry = dict(uid='x', sourceSHA256='a', index=[0, 1, 2], position=self.attr['completeLiteralWorldPosition'][:])

    def test_accept_exact_current_tuple(self):
        verify_row(self.source, self.original, self.attr, self.geometry)

    def test_reject_changed_geometry_or_source_context(self):
        cases = [lambda: self.source['source']['building'].update(base=3),
                 lambda: self.source['candidate']['entry'].update(rootTranslation=[0, 0, 1]),
                 lambda: self.geometry.update(sourceSHA256='b'),
                 lambda: self.geometry.update(index=[0, 2, 1]),
                 lambda: self.geometry['position'].__setitem__(1, 3)]
        for mutate in cases:
            self.setUp()
            mutate()
            with self.assertRaises(AssertionError):
                verify_row(self.source, self.original, self.attr, self.geometry)

    def test_allow_only_authenticated_old_manifest_reference(self):
        actual = {MANIFEST: 'new', 'geometry.js': 'stable'}
        hashes = {MANIFEST: 'new'}
        add_current_hash(hashes, MANIFEST, 'historical', actual.__getitem__)
        add_current_hash(hashes, 'geometry.js', 'stable', actual.__getitem__)
        self.assertEqual(hashes, actual)
        with self.assertRaises(AssertionError):
            add_current_hash(hashes, 'geometry.js', 'changed', actual.__getitem__)
        with self.assertRaises(AssertionError):
            add_current_hash({MANIFEST: 'stale'}, MANIFEST, 'historical', actual.__getitem__)
        with self.assertRaises(AssertionError):
            add_current_hash({MANIFEST: 'new', 'geometry.js': 'conflicting'}, 'geometry.js', 'stable', actual.__getitem__)


if __name__ == '__main__':
    unittest.main()
