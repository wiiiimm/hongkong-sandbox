"""Pure glue fixtures; no source geometry arithmetic or DB."""
import unittest
from nam_fung79099_source_bound_basic_mainbody_interbody_role_draft_v1_20261012 import typed_graph

def row(a,b,dim=1,zero=False,actual=False,interior=False):
 return dict(originalBodyLabels=[a,b],dimension=dim,actualFinitePrimitiveDimensions=[2,2],originalNonrenderingSourceFlags=[zero,False],actualNonrenderingSourceFlags=[actual,False],bothRelativeInteriorSurfaceCrossing=interior)
class Tests(unittest.TestCase):
 def paths(self,rs,terminal=()):return typed_graph(rs,body_count=4,terminal_bodies=terminal)['conditionalGraph']['conditionalPositiveDimensionalContactPaths']
 def test_positive_chain(self):self.assertEqual(self.paths([row(0,1),row(1,2)])['2'],[0,1,2])
 def test_point_cannot_bridge(self):self.assertNotIn('1',self.paths([row(0,1,0)]))
 def test_authored_zero_nonbridge_even_if_actual_nonzero(self):self.assertNotIn('1',self.paths([row(0,1,zero=True)]))
 def test_actual_zero_nonbridge(self):self.assertNotIn('1',self.paths([row(0,1,actual=True)]))
 def test_terminal_cannot_bridge(self):self.assertNotIn('2',self.paths([row(0,1),row(1,2)],(1,)))
 def test_interior_retained(self):self.assertIn('1',self.paths([row(0,1,interior=True)]))
 def test_zero_singleton_none_label_not_root(self):self.assertEqual(self.paths([row(None,1,zero=True)]),{'0':[0]})
 def test_bad_label_rejected(self):
  with self.assertRaises(AssertionError):self.paths([row(0,4)])
 def test_no_accepted_root_from_path(self):self.assertFalse(typed_graph([row(0,1)],body_count=4)['conditionalGraph']['actualIndependentRootProvided'])
 def test_deterministic_saved_indices(self):self.assertEqual(typed_graph([row(0,1,0),row(0,2)],body_count=4)['rawContactIndicesForFilteredGraph'],[1])
 def test_disconnected_not_fabricated(self):self.assertNotIn('3',self.paths([row(0,1),row(2,3)]))
 def test_area_contact_allowed(self):self.assertIn('1',self.paths([row(0,1,2)]))
if __name__=='__main__':unittest.main()
