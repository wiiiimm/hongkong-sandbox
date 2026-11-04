"""Whole actual pair and adversarial structural/visual/zero separation cases."""
import copy,unittest
import twin_regency1120_complete_original_role_composition_v1_20261011 as k
from twin_regency1120_complete_actual_fixture_v1_20261011 import actual_fixture
class ActualWholePairTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.args,cls.docs,cls.refs,cls.receipts=actual_fixture()
 def changed(self,key,mutate):
  args=self.args.copy();args[key]=copy.deepcopy(args[key]);mutate(args[key]);args['expected_binding']=k.binding(**{a:b for a,b in args.items()if a!='expected_binding'})
  with self.assertRaises(AssertionError):k.verify(**args)
 def selected_witness(self,x,mode='providerOriginal',involving=None):
  allowed=set.intersection(*[set(r['qualifiedDiagnosticBodyIDs'])for r in x['rows']]);row=next(r for r in x['rows']if r['mode']==mode)
  keys={tuple(r['proofKey'])for child,r in row['qualifiedDiagnosticParentForest'].items()if int(child)in allowed and(involving is None or involving in r['proofKey'])}
  assert keys
  return next(a['witness']for a in row['allAttemptedOriginalPairs']if tuple(a['originalBodies'])in keys)
 def test_complete_actual1120_partition_four_modes_and_no_visual_bridge(self):
  r=k.verify(**self.args);self.assertEqual(r['completeSourceFacets'],13519);self.assertEqual(r['completeOriginalNonzeroBodies'],1120)
  self.assertEqual(len(r['complete827IndependentNonvisualBodies']),827);self.assertEqual(len(r['complete155BoundaryVisualBodies']),155);self.assertEqual(len(r['complete138SourcePlacementVisualBodies']),138)
  self.assertEqual(len(r['all8OriginalZerosRetainedUncredited']),8);self.assertFalse(r['fullAcceptance']);self.assertFalse(r['installationApproved'])
  allowed=set(r['complete827IndependentNonvisualBodies'])
  for row in r['allFourStreamRows']:
   self.assertEqual(len(row['all826CompleteStrictPositiveInterfaces']),826)
   self.assertTrue(all(v['parent']in allowed for v in row['all826CompleteStrictPositiveInterfaces']))
 def test_visual_parent_cannot_bridge_otherwise_qualified_body(self):
  def mutate(x):next(iter(x['rows'][0]['qualifiedDiagnosticParentForest'].values()))['parent']=17
  self.changed('paths',mutate)
 def test_two_genuine_edges_forming_cycle_do_not_supply_ground_path(self):
  def mutate(x):
   f=x['rows'][0]['qualifiedDiagnosticParentForest'];allowed=set.intersection(*[set(r['qualifiedDiagnosticBodyIDs'])for r in x['rows']])
   child=next(int(i)for i,r in f.items()if int(i)in allowed and r['parent']in allowed-{1091});parent=f[str(child)]['parent'];f[str(parent)]={'parent':child,'proofKey':sorted([child,parent])}
  self.changed('paths',mutate)
 def test_source_zero_facet_cannot_be_positive_endpoint(self):
  def mutate(x):
   q=self.selected_witness(x);q['actualGlobalFaces'][0]=6580
  self.changed('paths',mutate)
 def test_render_collapsed_facet_cannot_be_contact_endpoint(self):
  def mutate(x):
   r=next(r for r in x['rows']if r['mode']=='explicitLeftAssociatedF32ModelMatrix');c=next(c for c in r['completeActualCensusForEveryOriginalBody']if c['completeActualEdgeCensus']['exactNonrenderingOriginalFaces']);body=c['originalBody'];face=c['completeActualEdgeCensus']['exactNonrenderingOriginalFaces'][0]
   q=self.selected_witness(x,'explicitLeftAssociatedF32ModelMatrix',body);i=next(i for i,b in enumerate(q['actualEndpointBodyMembership'])if b[0]==body);q['actualGlobalFaces'][i]=face
  self.changed('paths',mutate)
 def test_missing_genuine_grade_interval_not_sampled_root(self):
  def mutate(x):x['rows'][0]['mainPodiumGenuineGradeSeed']['exactGenuineGradeIntervals'][0]['exactActiveUpperGroundIntervals']=[]
  self.changed('paths',mutate)
 def test_vacuous_cap_cannot_be_relabelled_independent_cap_credit(self):self.changed('paths',lambda x:x['rows'][0]['mainPodiumGenuineGradeSeed'].update(vacuousCapIsNotIndependentCapCredit=False))
 def test_partial_visual_source_body_rejects_complete_accounting(self):self.changed('placement138',lambda x:x['rows'][0]['completeOriginalFaces'].pop())
 def test_visual_current_acceptance_or_structural_claim_rejects(self):self.changed('boundary155',lambda x:x['rows'][0].update(structuralRootCredit=True,currentAcceptance=True))
 def test_source_placement_mount_claim_cannot_replace_raw_failure(self):self.changed('placement138',lambda x:x['rows'][0].update(finiteMountingCertified=True))
 def test_discarded_mounting_negatives_rejects(self):self.changed('placement138',lambda x:x['rows'][0].update(allPriorMountingAndFreeEdgeNegativesVerbatim=[]))
 def test_ordinary_ground_coverage_not_exempted_by_role(self):self.changed('finite',lambda x:x['rows'][0]['completeAllOriginalFacetContexts'][0].update(groundProjectionCovered=False))
 def test_endpoint_only_exposure_does_not_replace_complete_strict_facets(self):
  self.changed('paths',lambda x:self.selected_witness(x)['completeStrictEndpointFacetContexts'][0].update(exactCertifiedLowerClearanceM='-1/100'))
 def test_complete_source_zero_inventory_cannot_be_dropped(self):self.changed('graph',lambda x:x['exactNonrenderingGlobalFacesRetainedUncredited'].pop())
 def test_complete_world_pose_change_cannot_rebind_completed_math(self):
  args=self.args.copy();args['worlds']=args['worlds'].copy();args['worlds']['capturedLiteral']=args['worlds']['capturedLiteral'].copy();args['worlds']['capturedLiteral'][0,0,0]+=.25
  args['expected_binding']=k.binding(**{a:b for a,b in args.items()if a!='expected_binding'})
  with self.assertRaises(AssertionError):k.verify(**args)
 def test_stale_interface_ground_selection_rejects(self):
  def mutate(x):self.selected_witness(x)['wholeInterfaceAgainstBothActorGrounds'][0]['proof']['selection']['completeGroundSHA256']='0'*64
  self.changed('paths',mutate)
if __name__=='__main__':unittest.main()
