import unittest,numpy as np
from fractions import Fraction
from exact_original_slab_projection_coverage_20261010 import slab_coverage
from exact_original_projection_coverage_20261009 import exact_coverage,point,cross,signed_area
def face(points):return np.asarray([[x,2,z] for x,z in points],float)
class Coverage(unittest.TestCase):
    def compare(self,source,ground):
        a=slab_coverage(source,np.asarray(ground));b=exact_coverage(source,np.asarray(ground));self.assertEqual(a['exactProjectionCovered'],b['exactProjectionCovered'])
        if a.get('exactUncoveredInteriorWitnessXZ') is not None:
            p=tuple(map(Fraction,a['exactUncoveredInteriorWitnessXZ']))
            def inside(f):
                tri=[point(q) for q in f[:,[0,2]]]
                if signed_area(tri)<0:tri.reverse()
                return signed_area(tri)!=0 and all(cross(u,v,p)>=0 for u,v in zip(tri,tri[1:]+tri[:1]))
            self.assertTrue(inside(source));self.assertFalse(any(inside(f) for f in ground))
        return a
    def test_full(self):self.assertTrue(self.compare(face([(0,0),(1,0),(0,1)]),[face([(0,0),(1,0),(0,1)])])['exactProjectionCovered'])
    def test_overlap_not_sum(self):self.assertFalse(self.compare(face([(0,0),(1,0),(0,1)]),[face([(0,0),(.5,0),(0,.5)])]*8)['exactProjectionCovered'])
    def test_different_triangulation(self):self.assertTrue(self.compare(face([(0,0),(1,0),(0,1)]),[face([(0,0),(1,0),(1,1)]),face([(0,0),(1,1),(0,1)])])['exactProjectionCovered'])
    def test_tiny_real_gap(self):self.assertFalse(self.compare(face([(0,0),(1,0),(0,1)]),[face([(0,0),(1,0),(0,1-2**-30)])])['exactProjectionCovered'])
    def test_reversed(self):self.assertTrue(self.compare(face([(0,1),(1,0),(0,0)]),[face([(0,0),(0,1),(1,0)])])['exactProjectionCovered'])
    def test_vertical_line(self):self.assertTrue(self.compare(face([(0,0),(0,1),(0,1)]),[face([(0,0),(1,0),(0,1)])])['exactProjectionCovered'])
    def test_uncovered_tip(self):self.assertFalse(self.compare(face([(0,0),(0,1),(0,1)]),[face([(0,0),(1,0),(0,.5)])])['exactProjectionCovered'])
    def test_crossing_polygons(self):self.compare(face([(0,0),(2,0),(1,2)]),[face([(-1,.5),(3,.5),(1,1)]),face([(0,0),(2,0),(1,.75)]),face([(0,.75),(2,.75),(1,2)])])
    def annulus(self,tiny=False):
        A,B,C=(0,0),(4,0),(0,4);a=(1,1);b=(1+2**-20,1) if tiny else (2,1);c=(1,1+2**-20) if tiny else (1,2)
        return face([A,B,C]),[face(q) for q in [[A,B,b],[A,b,a],[B,C,c],[B,c,b],[C,A,a],[C,a,c]]]
    def test_interior_hole_all_edges_covered(self):
        s,g=self.annulus();self.assertFalse(self.compare(s,g)['exactProjectionCovered'])
        self.assertTrue(all(exact_coverage(np.asarray([a,b,b]),np.asarray(g))['exactProjectionCovered'] for a,b in zip(s,np.roll(s,-1,axis=0))))
    def test_tiny_interior_hole_all_edges_covered(self):
        s,g=self.annulus(True);self.assertFalse(self.compare(s,g)['exactProjectionCovered'])
        self.assertTrue(all(exact_coverage(np.asarray([a,b,b]),np.asarray(g))['exactProjectionCovered'] for a,b in zip(s,np.roll(s,-1,axis=0))))
    def test_disconnected_ranges(self):self.assertFalse(self.compare(face([(0,0),(4,0),(0,4)]),[face([(0,0),(1,0),(0,1)]),face([(3,0),(4,0),(3,1)])])['exactProjectionCovered'])
    def test_tangent_only(self):self.assertFalse(self.compare(face([(0,0),(1,0),(0,1)]),[face([(-1,0),(0,0),(-1,1)])])['exactProjectionCovered'])
    def test_overlapping_complete_coverage(self):self.assertTrue(self.compare(face([(0,0),(1,0),(0,1)]),[face([(-1,-1),(3,-1),(-1,3)]),face([(-1,-1),(3,-1),(-1,3)])])['exactProjectionCovered'])
    def test_zero_area_point(self):self.assertTrue(self.compare(face([(.25,.25)]*3),[face([(0,0),(1,0),(0,1)])])['exactProjectionCovered'])
    def test_zero_area_point_absent(self):self.assertFalse(self.compare(face([(2,2)]*3),[face([(0,0),(1,0),(0,1)])])['exactProjectionCovered'])
    def test_no_ground_faces(self):self.assertFalse(slab_coverage(face([(0,0),(1,0),(0,1)]),np.empty((0,3,3)))['exactProjectionCovered'])
    def test_nonfinite_rejected(self):
        s=face([(0,0),(1,0),(0,1)]);s[0,0]=np.nan
        with self.assertRaises(AssertionError):slab_coverage(s,np.asarray([face([(0,0),(1,0),(0,1)])]))
    def test_dyadic_partial_coverage_cases(self):
        rng=np.random.default_rng(641)
        for _ in range(24):
            ground=[face(rng.integers(-2,6,(3,2))/4) for _ in range(4)]
            self.compare(face([(0,0),(1,0),(0,1)]),ground)
if __name__=='__main__':unittest.main()
