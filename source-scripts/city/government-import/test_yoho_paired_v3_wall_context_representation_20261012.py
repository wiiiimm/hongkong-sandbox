"""Unexecuted actual saved-prefix adapter tests, no clearance rerun."""
import copy,unittest
import numpy as np
from run import ROOT,HERE,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from yoho_paired_v3_wall_context_representation_20261012 import for_context,canonical

class ActualSavedYohoPairedProof(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  base=ROOT/'docs/astra-city/government-import';batch='xl-terrain-recovery-20261012-yoho-source-holes-preserved-routing-main955-wall-cap-v1'
  prefix=read(HERE/'local'/batch/'providerOriginal-finite-progress.json.gz')
  routed=read(base/batch/'source-hole-routing-diagnostic.json.gz');cls.ground=np.asarray(routed['proposedDiagnosticGround'],float)
  row=read(base/'xl-terrain-recovery-20261012-yoho-eight-original-pair-current-capture-v1/selection.json.gz')['rows'][1]
  world=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes())
  assert digest(world[prefix['main955OriginalIDs']].tobytes())==prefix['worldSHA256']and digest(cls.ground.tobytes())==prefix['groundSHA256']
  cls.row=next(r for r in prefix['rows']if r['pairedExactOriginalFiniteBound']is not None);cls.face=world[cls.row['actorLocalOriginalFace']];cls.originalSHA=canonical(cls.row)
 def test_actual_proof_retained_and_original_unmodified(self):
  out=for_context(self.row,self.face,self.ground);p=out['pairedExactOriginalFiniteBound'];old=self.row['pairedExactOriginalFiniteBound']
  self.assertEqual(p['completePairedV3ProofVerbatim'],old);self.assertEqual(p['allProjectedBoundingCandidateOriginalGroundFacets'],old['sameConstraintOptimizedOrdinaryPrismProof']['allProjectedBoundingCandidateOriginalGroundFacets']);self.assertEqual(canonical(self.row),self.originalSHA)
 def test_changed_ground_bytes_rejected(self):
  g=self.ground.copy();g[0,0,1]+=1
  with self.assertRaises(AssertionError):for_context(self.row,self.face,g)
 def test_changed_source_pose_rejected(self):
  f=self.face.copy();f[0,0]+=1
  with self.assertRaises(AssertionError):for_context(self.row,f,self.ground)
 def test_missing_nested_candidate_rejected(self):
  r=copy.deepcopy(self.row);r['pairedExactOriginalFiniteBound']['sameConstraintOptimizedOrdinaryPrismProof']['allProjectedBoundingCandidateOriginalGroundFacets'].pop()
  with self.assertRaises(AssertionError):for_context(r,self.face,self.ground)
 def test_coarse_closed_candidate_mismatch_rejected(self):
  r=copy.deepcopy(self.row);r['priorCoarseBoundProofVerbatim']['completeOriginal']['allProjectedBoundingCandidateOriginalGroundFacets'].pop()
  with self.assertRaises(AssertionError):for_context(r,self.face,self.ground)
 def test_nested_geometry_binding_mismatch_rejected(self):
  r=copy.deepcopy(self.row);r['pairedExactOriginalFiniteBound']['sameConstraintOptimizedOrdinaryPrismProof']['completeCurrentGroundSHA256']='0'*64
  with self.assertRaises(AssertionError):for_context(r,self.face,self.ground)
 def test_bound_credit_inconsistent_with_saved_proof_rejected(self):
  r=copy.deepcopy(self.row);r['completeOriginalBoundProved']=not r['completeOriginalBoundProved']
  with self.assertRaises(AssertionError):for_context(r,self.face,self.ground)

if __name__=='__main__':unittest.main()
