import unittest
import numpy as np
import shapely
from preserve_original_boundary_facets_v1_20261027 import preserve_boundary_facets

class BoundaryFacetPreservation(unittest.TestCase):
    def setUp(self):
        self.face=np.asarray([[1,4,0],[2,5,0],[3,4,0]],float)
        self.interior=np.asarray([[4,3,4],[5,3,4],[4,3,5]],float)
        self.edit=shapely.box(4,4,6,6);self.bounds=[0,0,10,10]
    def test_exact_missing_boundary_face_restored_without_editing_inputs(self):
        old=np.asarray([self.face,self.interior]);candidate=np.asarray([self.interior]);before=old.copy()
        result,rows=preserve_boundary_facets(old,candidate,self.bounds,self.edit)
        self.assertTrue(np.array_equal(old,before));self.assertTrue(np.array_equal(result[0],self.interior));self.assertTrue(np.array_equal(result[1],self.face));self.assertEqual(rows[0]['originalFace'],0)
    def test_duplicate_multiplicity_retained(self):
        result,rows=preserve_boundary_facets(np.asarray([self.face,self.face]),np.asarray([self.face]),self.bounds,self.edit)
        self.assertEqual(len(result),2);self.assertEqual(len(rows),1)
    def test_original_face_touching_edit_is_rejected(self):
        with self.assertRaisesRegex(AssertionError,'touches edit'):
            preserve_boundary_facets(np.asarray([self.face]),np.asarray([self.interior]),self.bounds,shapely.box(0,0,4,2))
    def test_interior_changes_are_never_reversed(self):
        result,rows=preserve_boundary_facets(np.asarray([self.face,self.interior]),np.asarray([self.face]),self.bounds,self.edit)
        self.assertEqual(rows,[]);self.assertEqual(len(result),1)
    def test_complete_candidate_remains_exact(self):
        values=np.asarray([self.face,self.interior]);result,rows=preserve_boundary_facets(values,values,self.bounds,self.edit)
        self.assertEqual(rows,[]);self.assertTrue(np.array_equal(values,result))

if __name__=='__main__':unittest.main()
