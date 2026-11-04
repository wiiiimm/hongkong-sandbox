"""Complete actual-source typed-account fixtures; no mocked production replay."""
import copy,unittest
import numpy as np
from run import ROOT,read
from evangel_college_whole_current_role_bound_20261011 import DOCS
from evangel_college_whole_current_role_policy_20261011 import compose
class WholeRole(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  docs={k:read(p/('proposal.json.gz'if k in {'standing','remaining'}else'diagnostic.json.gz'))for k,p in DOCS.items()if k not in {'source','identity','native_input'}}
  physical=DOCS['physical'];guards={k:read(physical/n)for k,n in dict(metrics='metrics.json',validation='validation.json',foundation='foundation.json',neighbours='neighbour-checks.json',native_checks='native-neighbour-checks.json').items()}
  runtime=read(ROOT/'source-scripts/city/government-import/local'/physical.name/'runtime-geometry.json.gz');ground=np.asarray(runtime['rows'][0]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
  cls.fixture=dict(data=read(DOCS['source']/'complete-four-stream-ground-inputs.json.gz'),ground=ground,identity=read(DOCS['identity']/'identity.json'),current_manifest=docs['physical']['currentManifest'],**docs,**guards)
 def reject(self,change):
  a=copy.deepcopy(self.fixture);change(a)
  with self.assertRaises((AssertionError,KeyError,ValueError,IndexError)):compose(**a)
 def test_actual_complete13960_four_stream_226_account(self):
  p=compose(**self.fixture);self.assertTrue(p['acceptanceReadyForStaging']);self.assertFalse(p['installationApproved']);self.assertEqual(len(p['completeFourWorldComposition']),4)
  for r in p['completeFourWorldComposition']:self.assertEqual(len(r['all132RawFiniteFailuresRetained']),132);self.assertEqual(len(r['all33OriginalZerosRetainedWithoutRootOrBridge']),33)
 def test_missing_complete_stream(self):self.reject(lambda a:a['data']['completeWorldStreams'].pop('actualLiteral'))
 def test_changed_original_source(self):self.reject(lambda a:a['data'].__setitem__('sourceSHA256','0'*64))
 def test_changed_actual_pose(self):self.reject(lambda a:a['data']['completeWorldStreams']['actualLiteral']['completeWorldTriangles'][0][0].__setitem__(1,123))
 def test_missing_whole_original_facet(self):self.reject(lambda a:a['finite']['rows'][0]['complete13960FaceComparisons'].pop())
 def test_missing_whole_real_component(self):self.reject(lambda a:a['graph']['rows'][0]['completeOriginalTopology']['sharedEdgeConnectedComponents'].pop())
 def test_zero_record_disappears(self):self.reject(lambda a:a['graph']['rows'][0]['completeOriginalTopology']['exactNonrenderingOriginalFaces'].pop())
 def test_ordinary_unknown_failure_not_erased(self):self.reject(lambda a:a['physical']['rawOrdinaryReasons'].append('unknown-current-failure'))
 def test_raw_failure_scope_not_erased(self):self.reject(lambda a:a['finite']['rows'][0]['complete13960FaceComparisons'][5137]['groundComparisons']['currentDrawn'].__setitem__('completeFiniteOrdinaryBoundProved',True))
 def test_changed_complete_actual_ground(self):self.reject(lambda a:a['ground'].__setitem__((0,0,1),99))
 def test_cap_proof_hidden(self):self.reject(lambda a:a['grade']['rows'][0]['strictCapPathDiagnostic']['paths'][0].__setitem__('hasExactOriginalStrictClearCapRoofPath',False))
 def test_wall_exposure_missing(self):self.reject(lambda a:a['grade']['rows'][0]['strictCapPathDiagnostic']['paths'][0].__setitem__('rawFaceExposurePositive',False))
 def test_grade_inventory_not_complete(self):self.reject(lambda a:a['grade']['rows'][0]['complete5297CurrentGradeContactInventory'].__setitem__('allPairsExamined',False))
 def test_points_do_not_root(self):
  def change(a):
   for c in a['grade']['rows'][0]['complete5297CurrentGradeContactInventory']['contacts']:c['dimension']=0
  self.reject(change)
 def test_buried_closure_not_source_bridge(self):self.reject(lambda a:a['grade']['rows'][0]['rawDownwardFacesRetainedAsUncredited'].remove(3854))
 def test_component_path_not_omitted(self):self.reject(lambda a:a['qualification']['rows'][0]['completeConditionalEnvelopeSourcePaths'].pop())
 def test_unqualified_envelope_body(self):self.reject(lambda a:a['qualification']['rows'][0]['unresolvedEnvelopeComponents'].append(13))
 def test_visual_never_roots(self):self.reject(lambda a:a['qualification']['rows'][0]['completeFiveVisualDispositions'][0].__setitem__('structuralRootCredit',True))
 def test_host_scope_not_omitted(self):self.reject(lambda a:a['qualification']['rows'][0]['completeConditionalHostFaceIds'].pop())
 def test_standing_proof_missing(self):self.reject(lambda a:a['standing']['rows'][0]['completeFourStandingSkinProofs'].pop())
 def test_standing_raw_footing_failure_retained(self):self.reject(lambda a:a['standing']['rows'][0]['completeFourStandingSkinProofs'][0]['rawOrdinaryWholeFootingVerbatim'].__setitem__('passed',True))
 def test_standing_does_not_transfer_support(self):self.reject(lambda a:a['standing']['rows'][0]['completeFourStandingSkinProofs'][0]['completeNamedStandingSkinProof'].__setitem__('supportTransferToOtherSourceBodies',True))
 def test_standing_no_engineering_claim(self):self.reject(lambda a:a['standing']['rows'][0]['completeFourStandingSkinProofs'][0]['completeNamedStandingSkinProof'].__setitem__('loadBearingClaim',True))
 def test_ordinary_body90_footing_needed(self):
  def change(a):next(r for r in a['qualification']['rows'][0]['completeFiveStandingDispositions']if r['originalComponent']==90)['completeOrdinaryFootingVerbatim']['passed']=False
  self.reject(change)
 def test_native_complete_count(self):self.reject(lambda a:a['native']['completeNativeActualBoundsCertificate'].__setitem__('completeForeignNativeActors',6644))
 def test_native_source_overlap(self):self.reject(lambda a:a['native']['completeNativeActualBoundsCertificate'].__setitem__('allFourOwnedByThreeActualNativeWorldBoundsStrictlyDisjoint',False))
 def test_native_changed_terrain_domain_overlap(self):self.reject(lambda a:a['domain']['terrainDomainNominatedActors'].append('landsd/123:0'))
 def test_basic_collision_obligation_not_omitted(self):self.reject(lambda a:a['foreign']['foreignActorsRequiringFullCollisionProof'].append('landsd/88878:0'))
 def test_neighbour_census_omission(self):self.reject(lambda a:a['neighbours']['rows'].pop())
 def test_neighbour_regression_not_waived(self):self.reject(lambda a:a['neighbours']['rows'][0]['reasons'].append('terrain-regression'))
 def test_runtime_exception_blocks(self):self.reject(lambda a:a['validation'].__setitem__('exceptions',1))
 def test_loader_rejection_blocks(self):self.reject(lambda a:a['validation'].__setitem__('loaderAccepted',0))
 def test_buried_upward_surface_not_named_base(self):self.reject(lambda a:a['foundation']['rows'][0]['foundation'].__setitem__('fullyBuriedUpwardTriangles',1))
 def test_identity_failure_blocks(self):self.reject(lambda a:a['identity'].__setitem__('passed',False))
 def test_stale_current_manifest(self):self.reject(lambda a:a['current_manifest'].__setitem__('sha256','0'*64))
 def test_changed_named_lower_proof(self):self.reject(lambda a:a['remaining']['rows'][0]['namedLowerSourceSkinProposal'].__setitem__('raw22FailureFacesProvideNoInterComponentRootOrBridge',False))
if __name__=='__main__':unittest.main()
