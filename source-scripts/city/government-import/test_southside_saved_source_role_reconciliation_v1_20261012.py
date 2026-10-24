"""Actual saved Southside baselines + adverse provenance/positive-edge cases."""
import unittest,json,gzip,copy,math
from pathlib import Path
from southside_saved_source_role_reconciliation_v1_20261012 import certify_original_subsegment,reconcile,canonical
R=Path(__file__).resolve().parents[3];D=R/'docs/astra-city/government-import/government-xl-southside-source-role-reconciliation-draft-v1-20261012'
class SavedEdges(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.fixtures=json.loads((D/'actual-saved-edge-fixtures.json').read_text())['fixtures']
 def certify(self,i,mutate=None):
  f=copy.deepcopy(self.fixtures[i]);
  if mutate:mutate(f)
  return certify_original_subsegment(f['edge'],f['proof'],expected_saved_proof_sha256=self.fixtures[i]['proofCanonicalSHA256'])
 def test_actual_strict_whole_1036(self):self.assertIsNotNone(self.certify(0))
 def test_actual_diagonal_1037(self):self.assertIsNotNone(self.certify(1))
 def test_actual_low_ceiling_5276(self):self.assertIsNotNone(self.certify(2))
 def test_actual_paired_5289(self):self.assertIsNotNone(self.certify(3))
 def test_actual_diagonal_5312(self):self.assertIsNotNone(self.certify(4))
 def test_changed_edge(self):
  with self.assertRaises(AssertionError):self.certify(1,lambda f:f['edge'][0].__setitem__(0,math.nextafter(f['edge'][0][0],math.inf)))
 def test_collapsed_edge(self):
  with self.assertRaises(AssertionError):self.certify(1,lambda f:f['edge'].__setitem__(1,f['edge'][0]))
 def test_changed_ground(self):
  with self.assertRaises(AssertionError):self.certify(1,lambda f:f['proof']['coarse'].__setitem__('completeCurrentGroundSHA256','0'*64))
 def test_false_coverage(self):
  with self.assertRaises(AssertionError):self.certify(1,lambda f:f['proof']['coarse'].__setitem__('groundProjectionCovered',False))
 def test_changed_height_ceiling(self):
  with self.assertRaises(AssertionError):self.certify(1,lambda f:f['proof']['coarse'].__setitem__('exactMaximumAllCandidateOriginalGroundHeightM','0'))
 def test_omitted_paired_piece(self):
  with self.assertRaises(AssertionError):self.certify(2,lambda f:f['proof']['paired']['allExactFiniteSourceGroundPieces'].pop())
 def test_changed_affine_gap(self):
  with self.assertRaises(AssertionError):self.certify(2,lambda f:f['proof']['paired']['allExactFiniteSourceGroundPieces'][0]['allExactSourcePrismIntersectionVertices'][0].__setitem__('exactGapM','1000000'))
 def test_foreign_source_sha(self):
  with self.assertRaises(AssertionError):self.certify(2,lambda f:f['proof']['coarse'].__setitem__('sourceFaceSHA256','0'*64))
 def test_wrong_proof_pin(self):
  f=self.fixtures[0]
  with self.assertRaises(AssertionError):certify_original_subsegment(f['edge'],f['proof'],expected_saved_proof_sha256='0'*64)
 def test_reverse_without_arithmetic_binding(self):
  with self.assertRaises(AssertionError):self.certify(0,lambda f:f['edge'].reverse())
class WholeAccount(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.binding=json.loads((D/'input-contract.json').read_text());paths=cls.binding['filePins'];cls.review=json.loads(gzip.decompress((R/paths[0]['path']).read_bytes()));cls.grade=json.loads(gzip.decompress((R/paths[1]['path']).read_bytes()))
 def baseline(self,review=None,grade=None):return reconcile(self.review if review is None else review,self.grade if grade is None else grade,expected_review_sha256=self.binding['reviewCanonicalSHA256'],expected_grade_sha256=self.binding['gradeCanonicalSHA256'])
 def reject(self,key,value):
  r=dict(self.review);r[key]=value
  with self.assertRaises(AssertionError):self.baseline(review=r)
 def test_actual_complete19_baseline(self):
  result=self.baseline();self.assertEqual(len(result['complete19SourceSpecificRouteProposals']),19);self.assertFalse(result['currentAcceptance']);self.assertTrue(result['terminalVisualsNeverRootOrBridge'])
 def test_source_role_approval_injected(self):self.reject('sourceRoleAccepted',True)
 def test_current_acceptance_injected(self):self.reject('currentAcceptance',True)
 def test_physical_acceptance_injected(self):self.reject('physicalAccepted',True)
 def test_part_omission(self):self.reject('complete19SourceRoleAndHostObligations',self.review['complete19SourceRoleAndHostObligations'][:-1])
 def test_duplicate_part(self):self.reject('complete19SourceRoleAndHostObligations',[self.review['complete19SourceRoleAndHostObligations'][0]]*19)
 def test_component_map_omission(self):self.reject('completeBodyObligationMapping',self.review['completeBodyObligationMapping'][:-1])
 def test_target_failure_omission(self):self.reject('targetFacetRecords',self.review['targetFacetRecords'][:-1])
 def test_geometry_change(self):self.reject('sourceGeometryChanges',1)
 def test_historical_mount_rewritten(self):
  roles=list(self.review['complete19SourceRoleAndHostObligations']);r=dict(roles[0]);r['historicalCoordinateBandNegativeVerbatim']={};roles[0]=r;self.reject('complete19SourceRoleAndHostObligations',roles)
 def test_mode_omission(self):
  g=dict(self.grade);g['rows']=g['rows'][:-1]
  with self.assertRaises(AssertionError):self.baseline(grade=g)
if __name__=='__main__':unittest.main()
