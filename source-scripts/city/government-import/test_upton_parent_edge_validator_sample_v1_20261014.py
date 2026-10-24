import unittest,ast
from pathlib import Path
from upton_parent_edge_validator_sample_v1_20261014 import parent_grid_sampler
class Sample(unittest.TestCase):
 def test_literal_validator_ast(self):
  base=Path(__file__).parent;v=ast.parse((base.parent/'island-detail-integration/native_terrain_validation.py').read_text());h=ast.parse((base/'upton_parent_edge_validator_sample_v1_20261014.py').read_text())
  find=lambda tree:next(n for n in ast.walk(tree)if isinstance(n,ast.FunctionDef)and n.name=='sample')
  self.assertEqual(ast.dump(find(v),include_attributes=False),ast.dump(find(h),include_attributes=False))
 def grid(self,step,heights):return {'w':2,'h':2,'meta':{'georef':{'aE':step,'aN':-step,'bE':834500.,'bN':816500.}},'elev':heights,'renderedElev':heights}
 def test_wrong_retained_extent_extrapolates(self):
  old=self.grid(5.,[0.,1.,0.,1.]);current=self.grid(70.,[0.,8.,0.,8.]);self.assertEqual(parent_grid_sampler(old)(70.,0.),14.);self.assertEqual(parent_grid_sampler(current)(70.,0.),8.)
 def test_shared_grid_diagonal(self):
  q=self.grid(70.,[2.,8.,4.,10.]);s=parent_grid_sampler(q);self.assertEqual(s(35.,35.),6.);self.assertEqual(s(70.,70.),10.)
 def test_rendered_floor_semantics(self):
  q=self.grid(70.,[0.,0.,0.,0.]);q.pop('renderedElev');self.assertEqual(parent_grid_sampler(q)(0.,0.),-4.)
 def test_lower_layer_maximum_is_independent(self):
  q=self.grid(70.,[8.,8.,8.,8.]);value=parent_grid_sampler(q)(0.,0.);own_y=8.;unrelated_upper_layer_y=11.;self.assertLess(abs(own_y-value),.01);self.assertGreater(abs(own_y-unrelated_upper_layer_y),.01)
if __name__=='__main__':unittest.main()
