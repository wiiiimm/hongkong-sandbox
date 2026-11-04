"""Actual source-placement roles and adverse changes to their full evidence."""
import copy,unittest
import numpy as np
from run import ROOT,read,digest
import elements11_named_original_visual_placement_proposal_v1_20261011 as k
from test_elements24_named_original_mounted_visual_surface_proposal_v1_20261011 import actual_fixture as source_fixture
BASE=ROOT/'docs/astra-city/government-import'

def actual_fixture():
 docs,packages=source_fixture();worlds=next(iter(packages.values()))['worlds']
 path=BASE/k.CONTEXT_BATCH/'diagnostic.json.gz';assert digest(path.read_bytes())==k.CONTEXT_DIAGNOSTIC_SHA
 contexts=read(path)['complete11OriginalImageContexts'];graph=docs['graph']
 paths=read(BASE/'xl-terrain-recovery-20261011-elements-bounded-owned-four-stream-path-replay-v1/diagnostic.json.gz')
 qualified=set(next(r for r in paths['rows']if r['mode']=='providerOriginal')['qualifiedDiagnosticOwnedBodies']);assert len(qualified)==866
 result={}
 for c in contexts:
  uid=c['actorUID'];hosts=sorted(f for b in qualified if graph['components'][b]['actorUID']==uid for f in graph['components'][b]['globalOriginalFaces'])
  image=ROOT/c['contextImage']['path'];assert digest(image.read_bytes())==c['contextImage']['sha256']
  result[c['originalBody']]=dict(part=c['originalBody'],uid=uid,source_sha=k.SOURCE_SHA[uid],worlds=worlds,context=c,qualified_nonvisual_faces=hosts)
 return docs,result

class ActualSourceVisualPlacementTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.docs,cls.parts=actual_fixture()
 def run_part(self,p,**change):
  args=self.parts[p].copy();args.update(change);return k.verify(**args)
 def reject_context(self,p,mutate):
  c=copy.deepcopy(self.parts[p]['context']);mutate(c)
  with self.assertRaises(AssertionError):self.run_part(p,context=c)
 def test_all11_complete_actual_source_and_four_arithmetic_modes(self):
  out=[self.run_part(p)for p in k.PINS];self.assertEqual(sum(len(r['completeOriginalFaces'])for r in out),2389)
  for r in out:
   self.assertEqual(len(r['allFourStreamCompleteProofs']),4);self.assertTrue(r['conditionalSourceVisualRoleProposal']);self.assertFalse(r['finiteMountingCertified']);self.assertFalse(r['structuralRootCredit']);self.assertFalse(r['structuralBridgeCredit']);self.assertFalse(r['currentAcceptance']);self.assertFalse(r['sourceFunctionInferred']);self.assertFalse(r['reciprocalRoofCoverCertified'])
 def test_source_geometry_translation_cannot_be_rebound_as_same_role(self):
  worlds=self.parts[705]['worlds'].copy();worlds['providerOriginal']=worlds['providerOriginal'].copy();worlds['providerOriginal'][12520:12524]+=np.array([12.,0.,0.])
  with self.assertRaises(AssertionError):self.run_part(705,worlds=worlds)
 def test_literal_only_detachment_retains_original_source_but_rejects(self):
  worlds=self.parts[921]['worlds'].copy();worlds['actualLiteral']=worlds['actualLiteral'].copy();worlds['actualLiteral'][22077,0,0]+=.125
  with self.assertRaises(AssertionError):self.run_part(921,worlds=worlds)
 def test_f32_only_pose_change_rejects(self):
  worlds=self.parts[839]['worlds'].copy();worlds['explicitBalancedFloat32']=worlds['explicitBalancedFloat32'].copy();worlds['explicitBalancedFloat32'][15128,0,1]+=.25
  with self.assertRaises(AssertionError):self.run_part(839,worlds=worlds)
 def test_winding_reversal_with_same_bounding_box_is_not_original(self):
  worlds=self.parts[69]['worlds'].copy();worlds['providerOriginal']=worlds['providerOriginal'].copy();worlds['providerOriginal'][2153]=worlds['providerOriginal'][2153,::-1]
  with self.assertRaises(AssertionError):self.run_part(69,worlds=worlds)
 def test_deleted_complete_source_facet_rejects(self):self.reject_context(893,lambda c:c['completeOriginalFaces'].pop())
 def test_changed_current_ground_failure_is_not_visual_exemption(self):self.reject_context(902,lambda c:c['allFourStreamCompleteFiniteFindings'][1]['completePartFiniteFindings'][0].update(strictlyExposedWholeFacet=False))
 def test_incomplete_current_finite_coverage_rejects(self):self.reject_context(75,lambda c:c['allFourStreamCompleteFiniteFindings'][0]['completePartFiniteFindings'][0].update(closedProjectionCovered=False))
 def test_cropped_or_unrelated_context_cannot_replace_reviewed_source(self):self.reject_context(705,lambda c:c.update(completeWideContextOriginalFaces=[12520]))
 def test_distant_backing_negative_cannot_be_relabelled_mount(self):self.reject_context(78,lambda c:c.update(allPriorIntrinsicFindingsVerbatim=[]))
 def test_false_equipment_function_or_source_role_not_added(self):
  with self.assertRaises(AssertionError):self.run_part(839,part=838)
  self.reject_context(839,lambda c:c.update(sourceFunctionInferred=True))
 def test_visual_cycle_cannot_substitute_qualified_nonvisual_context(self):
  hosts=self.parts[897]['qualified_nonvisual_faces'].copy();hosts[0]=16218;hosts=sorted(set(hosts))
  with self.assertRaises(AssertionError):self.run_part(897,qualified_nonvisual_faces=hosts)
 def test_foreign_actor_inventory_and_wrong_source_reject(self):
  with self.assertRaises(AssertionError):self.run_part(75,qualified_nonvisual_faces=self.parts[839]['qualified_nonvisual_faces'])
  with self.assertRaises(AssertionError):self.run_part(75,source_sha='0'*64)
 def test_missing_arithmetic_stream_rejects(self):
  worlds=self.parts[744]['worlds'].copy();worlds.pop('explicitLeftFloat32')
  with self.assertRaises(AssertionError):self.run_part(744,worlds=worlds)
 def test_image_hash_or_full_current_actor_context_mutation_rejects(self):
  self.reject_context(76,lambda c:c['contextImage'].update(sha256='0'*64))
  self.reject_context(76,lambda c:c['completeActorContextOriginalFaces'].pop())
if __name__=='__main__':unittest.main()
