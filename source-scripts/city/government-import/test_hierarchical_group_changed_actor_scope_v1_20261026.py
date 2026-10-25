import unittest,json
import numpy as np
from hierarchical_group_changed_actor_scope_v1_20261026 import separation

class SeparationTests(unittest.TestCase):
 def test_overlap_is_affected(self):
  self.assertFalse(separation([0,0],[2,2],[1,1,3,3])['strictlyDisjoint'])
 def test_boundary_contact_is_affected(self):
  self.assertFalse(separation([0,0],[1,1],[1,0,2,1])['strictlyDisjoint'])
 def test_half_metre_margin_is_affected(self):
  self.assertFalse(separation([0,0],[1,1],[1.5,0,2,1])['strictlyDisjoint'])
 def test_strict_separation(self):
  self.assertTrue(separation([0,0],[1,1],[1.50001,0,2,1])['strictlyDisjoint'])
 def test_numpy_inputs_serialize_without_losing_false(self):
  proof=separation(np.array([0.,0.]),np.array([1.,1.]),[0,0,2,2])
  self.assertIs(json.loads(json.dumps(proof))['strictlyDisjoint'],False)
if __name__=='__main__':unittest.main()
