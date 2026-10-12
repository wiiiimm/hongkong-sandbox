"""UNEXECUTED focused integration cases; existing exact clip kernel unchanged."""
import unittest
from fractions import Fraction as F
from southside_saved_finite_piece_guard_domain_v1_20261012 import closed_clip,restrict_saved_piece
P=lambda rows:[tuple(F(v)for v in r)for r in rows]
class SavedPieceTests(unittest.TestCase):
 def test_no_negative_vertex_inside_but_clipped_region_negative(self):
  poly=P([[-2,-1,-2],[2,-1,-2],[0,-1,2]]);domain=P([[-1,0],[1,0],[0,1]]);self.assertTrue(closed_clip(poly,domain));self.assertTrue(all(p[1]<F(-1,2)for p in closed_clip(poly,domain)))
 def test_exact_touch_retained(self):self.assertEqual(closed_clip(P([[0,1,0]]),P([[0,0],[1,0],[0,1]])),P([[0,1,0]]))
 def test_strict_far_excluded(self):self.assertEqual(closed_clip(P([[2,1,2]]),P([[0,0],[1,0],[0,1]])),[])
 def test_clockwise_same(self):
  p=P([[-1,1,-1],[2,1,-1],[0,1,2]]);d=P([[0,0],[1,0],[0,1]]);self.assertEqual(set(closed_clip(p,d)),set(closed_clip(p,list(reversed(d)))))
 def test_vertical_source_preserves_lower_y(self):self.assertEqual({p[1]for p in closed_clip(P([[0,-2,0],[0,2,0],[0,2,2]]),P([[0,0],[1,0],[0,1]]))},{F(-2),F(2),F(0)})
 def test_segment_domain_endpoints(self):self.assertEqual(set(closed_clip(P([[-2,0,0],[2,0,0]]),P([[-1,0],[1,0]]))),set(P([[-1,0,0],[1,0,0]])))
 def test_point_domain(self):self.assertEqual(closed_clip(P([[-1,0,0],[1,0,0]]),P([[0,0]])),P([[0,0,0]]))
 def test_below_next_fraction_bound(self):
  y=F(-1,2)-F(1,2**60);piece={'originalGroundFace':0,'exactMinimumGapM':str(y),'allExactSourcePrismIntersectionVertices':[{'exactOriginalSourcePoint':['0',str(y),'0'],'exactFiniteGroundHeightM':'0','exactGapM':str(y)}]};r=restrict_saved_piece(piece,P([[0,0,0],[1,0,0],[0,0,1]]),[{'domainID':'point','domainKind':'unused-POSITION-point','completeXZPoints':[['0','0']]}]);self.assertFalse(r['restrictions'][0]['unchangedOrdinaryBoundProvedOnRestriction'])
 def test_changed_saved_gap_rejected(self):
  p={'exactMinimumGapM':'0','allExactSourcePrismIntersectionVertices':[{'exactOriginalSourcePoint':['0','0','0'],'exactFiniteGroundHeightM':'0','exactGapM':'1'}]}
  with self.assertRaises(AssertionError):restrict_saved_piece(p,P([[0,0,0],[1,0,0],[0,0,1]]),[])
 def test_collapsed_ground_unresolved(self):self.assertTrue(restrict_saved_piece({'collapsedProjectionConservative':True},P([[0,0,0],[0,1,0],[1,0,0]]),[])['unresolved'])
if __name__=='__main__':unittest.main()
