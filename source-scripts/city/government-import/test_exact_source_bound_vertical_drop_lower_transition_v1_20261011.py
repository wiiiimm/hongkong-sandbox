"""DRAFT bounded source-derived drop counterexamples; awaiting ROOT test approval."""
import unittest
from fractions import Fraction as F
from exact_source_bound_vertical_drop_lower_transition_v1_20261011 import lower_endpoint,nominate,contacts,domain_proof
from exact_faithful_source_step_junction_feasibility_v2_20261011 import native_footprints
DOMAIN=[[(F(-5),F(-5)),(F(10),F(-5)),(F(-5),F(10))]]
def plane(y):return [(0,y,0),(2,y,0),(0,y,2)]
def probe(source=None,q=(1,-1),outer=(1,0,-2),domain=DOMAIN):return nominate(source or[plane(2),plane(0)],(0,2,0),(2,2,0),q,outer,domain)
class Drop(unittest.TestCase):
 def test_no_finite_lower_owner(self):self.assertFalse(lower_endpoint(native_footprints([plane(2)]),(0,2,0))['qualified'])
 def test_equal_plane_is_not_lower(self):self.assertFalse(lower_endpoint(native_footprints([plane(2),plane(2)]),(0,2,0))['qualified'])
 def test_highest_genuine_lower(self):self.assertEqual(lower_endpoint(native_footprints([plane(2),plane(-1),plane(1)]),(0,2,0))['exactLowerPoint'],(0,1,0))
 def test_nonrepresentable_lower_plane_rejected(self):
  n=native_footprints([[(0,0,0),(3,1,0),(0,0,3)],plane(2)])
  self.assertFalse(lower_endpoint(n,(1,2,0))['qualified'])
 def test_exact_zero_projected_walls(self):
  d=probe();self.assertTrue(d['actualZeroProjectedWallAndNativeExclusion']);self.assertEqual(d['allActualNativeIndexExclusions'],[0,1])
 def test_whole_three_shared_edges(self):self.assertTrue(all(v['wholeFiniteRenderedSeamCovered']for v in probe()['allWholeActualCopiedAndInternalSeams'].values()))
 def test_lower_transition_preserves_core(self):self.assertTrue(probe()['completeClosedCoreMAXProof']['wholeOriginalClosedCoreMAXPreserved'])
 def test_inside_core_raised_transition_rejected(self):self.assertFalse(probe(q=(1,F(1,2)),outer=(1,100,-2))['completeClosedCoreMAXProof']['wholeOriginalClosedCoreMAXPreserved'])
 def test_complete_domain_rejection(self):self.assertFalse(probe(domain=[[(F(0),F(0)),(F(2),F(0)),(F(0),F(2))]])['completeClosedActualDomainProof']['wholeGeneratedClosedProjectionWithinDomain'])
 def test_actual_source_crossings_retained(self):
  source=[[(1,-1,-1),(1,3,-1),(1,1,1)]];wall=[[(0,0,0),(2,0,0),(0,2,0)]];d=contacts(source,wall)
  self.assertTrue(any(r['properNoncoplanarInteriorSegment']for r in d['allFiniteOriginalGeneratedContacts']))
 def test_missing_endpoint_no_geometry_emission(self):
  d=probe([plane(2)]);self.assertFalse(d['localFeasibility']);self.assertNotIn('allComputeOnlyLiteralFacets',d)
 def test_no_acceptance_from_pass(self):
  d=probe();self.assertTrue(d['localFeasibility']);self.assertTrue(d['noCandidate']and d['allNewContactsAndUnpairedTerminationsStillUnqualified'])
if __name__=='__main__':unittest.main()
