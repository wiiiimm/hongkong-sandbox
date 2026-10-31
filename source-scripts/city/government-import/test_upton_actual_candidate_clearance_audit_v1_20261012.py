"""Unexecuted adverse accounting fixtures; no captures, DB or approval writes."""
import unittest,copy
import numpy as np
from upton_actual_candidate_clearance_audit_v1_20261012 import candidate_surface,verify_drawn_multiset,measured_projection,reuse_key,compare_candidate
from upton_parent_tin_regression_bookkeeping_v1_20261012 import sha
class Tests(unittest.TestCase):
 def fixture(self,faces):
  a=np.asarray(faces,float);p={'w':2,'h':2,'elev':[0]*4,'renderedElev':[0]*4,'meta':{'georef':{'bE':834500,'bN':816500,'aE':1,'aN':-1}},'nativeMesh':{'position':a.reshape(-1).tolist(),'index':list(range(a.size//3)),'source':{}}};q=[dict(candidateFace=i,kind='originalTIN',rawNominationFaceSHA256=sha(f))for i,f in enumerate(a)];return p,q
 def ground(self):return [[[0,0,0],[0,0,1],[1,0,0]],[[1,0,0],[0,0,1],[1,0,1]]]
 def test_duplicate_positive_area_is_measured_not_approved(self):
  p,q=self.fixture(self.ground()+self.ground()[:1]);q[2]['kind']='capturedCurrentRing';r=measured_projection(p,q,[0,0,1,1],p);self.assertEqual(r['nativeProjectedExcessM2'],.5);self.assertTrue(r['noOverlapApprovalGranted']);self.assertNotIn('sourceOverlap',p['nativeMesh']);self.assertEqual(r['pairsBySavedProvenanceKinds']['capturedCurrentRing|originalTIN']['areaPairs'],1)
 def test_shared_edge_is_line_not_area_overlap(self):
  p,q=self.fixture(self.ground());r=measured_projection(p,q,[0,0,1,1],p);self.assertEqual(r['nativeProjectedExcessM2'],0);self.assertEqual(r['allProjectedIntersectingPairs'][0]['projectedDimension'],'line')
 def test_vertical_and_zero_facets_remain_inventory(self):
  p,q=self.fixture(self.ground()+[[[0,0,0],[0,1,0],[0,1,1]],[[0,0,0]]*3]);r=measured_projection(p,q,[0,0,1,1],p);self.assertEqual(r['allOtherDrawnFacetsRetainedButNotHeightCoverageFaces'],[2,3])
 def test_height_disagreement_not_hidden_by_same_projection(self):
  a=self.ground()+[[[0,2,0],[0,2,1],[1,2,0]]];p,q=self.fixture(a);r=measured_projection(p,q,[0,0,1,1],p);self.assertEqual(r['float32HighestRayAgreement']['rows'][0]['highestSamplerHeight'],2);self.assertTrue(any(x.get('representativePointHeightMeasurements',{}).get('signedLeftMinusRightM')==-2 for x in r['allProjectedIntersectingPairs']))
 def test_parent_edge_gap_preserved(self):
  p,q=self.fixture(np.asarray(self.ground())+[0,1,0]);r=measured_projection(p,q,[0,0,1,1],p);self.assertEqual(r['parentEdgeMaximumGap'],1)
 def test_actual_winding_permutation_preserves_multiset(self):
  a=np.asarray(self.ground());self.assertTrue(verify_drawn_multiset(a,a[:,[0,2,1]])['candidateMultisetIncludedWithMultiplicity'])
 def test_missing_duplicate_is_rejected(self):
  a=np.asarray(self.ground());
  with self.assertRaises(AssertionError):verify_drawn_multiset(np.concatenate([a,a[:1]]),a)
 def test_changed_drawn_height_is_rejected(self):
  a=np.asarray(self.ground());
  with self.assertRaises(AssertionError):verify_drawn_multiset(a,a+[0,.001,0])
 def test_wrong_provenance_is_rejected(self):
  p,q=self.fixture(self.ground());q[0]['candidateFace']=1
  with self.assertRaises(AssertionError):candidate_surface(p,q)
 def test_stale_approval_is_rejected(self):
  p,q=self.fixture(self.ground());p['nativeMesh']['sourceOverlap']={'policy':'highest-native-surface'}
  with self.assertRaises(AssertionError):candidate_surface(p,q)
 def test_reuse_tuple_requires_whole_face_and_ground(self):
  a=np.asarray(self.ground());self.assertNotEqual(reuse_key(a[0],a),reuse_key(a[0],a+[0,.001,0]));self.assertNotEqual(reuse_key(a[0],a),reuse_key(a[1],a))
 def test_new_negative_inside_domain_is_regression(self):
  a=dict(sourceFaceSHA256='same',ordinaryBoundProved=True,projectionCovered=True,exactLowerM='0');b={**a,'ordinaryBoundProved':False,'projectionCovered':False,'exactLowerM':None};r=compare_candidate(a,b,True);self.assertTrue(r['currentClearCandidateUnproved']);self.assertFalse(r['candidateCoverageUnprovedOutsideCapturedDomainIsExtractionLimit'])
 def test_old_outside_extraction_failure_not_runtime_hole(self):
  a=dict(sourceFaceSHA256='same',ordinaryBoundProved=False,projectionCovered=False,exactLowerM=None);r=compare_candidate(a,a,False);self.assertTrue(r['candidateCoverageUnprovedOutsideCapturedDomainIsExtractionLimit']);self.assertFalse(r['currentClearCandidateUnproved'])
if __name__=='__main__':unittest.main()
