"""Actual138 complete source placements and meaningful changed-evidence cases.

No distance queries; these test distinct placement/source/current bindings.
"""
import copy,unittest
import numpy as np
import twin138_named_original_source_placement_proposal_v1_20261011 as k
from twin138_source_placement_actual_fixture_v1_20261011 import actual_fixture
class ActualSourcePlacementTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.docs,cls.parts,cls.refs,cls.receipts=actual_fixture()
 def run_part(self,p=17,**changes):
  args=self.parts[p].copy();args.update(changes);return k.verify(**args)
 def reject_context(self,mutate,p=17):
  c=copy.deepcopy(self.parts[p]['context']);mutate(c)
  with self.assertRaises(AssertionError):self.run_part(p,context=c)
 def changed_world(self,mode,mutate):
  worlds=self.parts[17]['worlds'].copy();worlds[mode]=worlds[mode].copy();face=self.parts[17]['context']['completeOriginalFaces'][0];mutate(worlds[mode],face)
  with self.assertRaises(AssertionError):self.run_part(worlds=worlds)
 def test_all138_complete_actual_source_parts_four_streams_and1521_faces(self):
  out=[self.run_part(p)for p in sorted(self.parts)]
  self.assertEqual(len(out),138);self.assertEqual(sum(len(r['completeOriginalFaces'])for r in out),1521)
  for r in out:
   self.assertEqual(len(r['allFourStreamCompleteProofs']),4)
   self.assertTrue(r['sourceContextIsPlacementEvidenceNotMount']);self.assertTrue(r['visualPartsNeverQualifyHosts'])
   for field in ('finiteMountingCertified','wholeInteriorProximityCertified','originalOpeningOrFunctionCertified','structuralRootCredit','structuralBridgeCredit','nativeReacceptance','currentAcceptance'):self.assertFalse(r[field])
 def test_wrong_source_cannot_transfer_visual_interpretation(self):
  with self.assertRaises(AssertionError):self.run_part(source_sha='0'*64)
  with self.assertRaises(AssertionError):self.run_part(part=18)
 def test_partial_part_is_not_the_complete_source_surface(self):self.reject_context(lambda c:c['completeOriginalFaces'].pop())
 def test_original_translation_not_rebound_as_reviewed_context(self):self.changed_world('providerOriginal',lambda w,f:w.__setitem__(f,w[f]+[20.,0.,0.]))
 def test_winding_changed_at_same_bounds_is_not_original(self):self.changed_world('providerOriginal',lambda w,f:w.__setitem__(f,w[f,::-1]))
 def test_literal_only_detachment_does_not_inherit_source_placement(self):self.changed_world('capturedLiteral',lambda w,f:w.__setitem__((f,0,0),w[f,0,0]+.25))
 def test_one_float32_arithmetic_pose_changed_rejects(self):self.changed_world('explicitBalancedF32ModelMatrix',lambda w,f:w.__setitem__((f,0,1),w[f,0,1]+.25))
 def test_changed_ground_uncovered_projection_is_not_visual_exemption(self):self.reject_context(lambda c:c['allFourStreamCompleteFiniteFindings'][0]['completePartFiniteFindings'][0]['completeFacetContextVerbatim'].update(groundProjectionCovered=False))
 def test_changed_ordinary_bound_or_strict_exposure_rejects(self):
  self.reject_context(lambda c:c['allFourStreamCompleteFiniteFindings'][1]['completePartFiniteFindings'][0]['completeFiniteProofVerbatim'].update(completeOriginalBoundProved=False))
  self.reject_context(lambda c:c['allFourStreamCompleteFiniteFindings'][2]['completePartFiniteFindings'][0]['completeFacetContextVerbatim'].update(exactCertifiedLowerClearanceM='-1/100'))
 def test_cropped_or_unrelated_source_surroundings_rejects(self):
  self.reject_context(lambda c:c.update(completeWideContextOriginalFaces=c['completeOriginalFaces']))
  self.reject_context(lambda c:c['completeActorContextOriginalFaces'].pop())
 def test_mounting_and_free_edge_negatives_cannot_disappear(self):self.reject_context(lambda c:c.update(allPriorMountingAndFreeEdgeNegativesVerbatim=[]))
 def test_foreign_actor_context_not_a_qualified_visual_host(self):
  with self.assertRaises(AssertionError):self.run_part(qualified_nonvisual_faces=self.parts[1092]['qualified_nonvisual_faces'])
 def test_visual_to_visual_bootstrap_cannot_replace827_nonvisual_context(self):
  h=copy.deepcopy(self.parts[17]['qualified_nonvisual_faces']);h['providerOriginal'][0]=self.parts[86]['context']['completeOriginalFaces'][0];h['providerOriginal']=sorted(set(h['providerOriginal']))
  with self.assertRaises(AssertionError):self.run_part(qualified_nonvisual_faces=h)
 def test_missing_render_arithmetic_stream_rejects(self):
  w=self.parts[17]['worlds'].copy();w.pop('explicitLeftAssociatedF32ModelMatrix')
  with self.assertRaises(AssertionError):self.run_part(worlds=w)
 def test_actual_context_image_cannot_be_replaced(self):self.reject_context(lambda c:c['contextImages'][0].update(sha256='0'*64))
 def test_inferred_function_or_root_claim_cannot_be_added(self):
  self.reject_context(lambda c:c.update(sourceFunctionInferred=True))
  self.reject_context(lambda c:c.update(structuralRootOrBridgeCredit=True))
if __name__=='__main__':unittest.main()
