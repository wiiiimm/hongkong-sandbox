"""Complete actual body accounting and meaningful unsupported-path mutations."""
import copy,unittest
from run import ROOT,read
import elements998_complete_original_role_composition_v1_20261011 as k
from test_elements11_named_original_visual_placement_proposal_v1_20261011 import actual_fixture as placement_fixture
BASE=ROOT/'docs/astra-city/government-import'
def actual_fixture():
 docs,parts=placement_fixture();worlds=next(iter(parts.values()))['worlds']
 names=dict(paths='elements-bounded-owned-four-stream-path-replay-v1',caps='elements998-bounded-four-stream-grade-cap-paths-v1',lateral='elements31-complete-lateral-patches-and39-disposition-v1',named24='elements24-named-original-visual-proposals-v1',named4='elements4-named-complete-perimeter-visual-sheet-proposals-v1',named11='elements11-named-original-visual-placement-proposals-v1')
 args=dict(worlds=worlds,graph=docs['graph'],finite=docs['finite'])
 args.update({key:read(BASE/('xl-terrain-recovery-20261011-'+name)/'diagnostic.json.gz')for key,name in names.items()});return args

class ActualCompleteRoleCompositionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.args=actual_fixture();cls.binding=k.binding(**cls.args)
 def check(self,change=None,*,rebind=False):
  args=self.args.copy();args.update(change or{});return k.verify(**args,expected_binding=k.binding(**args)if rebind else self.binding)
 def altered_path(self):
  p=self.args['paths'].copy();p['rows']=p['rows'].copy();p['rows'][1]=copy.deepcopy(p['rows'][1]);return p,p['rows'][1]
 def test_complete_actual23809_998_866_132_fourstream_partition(self):
  r=self.check();self.assertEqual(r['completeOriginalFaces'],23809);self.assertEqual(r['completeNonzeroOriginalBodies'],998);self.assertEqual(r['completeStructuralPathBodies'],866);self.assertEqual(r['completeNonstructuralVisualBodies'],132);self.assertEqual(len(r['all47OriginalZeroFacetsPreservedUncredited']),47);self.assertTrue(r['noWholeNativeReacceptance']);self.assertFalse(r['currentAcceptance'])
 def test_visual_body_cannot_parent_a_structural_path(self):
  p,row=self.altered_path();child=next(iter(row['qualifiedDiagnosticParentForest']));row['qualifiedDiagnosticParentForest'][child]['parent']=893
  with self.assertRaises(AssertionError):self.check(dict(paths=p),rebind=True)
 def test_missing_structural_parent_cannot_leave_body_claimed(self):
  p,row=self.altered_path();row['qualifiedDiagnosticParentForest'].pop(next(iter(row['qualifiedDiagnosticParentForest'])))
  with self.assertRaises(AssertionError):self.check(dict(paths=p),rebind=True)
 def test_point_contact_never_substitutes_positive_interface(self):
  p,row=self.altered_path();parent=next(iter(row['qualifiedDiagnosticParentForest'].values()));proof=next(x for x in row['allAttemptedOriginalOwnedPairs']if x['originalBodies']==parent['proofKey']);proof['witness']['actualExactContact']['dimension']=0
  with self.assertRaises(AssertionError):self.check(dict(paths=p),rebind=True)
 def test_endpoint_only_area_credit_rejects(self):
  p,row=self.altered_path();parent=next(iter(row['qualifiedDiagnosticParentForest'].values()));proof=next(x for x in row['allAttemptedOriginalOwnedPairs']if x['originalBodies']==parent['proofKey']);proof['witness']['allPointsExposedByCompleteEndpointFacets']=False
  with self.assertRaises(AssertionError):self.check(dict(paths=p),rebind=True)
 def test_source_original_zero_cannot_be_omitted(self):
  g=self.args['graph'].copy();g['exactNonrenderingGlobalFacesRetained']=g['exactNonrenderingGlobalFacesRetained'][1:]
  with self.assertRaises(AssertionError):self.check(dict(graph=g),rebind=True)
 def test_entire_native_body_is_not_a_root_seed(self):
  c=self.args['caps'].copy();c['nativeBodyReceivesNoRootSeed']=False
  with self.assertRaises(AssertionError):self.check(dict(caps=c),rebind=True)
 def test_grade_interval_removed_from_native_seed_rejects(self):
  c=self.args['caps'].copy();c['rows']=c['rows'].copy();c['rows'][1]=copy.deepcopy(c['rows'][1]);record=next(x for x in c['rows'][1]['all20OriginalInterfacesAccounted']if x['ownedBody']==4);record['gradeWall']['exactUpperGroundIntervals']=[]
  p,row=self.altered_path();nom=next(x for x in row['qualifiedNativeInterfaceNominations']if x['originalBody']==4);nom['wholeBoundedNativePath']=record
  with self.assertRaises(AssertionError):self.check(dict(caps=c,paths=p),rebind=True)
 def test_rendered_wholefacet_failure_is_not_a_visual_exemption(self):
  finite=self.args['finite'].copy();finite['rows']=finite['rows'].copy();finite['rows'][2]=copy.deepcopy(finite['rows'][2]);finite['rows'][2]['allFaces'][0]['strictlyExposedWholeFacet']=False
  with self.assertRaises(AssertionError):self.check(dict(finite=finite),rebind=True)
 def test_missing_named_visual_body_rejects_complete_accounting(self):
  n=self.args['named11'].copy();n['all11NamedOriginalVisualPlacementProposals']=n['all11NamedOriginalVisualPlacementProposals'][:-1]
  with self.assertRaises(AssertionError):self.check(dict(named11=n),rebind=True)
 def test_source_visual_becoming_bridge_is_rejected(self):
  n=self.args['named11'].copy();n['all11NamedOriginalVisualPlacementProposals']=n['all11NamedOriginalVisualPlacementProposals'].copy();n['all11NamedOriginalVisualPlacementProposals'][0]=n['all11NamedOriginalVisualPlacementProposals'][0].copy();n['all11NamedOriginalVisualPlacementProposals'][0]['structuralBridgeCredit']=True
  with self.assertRaises(AssertionError):self.check(dict(named11=n),rebind=True)
 def test_complete_lateral_patch_cannot_be_replaced_with_partial_edges(self):
  l=self.args['lateral'].copy();l['rows']=l['rows'].copy();l['rows'][1]=copy.deepcopy(l['rows'][1]);u=l['rows'][1]['all31CompleteUnitLateralDiagnoses'][0];i=u['completeOppositePatchBandCandidates'][0][0];u['allCompleteLateralPatchProofs'][i]['completePatchWithinExistingFiniteBand']=False
  with self.assertRaises(AssertionError):self.check(dict(lateral=l),rebind=True)
 def test_visual_host_cycle_in_frame_unit_is_rejected(self):
  l=self.args['lateral'].copy();l['rows']=l['rows'].copy();l['rows'][1]=copy.deepcopy(l['rows'][1]);u=l['rows'][1]['all31CompleteUnitLateralDiagnoses'][0];i=u['completeOppositePatchBandCandidates'][0][0];u['allCompleteLateralPatchProofs'][i]['completeSameActorQualifiedHostSelection']['selectedGlobalHostFaces']=[u['complete22OriginalUnitFaceIds'][0]]
  with self.assertRaises(AssertionError):self.check(dict(lateral=l),rebind=True)
 def test_changed_world_rejects_even_rebound_inputs(self):
  w=self.args['worlds'].copy();w['actualLiteral']=w['actualLiteral'].copy();w['actualLiteral'][0,0,0]+=.125
  with self.assertRaises(AssertionError):self.check(dict(worlds=w),rebind=True)
if __name__=='__main__':unittest.main()
