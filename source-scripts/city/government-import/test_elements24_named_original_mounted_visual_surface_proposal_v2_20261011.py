"""Sixteen preserved v1 cases plus seven direct negative-policy predicates.

Rebinding in these seven synthetic negative fixtures deliberately lets the
predicate see a newly admitted FAILED diagnostic. It is not an archive alias,
current receipt, numerical proof, or a way to replace any frozen producer input.
"""
import copy,unittest
import test_elements24_named_original_mounted_visual_surface_proposal_v1_20261011 as fixture
import elements24_named_original_mounted_visual_surface_proposal_v1_20261011 as k

class ActualPolicyPredicateTests(fixture.ActualNamedVisualSurfaceTests):
 def admitted_negative(self,part,contexts=None,hosts=None):
  p=self.packages[part].copy()
  if contexts is not None:p['contexts']=contexts
  if hosts is not None:p['qualified_hosts']=hosts
  p['expected_binding']=k.binding(part,p['uid'],p['source_sha'],p['worlds'],p['contexts'],p['qualified_hosts'])
  return p
 def test_true_free_edge_cannot_substitute_for_failed_named_U_chain(self):
  p=self.packages[500];contexts=copy.deepcopy(p['contexts']);m=k.original_mount(500,p['worlds']['providerOriginal'],k.NAMED_SOURCE_PART_FACES[500]);a=contexts['providerOriginal']['association']
  for e in a['allActualIncidenceOneBoundaryEdgeProofs']:
   e['wholeEdgeWithinExistingFiniteHostBand']=k.key(e['completeActualBoundaryEdge'])in m['free']
  with self.assertRaisesRegex(AssertionError,'Incomplete named mounting chain'):k.verify(**self.admitted_negative(500,contexts))
 def test_new_failed_whole_surface_is_not_generic_visual_credit(self):
  contexts=copy.deepcopy(self.packages[68]['contexts']);contexts['providerOriginal']['association']['allActualFacetProofs'][0]['wholeFacetWithinExistingFiniteHostBand']=False
  with self.assertRaises(AssertionError):k.verify(**self.admitted_negative(68,contexts))
 def test_partial_folded_bottom_backbone_fails_even_with_terminal_mounts(self):
  p=self.packages[509];contexts=copy.deepcopy(p['contexts']);m=k.original_mount(509,p['worlds']['providerOriginal'],k.NAMED_SOURCE_PART_FACES[509]);e=next(e for e in contexts['providerOriginal']['association']['allActualIncidenceOneBoundaryEdgeProofs']if k.key(e['completeActualBoundaryEdge'])in m['lower']);e['wholeEdgeWithinExistingFiniteHostBand']=False
  with self.assertRaisesRegex(AssertionError,'Incomplete named mounting chain'):k.verify(**self.admitted_negative(509,contexts))
 def test_folded_required_terminal_is_not_a_permitted_free_edge(self):
  p=self.packages[509];contexts=copy.deepcopy(p['contexts']);m=k.original_mount(509,p['worlds']['providerOriginal'],k.NAMED_SOURCE_PART_FACES[509]);e=next(e for e in contexts['providerOriginal']['association']['allActualIncidenceOneBoundaryEdgeProofs']if k.key(e['completeActualBoundaryEdge'])in m['terminals']);e['wholeEdgeWithinExistingFiniteHostBand']=False
  with self.assertRaisesRegex(AssertionError,'Incomplete named mounting chain'):k.verify(**self.admitted_negative(509,contexts))
 def test_ineligible_host_cannot_receive_visual_bootstrap(self):
  hosts=copy.deepcopy(self.packages[500]['qualified_hosts']);hosts['actualLiteral']=[]
  with self.assertRaises(AssertionError):k.verify(**self.admitted_negative(500,hosts=hosts))
 def test_finite_ordinary_failure_not_masked_by_mount(self):
  contexts=copy.deepcopy(self.packages[500]['contexts']);contexts['actualLiteral']['allCompletePartFiniteFaces'][0]['existingOrdinaryClearanceBoundProved']=False
  with self.assertRaises(AssertionError):k.verify(**self.admitted_negative(500,contexts))
 def test_partial_boundary_inventory_not_accepted_as_whole_U(self):
  contexts=copy.deepcopy(self.packages[500]['contexts']);contexts['actualLiteral']['association']['allActualIncidenceOneBoundaryEdgeProofs'].pop()
  with self.assertRaises(AssertionError):k.verify(**self.admitted_negative(500,contexts))
if __name__=='__main__':unittest.main()
