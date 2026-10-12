"""Unexecuted actual-incidence and contract counterexamples; no new admission rule."""
import unittest
from fractions import Fraction as F
import numpy as np
from upton_actual_ruling_reconciliation_v1_20261012 import prepare,incidence,reconcile,full_draw_attribution,saved_change_contract,broadphase
def triangle():return np.array([[0,0,0],[2,0,0],[0,0,2]],float)
class Tests(unittest.TestCase):
 def test_interior_is_virtual_not_missing_seam(self):
  q=incidence([[.2,0,.2],[.8,0,.2]],prepare([triangle()]));self.assertTrue(q['completeExactSurfaceCoverage']);self.assertEqual(q['allOpenIntervalIncidenceClasses'][0]['classification'],'strictInteriorOfSurvivingFacet')
 def test_one_sided_exterior_is_normal(self):
  q=incidence([[0,0,0],[2,0,0]],prepare([triangle()]));self.assertEqual(q['allOpenIntervalIncidenceClasses'][0]['classification'],'ordinaryOneSidedExteriorEdgeIncidence');self.assertTrue(q['oneSidedExteriorEdgesAreNormal']and q['noTopologyAdmissionGate'])
 def test_coplanar_opposite_sides_internal(self):
  a=triangle();b=a.copy();b[2,2]=-2;q=incidence([[0,0,0],[2,0,0]],prepare([a,b]));self.assertEqual(q['allOpenIntervalIncidenceClasses'][0]['classification'],'coplanarTwoSidedInternalIncidence')
 def test_opposite_winding_duplicate_not_two_sided(self):
  a=triangle();q=incidence([[0,0,0],[2,0,0]],prepare([a,a[::-1]]));self.assertEqual(q['allOpenIntervalIncidenceClasses'][0]['classification'],'ordinaryOneSidedExteriorEdgeIncidence');self.assertEqual(len(q['allOpenIntervalIncidenceClasses'][0]['allActualIncidentFaceIDs']),2)
 def test_nonplanar_surviving_crease(self):
  a=triangle();b=np.array([[0,0,0],[2,0,0],[0,2,0]],float);q=incidence([[0,0,0],[2,0,0]],prepare([a,b]));self.assertEqual(q['allOpenIntervalIncidenceClasses'][0]['classification'],'sharedNoncoplanarCreaseIncidence')
 def test_partial_tjunction_is_interval_accounted(self):
  a=triangle();b=np.array([[0,0,0],[1,0,0],[0,0,-1]],float);q=incidence([[0,0,0],[2,0,0]],prepare([a,b]));self.assertEqual([x['classification']for x in q['allOpenIntervalIncidenceClasses']],['coplanarTwoSidedInternalIncidence','ordinaryOneSidedExteriorEdgeIncidence'])
 def test_point_contact_does_not_cover_segment(self):
  q=incidence([[-1,0,0],[0,0,0]],prepare([triangle()]));self.assertFalse(q['completeExactSurfaceCoverage']);self.assertEqual(q['allClosedBreakpointIncidences'][-1]['allActualIncidentFaceIDs'],[0])
 def test_missing_middle_is_preserved(self):
  a=triangle()*.25;b=a+[1.5,0,0];q=incidence([[0,0,0],[2,0,0]],prepare([a,b]));self.assertFalse(q['completeExactSurfaceCoverage']);self.assertIn('noExactFacetOnNominalTrace',[x['classification']for x in q['allOpenIntervalIncidenceClasses']])
 def test_degenerate_is_not_target(self):
  p=prepare(np.zeros((1,3,3)));q=incidence([[0,0,0],[1,0,0]],p);self.assertEqual(p['exactDegenerateFaceIDs'],[0]);self.assertFalse(q['completeExactSurfaceCoverage'])
 def test_displaced_packing_is_not_permanent_hold(self):
  q=reconcile([[0,.00001,0],[1,.00001,0]],prepare([triangle()]));self.assertFalse(q['completeActualIncidence']['completeExactSurfaceCoverage']);self.assertTrue(q['allSeparateDistanceDiagnostics']['distance01MSeparateDiagnostic']['completeFinite3DCorrespondence']);self.assertTrue(q['packingDisplacementDoesNotCreatePermanentHold'])
 def test_actual_fallback_included(self):
  a=triangle();b=a+[3,0,0];q=full_draw_attribution([a,b],[a],[{'kind':'originalTIN'}],[b],[{'globalCurrentFace':0}]);self.assertEqual(q['fallbackFaceIDs'],[1]);self.assertEqual(q['rows'][1]['allCurrentSourceIdentityAlternatives'],[{'globalCurrentFace':0}])
 def test_missing_candidate_occurrence_rejected(self):
  with self.assertRaises(AssertionError):full_draw_attribution([triangle()],[triangle(),triangle()],[{},{}],[triangle()],[{}])
 def test_unattributed_fallback_rejected(self):
  with self.assertRaises(AssertionError):full_draw_attribution([triangle(),triangle()+[3,0,0]],[triangle()],[{}],[triangle()],[{}])
 def test_duplicate_candidate_current_ambiguity_retained(self):
  a=triangle();q=full_draw_attribution([a,a],[a],[{}],[a,a],[{'id':1},{'id':2}]);self.assertEqual(len(q['rows'][1]['allCurrentSourceIdentityAlternatives']),2)
 def test_nonzero_existing_contract_not_zero_gate(self):
  r={'completeDrawnUnionIdealAffineMax':{'proof':{'completeIdealAffineMaxRegionCovered':True,'exactMaximumAbsoluteIdealAffineMaxDifferenceM':'1/10000000'}},'exactInheritance':{}};q=saved_change_contract(r);self.assertTrue(q['belowExistingSamplerAudit01MContract']and q['exactZeroIsNotAdmissionRequirement'])
 def test_existing_strict_01_not_widened(self):
  r={'completeDrawnUnionIdealAffineMax':{'proof':{'completeIdealAffineMaxRegionCovered':True,'exactMaximumAbsoluteIdealAffineMaxDifferenceM':str(F(.01))}},'exactInheritance':{}};self.assertFalse(saved_change_contract(r)['belowExistingSamplerAudit01MContract'])
 def test_rational_bounds_do_not_lose_cancellation(self):
  a=F(1,10)+F(1,10**20);q=broadphase([[a,0,0],[a,1,0]],np.array([[[-4e-18,0,0],[-4e-18,1,0],[-4e-18,0,1]]]),F(.1));self.assertEqual(q,[0])
 def test_nonfinite_world_rejected(self):
  with self.assertRaises(AssertionError):prepare([triangle()*np.nan])
 def test_collapsed_trace_uncredited(self):
  self.assertTrue(reconcile([[0,0,0],[0,0,0]],prepare([triangle()]))['collapsedNominationRetainedUncredited'])
if __name__=='__main__':unittest.main()
