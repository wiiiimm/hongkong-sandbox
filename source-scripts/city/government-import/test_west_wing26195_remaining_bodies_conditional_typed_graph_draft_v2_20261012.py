"""DRAFT minimal adverse conditional bridge tests, no real source arithmetic."""
import unittest
from west_wing26195_remaining_bodies_conditional_typed_graph_draft_v2_20261012 import conditional_paths

def edge(a,b,dimension=1,interior=False,primitive=(2,2)):
 return dict(originalBodyLabels=[a,b],dimension=dimension,actualFinitePrimitiveDimensions=list(primitive),bothRelativeInteriorSurfaceCrossing=interior)
class Tests(unittest.TestCase):
 def paths(self,c,visual=()):return conditional_paths(c,body_count=5,visual_only=visual)
 def test_positive_boundary_chain_is_conditional(self):
  r=self.paths([edge(0,1),edge(1,2)]);self.assertEqual(r['conditionalPositiveDimensionalContactPaths'][2],[0,1,2]);self.assertFalse(r['actualIndependentRootProvided']);self.assertFalse(r['bodySupportAccepted'])
 def test_point_cannot_bridge(self):self.assertNotIn(2,self.paths([edge(0,1),edge(1,2,dimension=0)])['conditionalPositiveDimensionalContactPaths'])
 def test_zero_primitive_cannot_bridge(self):self.assertNotIn(2,self.paths([edge(0,1),edge(1,2,primitive=(0,2))])['conditionalPositiveDimensionalContactPaths'])
 def test_positive_interior_retains_existing_adjacency(self):
  r=self.paths([edge(0,1),edge(1,2,interior=True)]);self.assertEqual(r['conditionalPositiveDimensionalContactPaths'][2],[0,1,2]);self.assertEqual(r['retainedProperInteriorContactIndices'],[1]);self.assertFalse(r['actualIndependentRootProvided'])
 def test_visual_cannot_bridge(self):self.assertNotIn(2,self.paths([edge(0,1),edge(1,2)],visual=(1,))['conditionalPositiveDimensionalContactPaths'])
 def test_other_boundary_route_survives_excluded_point(self):self.assertEqual(self.paths([edge(0,2,dimension=0),edge(0,1),edge(1,2)])['conditionalPositiveDimensionalContactPaths'][2],[0,1,2])
 def test_disconnected_context_not_global_failure(self):self.assertEqual(self.paths([edge(3,4)])['unreachedNonvisualBodies'],[1,2,3,4])
 def test_invalid_self_body(self):
  with self.assertRaises(AssertionError):self.paths([edge(0,0)])
 def test_interior_point_still_cannot_bridge(self):self.assertNotIn(2,self.paths([edge(0,1),edge(1,2,dimension=0,interior=True)])['conditionalPositiveDimensionalContactPaths'])
 def test_interior_visual_still_cannot_bridge(self):self.assertNotIn(2,self.paths([edge(0,1,interior=True),edge(1,2)],visual=(1,))['conditionalPositiveDimensionalContactPaths'])
 def test_invalid_primitive_dimension(self):
  with self.assertRaises(AssertionError):self.paths([edge(0,1,primitive=(3,2))])
if __name__=='__main__':unittest.main()
