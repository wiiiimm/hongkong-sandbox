"""Same synthetic full-result suite, now exercising the combined executor."""
import builtins,numpy as np
import exact_finite_combined_coverage_cache_v1_draft_20261014 as combined
import exact_finite_coverage_cache_v1_draft_20261014 as original
from test_exact_finite_coverage_cache_v1_draft_20261014 import CacheTests

class CombinedTests(CacheTests):
    def setUp(self):self.run,self.memo=combined.executor()
    def test_bounded_eviction_and_no_global_mutation(self):
        modules=[original.coverage,original.coarse,original.paired,original.refinement,original.bookkeeping]
        snapshots=[dict(m.__dict__)for m in modules];old_import=builtins.__import__
        run,memo=combined.executor(max_entries=1,max_key_bytes=256,max_polygons=1)
        a=np.array([[0,2,0],[2,2,0],[0,2,2.]]);g=np.array([[[0,0,0],[2,0,0],[0,0,2.]]])
        for face in [a,a+[1,0,0],a]:self.assertEqual(run(face,g),original.bookkeeping.finite_record(face,g))
        self.assertLessEqual(len(memo.entries),1);self.assertLessEqual(memo.key_bytes,256)
        self.assertEqual(memo.bounds_totals['maxCachedPolygons'],1)
        self.assertIs(builtins.__import__,old_import)
        for old,m in zip(snapshots,modules):
            self.assertEqual(set(old),set(m.__dict__));self.assertTrue(all(m.__dict__[k]is v for k,v in old.items()))
    def test_paired_three_coverage_calls_become_one(self):
        super().test_paired_three_coverage_calls_become_one()
        self.assertGreater(self.memo.bounds_totals['calls'],0)

if __name__=='__main__':
    import unittest
    # Do not execute the imported original TestCase a second time.
    unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CombinedTests)).wasSuccessful()or exit(1)
