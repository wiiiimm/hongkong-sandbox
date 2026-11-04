"""Focused scheduling tests: exclusions are exact, closed and restriction-record preserving."""
import unittest
from fractions import Fraction as F
from southside_saved_piece_closed_bounds_schedule_v1_20261012 import prepare_domains,saved_piece_bounds,nominate_domains
from southside_saved_finite_piece_guard_domain_v1_20261012 import restrict_saved_piece

def domain(i,points):return dict(domainID=i,domainKind='fixture-complete-domain',completeXZPoints=points)
def piece(points,y=F(-1)):
 return dict(exactMinimumGapM=str(y),allExactSourcePrismIntersectionVertices=[dict(exactOriginalSourcePoint=[str(x),str(y),str(z)],exactFiniteGroundHeightM='0',exactGapM=str(y))for x,z in points])
GROUND=[(F(0),F(0),F(0)),(F(1),F(0),F(0)),(F(0),F(0),F(1))]
class ScheduleTests(unittest.TestCase):
 def test_closed_actor_and_primitive_touch_retained(self):
  d=domain('triangle',[[0,0],[1,0],[0,1]]);nom,a=nominate_domains(saved_piece_bounds(piece([[1,0]])),prepare_domains([d]));self.assertEqual(nom,[d]);self.assertFalse(a['actorStrictDisjoint'])
 def test_next_exact_fraction_far_excluded(self):
  d=domain('triangle',[[0,0],[1,0],[0,1]]);nom,a=nominate_domains(saved_piece_bounds(piece([[F(1)+F(1,2**60),0]])),prepare_domains([d]));self.assertEqual(nom,[]);self.assertTrue(a['actorStrictDisjoint']);self.assertEqual(a['primitiveStrictDisjoint'],1)
 def test_union_gap_primitives_strictly_excluded(self):
  ds=[domain('left',[[0,0]]),domain('right',[[2,0]])];nom,a=nominate_domains(saved_piece_bounds(piece([[1,0]])),prepare_domains(ds));self.assertEqual(nom,[]);self.assertFalse(a['actorStrictDisjoint']);self.assertEqual(a['primitiveStrictDisjoint'],2)
 def test_complete_restriction_records_equal_with_pruning(self):
  ds=[domain('triangle',[[-1,0],[1,0],[0,1]]),domain('segment',[[-1,0],[1,0]]),domain('point',[[0,0]]),domain('far',[[20,20]])];p=piece([[-2,-2],[2,-2],[0,2]]);nom,a=nominate_domains(saved_piece_bounds(p),prepare_domains(ds));self.assertEqual(a['primitiveStrictDisjoint'],1);self.assertEqual(restrict_saved_piece(p,GROUND,ds),restrict_saved_piece(p,GROUND,nom))
 def test_nonfinite_unresolved_not_pruned(self):
  p=dict(collapsedProjectionConservative=True);ds=[domain('far',[[20,20]])];nom,a=nominate_domains(saved_piece_bounds(p),prepare_domains(ds));self.assertEqual(nom,ds);self.assertTrue(a['nonFiniteRecordNotPruned']);self.assertTrue(restrict_saved_piece(p,GROUND,nom)['unresolved'])
 def test_saved_plane_validation_still_required_before_exclusion(self):
  p=piece([[50,50]]);p['allExactSourcePrismIntersectionVertices'][0]['exactGapM']='0';nom,_=nominate_domains(saved_piece_bounds(p),prepare_domains([domain('point',[[0,0]])]));self.assertEqual(nom,[])
  with self.assertRaises(AssertionError):restrict_saved_piece(p,GROUND,[])
if __name__=='__main__':unittest.main()
