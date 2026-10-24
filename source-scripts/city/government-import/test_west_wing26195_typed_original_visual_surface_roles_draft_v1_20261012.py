"""Frozen actual metadata fixtures; no source/terrain/contact arithmetic or DB."""
import unittest,copy,gzip,json
from pathlib import Path
import west_wing26195_typed_original_visual_surface_roles_draft_v1_20261012 as H
from run import ROOT
B=ROOT/'docs/astra-city/government-import'
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  def gz(p):return json.load(gzip.open(p,'rt'))
  cls.mount=gz(B/'government-xl-west-wing26195-body108-113-visual-mounting-interface-context-v1-20261012/diagnostic.json.gz');cls.visual=json.loads((B/'government-xl-west-wing26195-body108-113-original-host-visual-context-v1-20261012/context.json').read_text());cls.census=gz(B/'government-xl-west-wing26195-complete-current-finite-ground-v3-20261012/diagnostic.json.gz')['originalBodyCensus'];cls.graph=gz(B/'government-xl-west-wing26195-complete-current-body-contact-graph-v1-20261012/diagnostic.json.gz');cls.source=dict(uid=H.UID,sourceSHA256=H.SOURCE)
 def check(self,m=None,v=None,c=None,g=None,source=None,pin=None):
  m=self.mount if m is None else m;v=self.visual if v is None else v;c=self.census if c is None else c;g=self.graph if g is None else g;return H.verify(m,v,c,g,self.source if source is None else source,expected_binding=H.input_binding(m,v,c,g)if pin is None else pin)
 def changed(self,callback):
  m=copy.deepcopy(self.mount);callback(m)
  with self.assertRaises(AssertionError):self.check(m=m)
 def body(self,m,label):return next(iter(m['distinctBodyAssociationContexts'].values()))['bodies'][str(label)]
 def test_actual_two_visual_contexts_never_approve_ground_or_install(self):
  r=self.check();self.assertEqual(r['sourceVisualOnlyBodies'],[108,113]);self.assertEqual(len(r['remaining116BodyRolesUnqualified']),116);self.assertFalse(r['physicalAccepted']);self.assertFalse(r['fullRoleReconciliationAccepted']);self.assertFalse(r['gradeRootAccepted'])
 def test_wrong_source_uid(self):
  with self.assertRaises(AssertionError):self.check(source=dict(uid='landsd/1:0',sourceSHA256=H.SOURCE))
 def test_wrong_source_revision(self):
  with self.assertRaises(AssertionError):self.check(source=dict(uid=H.UID,sourceSHA256='0'*64))
 def test_whole_partition_omission(self):
  c=copy.deepcopy(self.census);c['sharedEdgeConnectedComponents'][0].pop()
  with self.assertRaises(AssertionError):self.check(c=c)
 def test_duplicate_partition_face(self):
  c=copy.deepcopy(self.census);c['sharedEdgeConnectedComponents'][1].append(c['sharedEdgeConnectedComponents'][0][0])
  with self.assertRaises(AssertionError):self.check(c=c)
 def test_missing_literal_binding(self):self.changed(lambda m:m['allFourStreamBindings'].pop('literal'))
 def test_unbound_full_context(self):
  pin=H.input_binding(self.mount,self.visual,self.census,self.graph);pin['mountSHA256']='0'*64
  with self.assertRaises(AssertionError):self.check(pin=pin)
 def test_visual_geometry_edit(self):
  v=copy.deepcopy(self.visual);v['geometryChanges']=1
  with self.assertRaises(AssertionError):self.check(v=v)
 def test_missing_inspected_image(self):
  v=copy.deepcopy(self.visual);v['outputs'].pop()
  with self.assertRaises(AssertionError):self.check(v=v)
 def test_108_higher_boundary_filled(self):self.changed(lambda m:self.body(m,108).__setitem__('higherCompleteBoundaryRetainedUnfilled',False))
 def test_108_fake_opening_acceptance(self):self.changed(lambda m:self.body(m,108)['priorFourMinimumEdgeFiniteBandProofsReusedVerbatim'].__setitem__('completeLowerOpeningAssociated',True))
 def test_108_missing_complete_rim(self):self.changed(lambda m:self.body(m,108)['priorFourMinimumEdgeFiniteBandProofsReusedVerbatim']['allFourMinimumEdgeProofs'].pop())
 def test_113_partial_edge_promoted(self):self.changed(lambda m:self.body(m,113).__setitem__('wholeBandAssociatedBoundaryEdgeIndices',[0,2]))
 def test_113_literal_negative_erased(self):self.changed(lambda m:self.body(m,113)['priorWholeHostBandAndLiteralPointFailuresReusedVerbatim'].__setitem__('literalPointOnlyContactNegativeNotRewritten',False))
 def test_113_whole_band_negative_waived(self):self.changed(lambda m:self.body(m,113)['priorWholeHostBandAndLiteralPointFailuresReusedVerbatim'].__setitem__('completeTwoFaceFixedBandAssociationContextOnly',True))
 def test_host_grounding_invented(self):self.changed(lambda m:self.body(m,113)['completeStrictHostInventory'].__setitem__('strictHostGroundedIndependently',True))
 def test_physical_acceptance_injected(self):self.changed(lambda m:m.__setitem__('physicalAccepted',True))
if __name__=='__main__':unittest.main()
