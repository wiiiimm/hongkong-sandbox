"""Synthetic-only comparisons to the complete real canonical function output."""
from pathlib import Path
import importlib.util,copy,unittest
import numpy as np
from shapely.geometry import Polygon
from foundation_source_face_attribution_adapter_v1_20261013 import attribute,canonical_pin

spec=importlib.util.spec_from_file_location('foundation_attribution_synthetic_canonical',Path(__file__).with_name('xl-final-script-pass.py'))
canonical=importlib.util.module_from_spec(spec);spec.loader.exec_module(canonical)
FUNCTION=canonical.foundation_context;PIN=canonical_pin(FUNCTION)
GROUND=np.asarray([[[-100.,0.,-100.],[-100.,0.,100.],[100.,0.,-100.]],[[100.,0.,100.],[100.,0.,-100.],[-100.,0.,100.]]])
TARGET=Polygon([[-50,-50],[50,-50],[50,50],[-50,50]])
def triangle(x=0.,y=-1.,z=0.,scale=1.,upward=True):
 t=np.array([[x,y,z],[x,y,z+scale],[x+scale,y,z]],dtype=float)
 return t if upward else t[[0,2,1]]
def bodies(*groups):return [dict(bodyId=i,sourceFaceIndices=list(g))for i,g in enumerate(groups)]

class AttributionTests(unittest.TestCase):
 def evaluate(self,t,body,ground=GROUND,nonrendering=()):
  t=np.asarray(t);g=np.asarray(ground);source=t.tobytes();terrain=g.tobytes();inventory=copy.deepcopy(body)
  globals_before=dict(FUNCTION.__globals__);module_before=dict(canonical.__dict__);second_before=dict(canonical.s.__dict__);shared_before=dict(canonical.s.context.shared.__dict__)
  expected=FUNCTION(t,g,TARGET)
  actual=attribute(FUNCTION,t,g,TARGET,body,expected_canonical_pin=PIN,nonrendering_source_face_indices=nonrendering)
  self.assertEqual(expected,actual['canonicalFoundationMetrics'])
  self.assertEqual(source,t.tobytes());self.assertEqual(terrain,g.tobytes());self.assertEqual(inventory,body)
  for before,after in [(globals_before,FUNCTION.__globals__),(module_before,canonical.__dict__),(second_before,canonical.s.__dict__),(shared_before,canonical.s.context.shared.__dict__)]:
   self.assertEqual(before.keys(),after.keys());self.assertTrue(all(after[k]is v for k,v in before.items()))
  self.assertEqual(PIN,canonical_pin(FUNCTION));self.assertFalse(actual['bodyRoleRootPhysicalOrInstallationAccepted'])
  return actual

 def test_upward_ids_and_full_metrics(self):
  r=self.evaluate([triangle(),triangle(3,1)],bodies([0],[1]));self.assertEqual([0],r['fullyBuriedSourceFaceIndices']);self.assertEqual([0],r['fullyBuriedUpwardSourceFaceIndices'])

 def test_downward_buried_is_not_upward(self):
  r=self.evaluate([triangle(upward=False)],bodies([0]));self.assertEqual([0],r['fullyBuriedSourceFaceIndices']);self.assertEqual([],r['fullyBuriedUpwardSourceFaceIndices'])

 def test_vertical_buried_id_preserved_without_role(self):
  t=np.array([[0,-1,0],[0,-1,1],[0,-.6,0]],float)
  r=self.evaluate([t],bodies([0]));self.assertEqual([0],r['fullyBuriedSourceFaceIndices']);self.assertEqual([],r['fullyBuriedUpwardSourceFaceIndices'])

 def test_exact_negative_half_is_not_fully_buried(self):
  r=self.evaluate([triangle(y=-.5),triangle(3,y=np.nextafter(-.5,-np.inf))],bodies([0],[1]));self.assertEqual([1],r['fullyBuriedSourceFaceIndices'])

 def test_no_ground_preserves_missing_coverage_metrics(self):
  r=self.evaluate([triangle()],bodies([0]),ground=np.empty((0,3,3)));self.assertEqual(0,r['canonicalFoundationMetrics']['completeTerrainTriangles']);self.assertEqual([],r['fullyBuriedSourceFaceIndices']);self.assertEqual([],r['failureGroupsInCanonicalDelegateOrder'])

 def test_mixed_missing_coverage_is_not_burial(self):
  r=self.evaluate([triangle(),triangle(1000)],bodies([0],[1]));self.assertEqual(1,r['canonicalFoundationMetrics']['completeTerrainTriangles']);self.assertEqual([0],r['fullyBuriedSourceFaceIndices']);self.assertEqual([1],r['notFullyBuriedSourceFaceIndices'])

 def test_degenerate_incident_preserved_and_uncredited(self):
  zero=np.array([[4.,-1.,4.],[4.,-1.,4.],[4.,-1.,4.]])
  r=self.evaluate([triangle(),zero],bodies([0],[1]),nonrendering=[1]);self.assertEqual([0,1],r['fullyBuriedSourceFaceIndices']);self.assertEqual([0],r['fullyBuriedUpwardSourceFaceIndices']);self.assertEqual([1],r['nonrenderingSourceFaceIndices']);self.assertTrue(r['nonrenderingFacetsReceiveNoSupportCredit'])

 def test_sorted_aggregate_not_journal_order(self):
  r=self.evaluate([triangle(scale=1),triangle(10,scale=4)],bodies([0],[1]));groups=r['failureGroupsInCanonicalDelegateOrder']
  self.assertEqual([[0],[1]],[q['sourceFaceIndices']for q in groups]);self.assertGreater(r['canonicalFoundationMetrics']['components'][0]['areaM2'],r['canonicalFoundationMetrics']['components'][1]['areaM2']);self.assertTrue(r['sortedCanonicalAggregatesNotHeuristicallyMatchedToJournal'])

 def test_failure_subset_does_not_replace_complete_body(self):
  wall=np.array([[0.,-1.,0.],[0.,-1.,1.],[0.,1.,0.]]) # Genuine shared edge with the buried floor.
  r=self.evaluate([triangle(),wall],bodies([0,1]));q=r['failureGroupsInCanonicalDelegateOrder'][0]['intersectionsWithEveryCompleteSavedBody'][0]
  self.assertEqual(2,q['completeSavedBodyFaceCount']);self.assertEqual([0],q['failureGroupSourceFaceIndices']);self.assertEqual([0,1],r['completeSavedBodyInventoryVerbatim'][0]['sourceFaceIndices'])

 def test_rounded_vertex_group_can_intersect_multiple_true_edge_bodies(self):
  r=self.evaluate([triangle(),triangle(z=1)],bodies([0],[1]));self.assertEqual(1,len(r['failureGroupsInCanonicalDelegateOrder']))
  intersections=r['failureGroupsInCanonicalDelegateOrder'][0]['intersectionsWithEveryCompleteSavedBody'];self.assertEqual([[0],[1]],[q['failureGroupSourceFaceIndices']for q in intersections])

 def test_every_body_including_empty_intersection_is_recorded(self):
  r=self.evaluate([triangle(),triangle(10,y=1),triangle(20)],bodies([0],[1],[2]));self.assertTrue(all(len(g['intersectionsWithEveryCompleteSavedBody'])==3 for g in r['failureGroupsInCanonicalDelegateOrder']));self.assertEqual([],r['failureGroupsInCanonicalDelegateOrder'][0]['intersectionsWithEveryCompleteSavedBody'][1]['failureGroupSourceFaceIndices'])

 def test_noncontiguous_input_and_source_order_not_renumbered(self):
  t=np.stack([triangle(10),triangle(0,y=1),triangle(20)])[::-1]
  self.assertFalse(t.flags.c_contiguous);r=self.evaluate(t,bodies([0],[1],[2]));self.assertEqual([0,2],r['fullyBuriedSourceFaceIndices']);self.assertEqual([0,1,2],r['completeSourceFaceIndices'])

 def test_overlapping_body_inventory_rejected(self):
  with self.assertRaises(AssertionError):attribute(FUNCTION,np.stack([triangle(),triangle(3)]),GROUND,TARGET,bodies([0,1],[1]),expected_canonical_pin=PIN)

 def test_omitted_body_face_rejected(self):
  with self.assertRaises(AssertionError):attribute(FUNCTION,np.stack([triangle(),triangle(3)]),GROUND,TARGET,bodies([0]),expected_canonical_pin=PIN)

 def test_float_and_boolean_source_indices_rejected(self):
  for bad in [[0.0],[False]]:
   with self.subTest(bad=bad),self.assertRaises(AssertionError):attribute(FUNCTION,np.stack([triangle()]),GROUND,TARGET,bodies(bad),expected_canonical_pin=PIN)

 def test_changed_canonical_pin_rejected(self):
  pin={**PIN,'foundationCodeSHA256':'0'*64}
  with self.assertRaises(AssertionError):attribute(FUNCTION,np.stack([triangle()]),GROUND,TARGET,bodies([0]),expected_canonical_pin=pin)

if __name__=='__main__':unittest.main(verbosity=2)
