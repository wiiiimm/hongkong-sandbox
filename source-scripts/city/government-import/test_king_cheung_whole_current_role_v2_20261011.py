"""Hermetic actual-source counterexamples; separate production binder replays Neon."""
import unittest,copy
from run import read
from king_cheung_whole_current_role_bound_v2_20261011 import DOCS,MANIFEST_SHA
from king_cheung_whole_current_role_policy_v2_20261011 import compose,row_for
from king_cheung_named14_intrinsic_visual_placement_20261011 import verify,IMAGES,NAMED
class Actual(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.args={k:read(p/('proposal.json.gz'if k in ['foundation','canopy']else'diagnostic.json.gz'))for k,p in DOCS.items()if k not in ['identity','input']}
  cls.args.update(data=read(DOCS['input']/'complete-four-stream-ground-inputs.json.gz'),identity=read(DOCS['identity']/'identity.json'),current_manifest=dict(path='3d-viewer/city/data/manifest.json',sha256=MANIFEST_SHA))
 def test_actual_complete908_four_stream_composition(self):
  r=compose(**self.args);self.assertTrue(r['acceptanceReadyForStaging']);self.assertFalse(r['installationApproved'])
  for row in r['completeFourWorldComposition']:
   self.assertEqual(len(row['qualifiedAttachedEnvelopeComponents']),714);self.assertEqual(len(row['nonstructuralPerimeterQualifiedVisualComponents']),177);self.assertEqual(row['nonstructuralNamedPlacementVisualComponents'],NAMED)
 def altered(self,key,mutate):
  args=self.args.copy();args[key]=copy.deepcopy(args[key]);mutate(args[key])
  with self.assertRaises((AssertionError,KeyError,ValueError)):compose(**args)
 def test_unknown_physical_reason(self):self.altered('physical',lambda x:x['ordinaryNumericReasons'].append('unknown'))
 def test_runtime_failure(self):self.altered('physical',lambda x:x.update(runtimeChecksPassed=0))
 def test_native_actor_omission(self):self.altered('native',lambda x:x['completeNativeActualBoundsCertificate'].update(completeForeignNativeActors=6641))
 def test_native_overlap(self):self.altered('native',lambda x:x['completeNativeActualBoundsCertificate'].update(allFourOwnedByThreeActualNativeWorldBoundsStrictlyDisjoint=False))
 def test_foreign_collision(self):self.altered('foreign',lambda x:x.update(foreignActorsRequiringFullCollisionProof=['unexpected']))
 def test_identity_failure(self):self.altered('identity',lambda x:x.update(passed=False))
 def test_changed_ground(self):self.altered('data',lambda x:x.update(completeDrawnGroundSHA256='bad'))
 def test_stale_world(self):self.altered('graph',lambda x:x['rows'][0].update(completeWorldSHA256='bad'))
 def test_buried_leaf_as_bridge(self):self.altered('foundation',lambda x:x['rows'][0]['proof']['sourceBackedFoundationLeaf799'].update(exposedBridgeCredit=True))
 def test_canopy_structural_support(self):self.altered('canopy',lambda x:x['rows'][0]['namedIsolatedOpenPost43Proof'].update(canopySupportCredit=True))
 def test_visual_propagation(self):self.altered('mounts',lambda x:x['rows'][0]['completeDetachedComponentDispositions'][0].update(structuralBridgeCredit=True))
 def test_missing_loop(self):self.altered('mounts',lambda x:x['rows'][0]['completeDetachedComponentDispositions'][0]['completeEveryOriginalClosedBoundaryLoop'].pop())
 def test_partial_perimeter_claim(self):self.altered('mounts',lambda x:x['rows'][0]['completeDetachedComponentDispositions'][0].update(allOriginalLoopsMandatory=False))
 def test_named_raw_failure_erased(self):self.altered('mounts',lambda x:x['rows'][0].update(unresolvedCompleteBoundaryComponents=[]))
 def test_named_context_changed(self):self.altered('placement',lambda x:x['rows'][0]['complete14UnresolvedOriginalParts'][0]['completeOriginalGeometry'][0][0].__setitem__(0,0))
 def test_named_context_missing_part(self):self.altered('placement',lambda x:x['rows'][0]['complete14UnresolvedOriginalParts'].pop())
 def test_wrong_named_source(self):self.altered('placement',lambda x:x.update(sourceSHA256='bad'))
 def test_old_visual_context_as_current_acceptance(self):self.altered('placement',lambda x:x.update(currentAcceptance=True))
 def test_changed_context_loop(self):self.altered('placement',lambda x:x['rows'][0]['complete14UnresolvedOriginalParts'][0]['completeOriginalClosedBoundaryLoops'].pop())
 def test_false_named_mount(self):self.altered('placement',lambda x:x['rows'][0]['complete14UnresolvedOriginalParts'][0].update(structuralRootCredit=True))
 def test_stale_image(self):
  mode='providerOriginal';images=copy.deepcopy(IMAGES);images[0]['sha256']='bad'
  with self.assertRaises(AssertionError):verify(context=self.args['placement'],mode=mode,world=self.args['data']['completeWorldStreams'][mode]['completeWorldTriangles'],mounts=row_for(self.args['mounts'],mode),image_refs=images)
if __name__=='__main__':unittest.main()
