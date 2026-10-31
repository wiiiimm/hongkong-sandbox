import contextlib,io,tempfile,unittest
from pathlib import Path
from fractions import Fraction as F
from exact_resumable_projected_inventory_v1_20261011 import Checkpoints,raw
from exact_cross_set_projected_source_coverage_v1_20261011 import contacts,coverage
from exact_source_core_ten_metre_transition_domain_v1_20261011 import intersection
from exact_original_projection_coverage_v2_20261010 import signed_area,subtract

class CrossSetTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name)
 def compute(self,s,n):
  with contextlib.redirect_stdout(io.StringIO()):
   cp=Checkpoints(self.path/'contacts',s+n,[],lambda:None,2);pos,counts=contacts(s,n,cp);cv=Checkpoints(self.path/'coverage',s+n,[],lambda:None,2);rows=coverage(s,n,cv)
  expected=[]
  for i,p in enumerate(s):
   for j,q in enumerate(n):
    area=signed_area(intersection(p,q))
    if area:expected.append((i,j,area))
  self.assertEqual([(r['sourcePiece'],r['nativePiece'],r['exactPositiveAreaM2'])for r in pos],expected)
  for j,q in enumerate(n):
   remaining=[q]
   for p in s:remaining=[part for r in remaining for part in subtract(r,p)]
   self.assertEqual(rows[j]['exactUncoveredPositiveAreaM2'],sum(signed_area(p)for p in remaining))
  self.assertEqual(counts['completeCrossPairs'],len(s)*len(n));return pos,rows
 def test_complete_coverage(self):
  _,rows=self.compute([[(0,0),(5,0),(0,5)],[(5,0),(5,5),(0,5)]],[[(1,1),(4,1),(1,4)]]);self.assertFalse(rows[0]['allUncoveredPositivePolygons'])
 def test_old_native_overlap_does_not_fake_source_absence(self):
  _,rows=self.compute([[(0,0),(5,0),(0,5)]],[[(1,1),(2,1),(1,2)],[(1,1),(2,1),(1,2)]]);self.assertEqual(len(rows),2);self.assertTrue(all(not r['allUncoveredPositivePolygons']for r in rows))
 def test_partial_coverage_is_failure(self):
  _,rows=self.compute([[(0,0),(1,0),(0,1)]],[[(0,0),(2,0),(0,2)]]);self.assertGreater(rows[0]['exactUncoveredPositiveAreaM2'],0)
 def test_wrong_domain_far_disjoint(self):
  pos,rows=self.compute([[(0,0),(1,0),(0,1)]],[[(50,50),(51,50),(50,51)]]);self.assertFalse(pos);self.assertGreater(rows[0]['exactUncoveredPositiveAreaM2'],0)
 def test_point_only_not_selection(self):
  pos,_=self.compute([[(0,0),(1,0),(0,1)]],[[(1,0),(2,0),(1,1)]]);self.assertFalse(pos)
 def test_whole_edge_only_not_selection(self):
  pos,_=self.compute([[(0,0),(1,0),(0,1)]],[[(1,0),(1,1),(0,1)]]);self.assertFalse(pos)
 def test_tiny_positive_intersection_kept(self):
  e=F(1,2**70);pos,_=self.compute([[(0,0),(1,0),(0,1)]],[[(1-e,0),(2,0),(1-e,1)]]);self.assertTrue(pos)
 def test_negative_bucket_and_rational_coords(self):self.compute([[(-6,-6),(-4,-6),(-6,-4)]],[[(-5,-5),(F(-9,2),-5),(-5,F(-9,2))]])
 def test_hole_cannot_be_hidden_by_total_area(self):
  _,rows=self.compute([[(0,0),(2,0),(0,2)],[(8,8),(10,8),(8,10)]],[[(1,1),(9,1),(1,9)]]);self.assertGreater(rows[0]['exactUncoveredPositiveAreaM2'],0)
 def test_resume_exact(self):
  s=[[(0,0),(3,0),(0,3)]];n=[[(1,1),(2,1),(1,2)]];a=self.compute(s,n);b=self.compute(s,n);self.assertEqual(raw(a),raw(b))

if __name__=='__main__':unittest.main()
