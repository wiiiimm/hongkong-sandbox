import unittest,numpy as np
from exact_runtime_coplanar_consolidation_20261010 import consolidate,ears
from exact_original_slab_projection_coverage_20261010 import slab_coverage
def grid(w=2,h=2,vertical=False):
    def p(x,z):return [0,x,z] if vertical else [x,3,z]
    return np.asarray([[p(x,z),p(x+1,z),p(x,z+1)] for z in range(h) for x in range(w)]+[[p(x+1,z),p(x+1,z+1),p(x,z+1)] for z in range(h) for x in range(w)],float)
class Consolidation(unittest.TestCase):
    def equivalent(self,t):
        out,p=consolidate(t);self.assertTrue(p['allOriginalFacesAccounted']);self.assertTrue(p['allDegenerateOriginalsRetained']);self.assertEqual({i for r in p['components'] for i in r['originalFaceIds']},set(range(len(t))))
        self.assertTrue(set(map(tuple,out.reshape(-1,3)))<=set(map(tuple,t.astype(np.float32).reshape(-1,3))))
        return out,p
    def test_flat_connected_grid(self):
        t=grid();out,p=self.equivalent(t);self.assertEqual(len(out),2)
        self.assertTrue(all(slab_coverage(f,out)['exactProjectionCovered'] for f in t));self.assertTrue(all(slab_coverage(f,t)['exactProjectionCovered'] for f in out))
    def test_vertical_retaining_grid(self):
        t=grid(vertical=True);out,p=self.equivalent(t);self.assertEqual(len(out),2)
        self.assertTrue(all(slab_coverage(f[:,[1,0,2]],out[:,:,[1,0,2]])['exactProjectionCovered'] for f in t))
    def test_degenerate_original_retained(self):
        d=np.asarray([[[0,3,0],[1,3,0],[2,3,0]]],float);out,p=self.equivalent(np.concatenate([grid(),d]));self.assertEqual(len(out),3);self.assertTrue(any(np.array_equal(f,d[0]) for f in out))
    def test_tiny_nonzero_preserved(self):
        t=np.asarray([[[0,3,0],[2**-20,3,0],[0,3,2**-20]]],float);out,p=self.equivalent(t);self.assertEqual(len(out),1);self.assertTrue(np.array_equal(out,t))
    def test_different_heights_never_merge(self):
        a=grid(1,1);b=a.copy();b[:,:,1]+=2**-20;out,p=self.equivalent(np.concatenate([a,b]));self.assertEqual(len(out),4)
    def test_opposite_winding_not_cancelled(self):
        a=grid();out,p=self.equivalent(np.concatenate([a,a[:,::-1]]));self.assertEqual(len(out),4)
    def test_duplicate_overlap_retained(self):
        a=grid();out,p=self.equivalent(np.concatenate([a,a]));self.assertEqual(len(out),16)
    def test_hole_retained(self):
        a=grid(3,3);a=np.concatenate([a[:4],a[5:13],a[14:]]);out,p=self.equivalent(a);self.assertEqual(len(out),len(a))
    def test_disconnected_regions_preserved(self):
        a=grid();b=a.copy();b[:,:,0]+=10;out,p=self.equivalent(np.concatenate([a,b]));self.assertEqual(len(out),4)
    def test_self_crossing_boundary_rejected(self):
        with self.assertRaises(AssertionError):ears([(0,0),(2,2),(0,2),(2,0)])
    def test_concave_ear_area(self):self.assertEqual(len(ears([(0,0),(3,0),(3,1),(1,1),(1,3),(0,3)])),4)
    def test_integer_overflow_scale(self):
        a=grid();a[:,:,[0,2]]+=np.asarray([30000,-30000]);out,p=self.equivalent(a);self.assertEqual(len(out),2)
if __name__=='__main__':unittest.main()
