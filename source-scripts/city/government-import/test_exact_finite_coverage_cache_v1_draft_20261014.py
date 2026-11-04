"""Synthetic-only full canonical-result equivalence; not executed by draft author."""
import copy,unittest,builtins
import numpy as np
import exact_finite_coverage_cache_v1_draft_20261014 as cached

class CacheTests(unittest.TestCase):
    def setUp(self):self.run,self.memo=cached.executor()
    def compare(self,face,ground):
        face=np.asarray(face,float);ground=np.asarray(ground,float).reshape(-1,3,3)
        a,b=face.tobytes(),ground.tobytes();actual=self.run(face,ground)
        self.assertEqual(actual,cached.bookkeeping.finite_record(face,ground))
        self.assertEqual(face.tobytes(),a);self.assertEqual(ground.tobytes(),b)
        return actual
    def test_positive_coarse_and_y_only_hash_rebinding(self):
        f=np.array([[0,3,0],[2,3,0],[0,3,2.]])
        g=np.array([[[0,0,0],[2,0,0],[0,0,2.]]])
        self.compare(f,g);f[:,1]+=1;g[:,:,1]+=.5
        self.compare(f,g);self.assertEqual((self.memo.misses,self.memo.hits),(1,1))
    def test_paired_three_coverage_calls_become_one(self):
        f=[[0,0,0],[2,2,0],[0,2,2]];g=[[[0,0,0],[2,1,0],[0,1,2]]]
        result=self.compare(f,g);self.assertIsNotNone(result['paired'])
        self.assertTrue(result['ordinaryBoundProved']);self.assertEqual((self.memo.misses,self.memo.hits),(1,2))
    def test_genuine_below_bound_unchanged(self):
        r=self.compare([[0,-1,0],[2,-1,0],[0,-1,2]],[[[0,0,0],[2,0,0],[0,0,2]]])
        self.assertFalse(r['ordinaryBoundProved']);self.assertTrue(r['projectionCovered'])
    def test_area_hole_and_piece_count_unchanged(self):
        f=[[0,1,0],[2,1,0],[0,1,2]];g=[[[0,0,0],[1,0,0],[0,0,1]]]
        r=self.compare(f,g);self.assertFalse(r['projectionCovered']);self.compare(f,g)
        self.assertEqual(self.memo.hits,1)
    def test_closed_segment_gap_unchanged(self):
        r=self.compare([[0,1,0],[2,1,0],[1,2,0]],[[[0,0,-1],[.5,0,-1],[0,0,1]]])
        self.assertFalse(r['projectionCovered'])
    def test_closed_point_coverage_unchanged(self):
        r=self.compare([[0,1,0],[0,2,0],[0,3,0]],[[[-1,0,-1],[1,0,-1],[0,0,1]]])
        self.assertTrue(r['projectionCovered'])
    def test_collapsed_ground_column_refinement_unchanged(self):
        self.compare([[0,2,0],[2,2,0],[0,2,2]],[[[0,0,0],[2,0,0],[0,0,2]],[[0,0,0],[0,3,0],[1,0,0]]])
    def test_ground_order_and_duplicates_are_distinct_keys(self):
        f=[[0,2,0],[2,2,0],[0,2,2]];a=[[0,0,0],[2,0,0],[0,0,2]];b=[[0,0,0],[1,0,0],[0,0,1]]
        self.compare(f,[a,b]);self.compare(f,[b,a]);self.compare(f,[a,b,b]);self.assertEqual(self.memo.misses,3)
    def test_changed_projection_and_signed_zero_not_aliased(self):
        f=np.array([[0.,2,0],[2,2,0],[0,2,2]]);g=np.array([[[0.,0,0],[2,0,0],[0,0,2]]])
        self.compare(f,g);g[0,0,0]=-0.;self.compare(f,g);g[0,0,0]=.25;self.compare(f,g)
        self.assertEqual(self.memo.misses,3)
    def test_cache_result_mutation_does_not_escape(self):
        f=np.array([[0,2,0],[2,2,0],[0,2,2.]]);g=np.array([[[0,0,0],[2,0,0],[0,0,2.]]])
        a=self.memo(f,g);a['exactProjectionCovered']=False
        self.assertEqual(self.memo(f,g),cached.coverage.exact_coverage(f,g))
    def test_bounded_eviction_and_no_global_mutation(self):
        snapshots=[dict(m.__dict__)for m in [cached.coverage,cached.coarse,cached.paired,cached.refinement,cached.bookkeeping]]
        old_import=builtins.__import__;run,memo=cached.executor(max_entries=1,max_key_bytes=256)
        a=np.array([[0,2,0],[2,2,0],[0,2,2.]]);g=np.array([[[0,0,0],[2,0,0],[0,0,2.]]])
        run(a,g);b=a.copy();b[:,0]+=1;run(b,g);run(a,g)
        self.assertLessEqual(len(memo.entries),1);self.assertLessEqual(memo.key_bytes,256)
        self.assertIs(builtins.__import__,old_import)
        for old,m in zip(snapshots,[cached.coverage,cached.coarse,cached.paired,cached.refinement,cached.bookkeeping]):
            self.assertEqual(set(old),set(m.__dict__));self.assertTrue(all(m.__dict__[k]is v for k,v in old.items()))
    def test_nonfinite_and_shape_fail_closed(self):
        for face,ground in [(np.full((3,3),np.nan),np.zeros((1,3,3))),(np.zeros((2,3)),np.zeros((1,3,3))),(np.zeros((3,3)),np.zeros((1,2,3)))]:
            with self.assertRaises(AssertionError):self.memo(face,ground)

if __name__=='__main__':unittest.main()
