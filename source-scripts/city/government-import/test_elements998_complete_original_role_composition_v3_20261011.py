"""Exact immutable census reuse rejects changed membership and world hashes."""
import copy,unittest
import elements998_complete_original_role_composition_v3_20261011 as k
from test_elements998_complete_original_role_composition_v2_20261011 import actual_fixture
class SavedWholeCensusReuseTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.args=actual_fixture()
 def check(self,args):return k.verify(**args,expected_binding=k.binding(**args))
 def test_actual_complete_four_stream_composition(self):
  r=self.check(self.args);self.assertEqual((r['completeNonzeroOriginalBodies'],r['completeStructuralPathBodies'],r['completeNonstructuralVisualBodies']),(998,866,132))
 def mutate(self):
  args=self.args.copy();args['finite']=self.args['finite'].copy();args['finite']['rows']=self.args['finite']['rows'].copy();args['finite']['rows'][2]=copy.deepcopy(args['finite']['rows'][2]);return args,args['finite']['rows'][2]['completeNonzeroEdgeCensus']
 def test_rebound_split_complete_census_is_not_reused(self):
  args,c=self.mutate();group=c['sharedEdgeConnectedComponents'][0];c['sharedEdgeConnectedComponents'][0]=group[:-1];c['sharedEdgeConnectedComponents'].append(group[-1:])
  with self.assertRaises(AssertionError):self.check(args)
 def test_rebound_census_for_different_world_is_not_reused(self):
  args,c=self.mutate();c['completeWorldTrianglesSHA256']='0'*64
  with self.assertRaises(AssertionError):self.check(args)
if __name__=='__main__':unittest.main()
