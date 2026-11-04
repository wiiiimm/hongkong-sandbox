import unittest
from fractions import Fraction as F
from exact_finite_upper_surface_cells_20261011 import partition,area,height
P=[(0,0,0),(1,0,0),(1,0,1),(0,0,1)]
def flat(y):return [[(0,y,0),(1,y,0),(1,y,1)],[(0,y,0),(1,y,1),(0,y,1)]]
class Tests(unittest.TestCase):
 def test_complete_flat(self):
  c,p=partition(P,flat(2));self.assertEqual(sum(area(r['polygon'])for r in c),1);self.assertTrue(p['exactInteriorPartition']['exactPartitionPassed']);self.assertEqual({v['closedUpperY']for v in p['completeBoundaryVertices']},{2})
 def test_lower_never_selected(self):self.assertEqual({r['faceIndex']for r in partition(P,flat(1)+flat(2))[0]},{2,3})
 def test_coincident_tie(self):self.assertEqual({r['faceIndex']for r in partition(P,flat(2)+flat(2))[0]},{0,1})
 def test_crossover(self):
  a=[[(0,0,0),(1,1,0),(1,1,1)],[(0,0,0),(1,1,1),(0,0,1)]];b=[[(0,1,0),(1,0,0),(1,0,1)],[(0,1,0),(1,0,1),(0,1,1)]]
  c,p=partition(P,a+b);self.assertTrue(any(v['point'][0]==F(1,2)for v in p['completeBoundaryVertices']))
  for r in c:
   for q in r['polygon']:self.assertEqual(height(q,r['plane']),max(q[0],1-q[0]))
 def test_finite_boundary_jump(self):
  cap=[[(0,3,0),(F(1,2),3,0),(F(1,2),3,1)],[(0,3,0),(F(1,2),3,1),(0,3,1)]]
  c,p=partition(P,flat(1)+cap);self.assertEqual(sum(area(r['polygon'])for r in c),1)
  jump=[r for r in p['completeBoundaryVertices']if r['point'][0]==F(1,2)];self.assertTrue(jump);self.assertEqual({r['closedUpperY']for r in jump},{3})
 def test_no_infinite_plane_extension(self):
  c,_=partition(P,flat(1)+[[(0,3,0),(F(1,2),3,0),(0,3,1)]])
  for r in c:
   if r['faceIndex']==2:self.assertTrue(all(q[0]<=F(1,2)for q in r['polygon']))
 def test_tiny_real_facet(self):
  tiny=F(1,2**80);c,p=partition(P,flat(1)+[[(0,2,0),(tiny,2,0),(0,2,tiny)]]);self.assertIn(2,{r['faceIndex']for r in c});self.assertEqual(p['completeZeroProjectedAreaFaceIds'],[])
 def test_vertical_zero_inventory(self):
  c,p=partition(P,flat(1)+[[(0,0,0),(0,2,0),(0,1,1)],[(0,0,0)]*3]);self.assertEqual(p['completeSourceFaceCount'],4);self.assertEqual(p['completeZeroProjectedAreaFaceIds'],[2,3])
 def test_reversed(self):self.assertEqual(sum(area(r['polygon'])for r in partition(list(reversed(P)),[list(reversed(t))for t in flat(1)])[0]),1)
 def test_missing_finite_domain(self):
  with self.assertRaises(AssertionError):partition(P,flat(1)[:1])
 def test_nonfinite(self):
  with self.assertRaises(AssertionError):partition(P,flat(float('nan')))
 def test_nonconvex(self):
  with self.assertRaises(AssertionError):partition([(0,0,0),(1,0,0),(F(1,4),0,F(1,4)),(0,0,1)],flat(1))
 def test_resource_exact_boundary(self):
  with self.assertRaises(AssertionError):partition(P,flat(1),max_cells=1)
  self.assertEqual(len(partition(P,flat(1),max_cells=2)[0]),2)
 def test_operations(self):
  with self.assertRaises(AssertionError):partition(P,flat(1),max_operations=1)
 def test_changed_plane(self):self.assertNotEqual(partition(P,flat(2))[0],partition(P,flat(3))[0])
 def test_disjoint_inventory(self):self.assertNotIn(2,partition(P,flat(1)+[[(10,4,10),(11,4,10),(10,4,11)]])[1]['exactEligibleFiniteHeightFaceIds'])
if __name__=='__main__':unittest.main()
