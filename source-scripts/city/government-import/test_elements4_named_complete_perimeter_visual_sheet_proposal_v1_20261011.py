"""Actual full-source fixtures and adverse perimeter/host/current bindings."""
import copy,unittest
import numpy as np
import elements4_named_complete_perimeter_visual_sheet_proposal_v1_20261011 as k
from test_elements24_named_original_mounted_visual_surface_proposal_v1_20261011 import actual_fixture as prior_fixture

def actual_fixture():
 docs,prior=prior_fixture();worlds=next(iter(prior.values()))['worlds'];packages={}
 for part,faces in k.NAMED_SOURCE_PART_FACES.items():
  uid='landsd/204145:0'if max(faces)<12129 else'landsd/204143:0';offset=0 if uid=='landsd/204145:0'else 12129
  assert sorted(docs['graph']['components'][part]['globalOriginalFaces'])==faces
  contexts={};hosts={}
  for mode in k.MODES:
   row=next(r for r in docs['bands']['rows']if r['mode']==mode)
   a=next(a for a in row['all132OriginalBodyAssociations']if a['originalBody']==part)
   finite=next(r for r in docs['finite']['rows']if r['mode']==mode and r['uid']==uid)
   assert k.world_sha(worlds[mode])==row['completeWorldSHA256']
   assert k.world_sha(worlds[mode][:12129]if offset==0 else worlds[mode][12129:])==finite['completeWorldSHA256']
   contexts[mode]=dict(completeOwnedWorldSHA256=row['completeWorldSHA256'],association=a,
    allCompletePartFiniteFaces=[finite['allFaces'][f-offset]for f in faces])
   hosts[mode]=a['completeHostSelection']['completeQualifiedSameActorHostFaces']
  packages[part]=dict(part=part,uid=uid,source_sha=k.SOURCE_SHA[uid],worlds=worlds,
   contexts=contexts,qualified_hosts=hosts,
   expected_binding=k.binding(part,uid,k.SOURCE_SHA[uid],worlds,contexts,hosts))
 return docs,packages

class CompletePerimeterVisualSheetTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.docs,cls.packages=actual_fixture()
 def changed(self,part=70):
  p=self.packages[part].copy();p['contexts']=copy.deepcopy(p['contexts']);p['qualified_hosts']=copy.deepcopy(p['qualified_hosts']);return p
 def rebind(self,p):p['expected_binding']=k.binding(p['part'],p['uid'],p['source_sha'],p['worlds'],p['contexts'],p['qualified_hosts'])
 def test_all_four_actual_parts_and_arithmetic_modes(self):
  for part in k.NAMED_SOURCE_PART_FACES:
   with self.subTest(part=part):
    r=k.verify(**self.packages[part]);self.assertEqual(len(r['allFourStreamProofs']),4)
    self.assertTrue(r['conditionalSourceVisualRoleProposal']);self.assertFalse(r['structuralRootCredit']);self.assertFalse(r['structuralBridgeCredit'])
    self.assertFalse(r['originalOpeningOrHoleCertified']);self.assertFalse(r['currentAcceptance'])
    self.assertTrue(any(not p['wholeInteriorBandPositive']for p in r['allFourStreamProofs']))
 def test_partial_perimeter_cannot_be_called_complete_even_rebound(self):
  p=self.changed();p['contexts']['actualLiteral']['association']['allActualIncidenceOneBoundaryEdgeProofs'].pop();self.rebind(p)
  with self.assertRaises(AssertionError):k.verify(**p)
 def test_duplicate_edge_cannot_replace_missing_edge_even_rebound(self):
  p=self.changed();a=p['contexts']['actualLiteral']['association']['allActualIncidenceOneBoundaryEdgeProofs'];a[-1]=copy.deepcopy(a[0]);self.rebind(p)
  with self.assertRaises(AssertionError):k.verify(**p)
 def test_one_free_edge_cannot_replace_full_perimeter_even_rebound(self):
  p=self.changed();p['contexts']['actualLiteral']['association']['allActualIncidenceOneBoundaryEdgeProofs'][0]['wholeEdgeWithinExistingFiniteHostBand']=False;self.rebind(p)
  with self.assertRaises(AssertionError):k.verify(**p)
 def test_source_face_removal_rejects_even_rebound(self):
  p=self.changed();p['contexts']['providerOriginal']['association']['completeOriginalFaceIds'].pop();self.rebind(p)
  with self.assertRaises(AssertionError):k.verify(**p)
 def test_ground_coverage_failure_rejects_even_rebound(self):
  p=self.changed();p['contexts']['actualLiteral']['allCompletePartFiniteFaces'][0]['closedProjectionCovered']=False;self.rebind(p)
  with self.assertRaises(AssertionError):k.verify(**p)
 def test_current_strict_exposure_failure_rejects_even_rebound(self):
  p=self.changed();p['contexts']['actualLiteral']['allCompletePartFiniteFaces'][0]['strictlyExposedWholeFacet']=False;self.rebind(p)
  with self.assertRaises(AssertionError):k.verify(**p)
 def test_actual_host_detachment_rejects_forged_old_positive_booleans(self):
  p=self.changed();mode='actualLiteral';p['worlds']=p['worlds'].copy();p['worlds'][mode]=p['worlds'][mode].copy()
  c=p['contexts'][mode];hs=c['association']['completeHostSelection'];ids=hs['selectedGlobalHostFaces']
  p['worlds'][mode][ids]+=np.array([4.,4.,4.]);c['completeOwnedWorldSHA256']=k.world_sha(p['worlds'][mode]);hs['actualSelectedHostWorldSHA256']=k.world_sha(p['worlds'][mode][sorted(ids)]);self.rebind(p)
  with self.assertRaises(AssertionError):k.verify(**p)
 def test_foreign_actor_host_rejects_even_rebound(self):
  p=self.changed(890);mode='actualLiteral';hs=p['contexts'][mode]['association']['completeHostSelection'];hs['selectedGlobalHostFaces']=[0]
  p['qualified_hosts'][mode]=[0];hs['completeQualifiedSameActorHostFaces']=[0];hs['actualSelectedHostWorldSHA256']=k.world_sha(p['worlds'][mode][[0]]);self.rebind(p)
  with self.assertRaises(AssertionError):k.verify(**p)
 def test_self_host_visual_bootstrap_rejects_even_rebound(self):
  p=self.changed();mode='actualLiteral';ids=k.NAMED_SOURCE_PART_FACES[70];hs=p['contexts'][mode]['association']['completeHostSelection']
  hs['selectedGlobalHostFaces']=ids;p['qualified_hosts'][mode]=ids;hs['completeQualifiedSameActorHostFaces']=ids;hs['actualSelectedHostWorldSHA256']=k.world_sha(p['worlds'][mode][ids]);self.rebind(p)
  with self.assertRaises(AssertionError):k.verify(**p)
 def test_stale_pose_binding_rejects(self):
  p=self.changed();p['worlds']=p['worlds'].copy();p['worlds']['actualLiteral']=p['worlds']['actualLiteral'].copy();p['worlds']['actualLiteral'][2336,0,0]+=.2
  with self.assertRaises(AssertionError):k.verify(**p)
 def test_unqualified_host_flag_rejects_even_rebound(self):
  p=self.changed();p['contexts']['actualLiteral']['association']['completeHostSelection']['allSelectedHostsBelongToNonvisualQualifiedPaths']=False;self.rebind(p)
  with self.assertRaises(AssertionError):k.verify(**p)
 def test_wrong_source_actor_or_arithmetic_inventory_rejects(self):
  for changed in [dict(source_sha='0'*64),dict(uid='landsd/204143:0')]:
   p=self.packages[70].copy();p.update(changed)
   with self.assertRaises(AssertionError):k.verify(**p)
  p=self.packages[70].copy();p['worlds']=p['worlds'].copy();p['worlds'].pop('explicitBalancedFloat32')
  with self.assertRaises(AssertionError):k.verify(**p)

if __name__=='__main__':unittest.main()
