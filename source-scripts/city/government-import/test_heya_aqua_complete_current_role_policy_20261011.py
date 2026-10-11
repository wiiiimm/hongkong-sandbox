"""Thirty hermetic actual-capture adverse cases; production replay is separate."""
import copy,unittest
import numpy as np
from heya_aqua_complete_current_role_fixture_20261011 import load
from heya_aqua_complete_current_role_policy_20261011 import compose,T,P
from heya_aqua_original_lower_assembly_join_20261011 import verify as join
class CompleteOriginalAccount(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=load()
 def bad(self,change):
  d=copy.deepcopy(self.data);change(d)
  with self.assertRaises((AssertionError,KeyError,StopIteration)):compose(**d)
 def test_actual_complete_four_world_account(self):
  r=compose(**self.data);self.assertTrue(r['stagingReady']);self.assertFalse(r['installationApproved'])
  self.assertEqual([r['completeProperCrossingsRetained']for r in r['completeSourceOwnedLowerAssemblyJoin']['rows']],[85]*4)
  self.assertEqual(r['completeTypedOriginalRoleAccount']['completeNonstructuralTerminalVisualComponents'],58)
 def test_source_byte_tamper(self):self.bad(lambda d:d['actual'][T].update(sourceSHA256='0'*64))
 def test_changed_literal_vertex(self):
  self.bad(lambda d:d['actual'][T]['completeWorldStreams']['actualLiteral']['completeWorldTriangles'][0][0].__setitem__(0,np.nextafter(d['actual'][T]['completeWorldStreams']['actualLiteral']['completeWorldTriangles'][0][0][0],np.inf)))
 def test_changed_ground(self):self.bad(lambda d:d['actual'][P]['completeDrawnGround'][0][0].__setitem__(1,100.))
 def test_finite_missing_face(self):self.bad(lambda d:d['finite']['rows'][0]['completeOriginalFaceComparisons'].pop())
 def test_finite_false_positive(self):self.bad(lambda d:d['finite']['rows'][0]['completeOriginalFaceComparisons'][0]['currentDrawnGroundComparison'].update(completeFiniteOrdinaryBoundProved=False))
 def test_visual_root_credit(self):self.bad(lambda d:d['visual'].update(structuralRootCredit=True))
 def test_visual_missing_component(self):self.bad(lambda d:d['visual']['completeNamedTerminalComponents'].pop())
 def test_engineering_claim(self):self.bad(lambda d:d['account'].update(engineeringSupportCertified=True))
 def test_podium_reapproval(self):self.bad(lambda d:d['account'].update(installedPodiumReapproved=True))
 def test_missing_attached_component(self):self.bad(lambda d:d['account']['rows'][0]['completeAttachedTowerComponents'].pop())
 def test_point_bridge(self):
  self.bad(lambda d:[c.update(dimension=0)for p in d['account']['rows'][0]['completeWithinTowerBoundsNominatedPairs']for c in p['completePrimitiveContactInventory']['contacts']])
 def test_parent_cycle(self):self.bad(lambda d:d['account']['rows'][0]['componentParentFromT4'].update({'0':0}))
 def test_missing_root_grade(self):self.bad(lambda d:d['interfaces']['rows'][0]['allGroundPrimitiveRecordsWithRealComponentBindings'].clear())
 def test_hidden_root_edge(self):self.bad(lambda d:d['account']['rows'][0]['originalExposedGradeToT4Path']['completeStrictSharedEdges'][0]['completeExposureProof'].update(strictlyExposedWholePositiveInterface=False))
 def test_identity_not_positive(self):self.bad(lambda d:d['identity'].update(passed=False))
 def test_unknown_physical_failure(self):self.bad(lambda d:d['physical']['ordinaryNumericReasons'].append('unknown'))
 def test_missing_runtime(self):self.bad(lambda d:d['physical'].update(runtimeChecksPassed=0))
 def test_basic_touch(self):self.bad(lambda d:d['foreign']['rows'][0]['fourStreamTrials'][0].update(strictCompleteClosedProjectionsDisjoint=False))
 def test_native_omission(self):self.bad(lambda d:d['native']['allSeparatedNativeActors'].pop())
 def test_native_touch(self):self.bad(lambda d:d['native']['allSeparatedNativeActors'][0]['completePairProofs'][0].update(exactPositiveGapM='0'))
 def test_wrong_provider_parent(self):self.bad(lambda d:next(f for f in d['current_forms']if f['uid']==P).update(parent='unrelated'))
 def test_wrong_provider_csuid(self):self.bad(lambda d:next(f for f in d['current_forms']if f['uid']==P).update(buildingCSUID='bad'))
 def test_duplicate_current_form(self):self.bad(lambda d:d['current_forms'].append(d['current_forms'][0]))
 def test_wrong_provider_native_source(self):self.bad(lambda d:next(r for r in d['provider_sources']if r['uid']==T)['native'].update(resultSha='0'*64))
 def test_missing_join_contact(self):self.bad(lambda d:d['native']['completeCoupledOriginalPrimitiveContext'][0]['completeTowerPodiumPrimitiveClassifications'].pop())
 def test_changed_join_face(self):self.bad(lambda d:d['native']['completeCoupledOriginalPrimitiveContext'][0]['completeTowerPodiumPrimitiveClassifications'][0]['contact'].update(sourceFaceA=0))
 def test_crossings_must_remain(self):self.bad(lambda d:d['native']['completeCoupledOriginalPrimitiveContext'][0].update(properTriangleInteriorCrossings=[]))
 def test_context_affected_face_omission(self):self.bad(lambda d:d['context']['rows'][0]['completeAffectedSourceFaceIds'][T].pop())
 def test_stale_current_manifest(self):self.bad(lambda d:d['native']['currentManifest'].update(sha256='0'*64))
if __name__=='__main__':unittest.main()
