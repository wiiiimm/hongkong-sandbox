"""Broad phase must preserve every emitted original facet and its stable order."""
import importlib.util
import time
import unittest
from unittest.mock import patch
import numpy as np
from run import HERE


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


class IndexedParentClippingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = load('exhaustive_patch_builder', 'resolve-pass.py')
        cls.indexed = load('indexed_patch_builder', 'resolve-pass-indexed-parent-clipping.py')
        cls.parent = {'w': 4, 'h': 4, 'elev': [3 + (i % 4) * .1 + (i // 4) * .2 for i in range(16)],
            'vegetation': [0] * 16, 'meta': {'georef': {'bE': 834500, 'bN': 816500, 'aE': 70, 'aN': -70}}}
        cls.group = {'uids': ['landsd/1:0'], 'cells': [0, 0, 3, 3]}

    def build(self, module, native, budget=100000):
        with patch.object(module, 'validate_patch') as validate:
            result = module.make_patch(self.group, self.parent, np.asarray(native), [],
                native_core=[15, 15, 195, 195], parent_sha256='a' * 64,
                terrain_triangle_budget=budget)
            validate.assert_called_once_with(result, self.parent)
            return result

    def test_whole_patch_is_exactly_equal_for_slopes_vertical_facets_and_grid_edges(self):
        rng = np.random.default_rng(42)
        native = rng.uniform([-10, 4, -10], [220, 9, 220], (48, 3, 3)).tolist()
        native += [[[0, 4, 0], [70, 5, 0], [0, 6, 70]],
                   [[70, 4, 0], [70, 8, 0], [70, 5, 70]],
                   [[70 + 1e-12, 4, 0], [140, 6, 0], [70, 5, 70]],
                   [[0, 4, 0], [210, 5, 0], [0, 6, 210]]]
        before = np.asarray(native).copy()
        old = self.build(self.original, native)
        new = self.build(self.indexed, native)
        self.assertEqual(old, new)
        np.testing.assert_array_equal(np.asarray(native), before)

    def test_runtime_budget_remains_enforced_by_the_builder(self):
        native = [[[0, 4, 0], [210, 5, 0], [0, 6, 210]]]
        for module in (self.original, self.indexed):
            with self.assertRaisesRegex(AssertionError, 'terrain-runtime-budget'):
                self.build(module, native, budget=1)

    def test_realistic_small_source_facets_skip_only_empty_parent_intersections(self):
        native = []
        for x in range(0, 210, 14):
            for z in range(0, 210, 14):
                native += [[[x, 4, z], [x + 14, 4.1, z], [x, 4.2, z + 14]],
                           [[x + 14, 4.1, z], [x + 14, 4.3, z + 14], [x, 4.2, z + 14]]]
        start = time.perf_counter(); old = self.build(self.original, native); old_seconds = time.perf_counter() - start
        start = time.perf_counter(); new = self.build(self.indexed, native); new_seconds = time.perf_counter() - start
        self.assertEqual(old, new)
        print(f'Exact patch equality: exhaustive={old_seconds:.3f}s indexed={new_seconds:.3f}s', flush=True)


if __name__ == '__main__':
    unittest.main()
