"""Hermetic actual-source standing skins and adverse geometry/binding cases."""
import copy
import numpy as np
import unittest
from run import ROOT,read
from evangel_college_named_standing_grade_skin_20261011 import verify,sha,IDS
B=ROOT/'docs/astra-city/government-import'
Q=read(B/'government-xl-evangel-college-91306-complete226-current-component-qualification-diagnostic-v1-20261011/diagnostic.json.gz')
R=read(ROOT/'source-scripts/city/government-import/local/government-xl-evangel-college-91306-disjoint-current-neighbour-parent-retention-v5-20261011/runtime-geometry.json.gz')
G=np.asarray(R['rows'][0]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
def fixture(component=62,mode='providerOriginal'):
 r=next(r for r in Q['rows']if r['arithmetic']==mode);x=next(x for x in r['completeFiveStandingDispositions']if x['originalComponent']==component)
 return np.asarray(x['completeOriginalGeometry'],dtype='<f8'),G.copy()
def call(t,g,c=62,ids=None,binding=None):
 b=dict(completePartSHA256=sha(t),completeGroundSHA256=sha(g));return verify(t,g,component=c,source_face_ids=IDS[c]if ids is None else ids,expected_binding=b if binding is None else binding,current_binding=b)
class StandingSkinTests(unittest.TestCase):
 def check_actual_worlds(self,component):
  for mode in ['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']:
   t,g=fixture(component,mode);p=call(t,g,component);assert p['everyLateralFacetGenuinelyCrossesGrade']and p['wholeOriginalUpperPerimeterStrictlyClear'];assert not p['closedSolidCertified']and not p['currentAcceptance'];assert p['rawWholeFootingFailureRemains']
 def test_actual_component_62(self):self.check_actual_worlds(62)
 def test_actual_component_98(self):self.check_actual_worlds(98)
 def test_actual_component_99(self):self.check_actual_worlds(99)
 def test_actual_component_100(self):self.check_actual_worlds(100)
 def test_wrong_source_face_ids(self):
  t,g=fixture()
  with self.assertRaises(AssertionError):call(t,g,ids=list(reversed(IDS[62])))
 def test_wrong_component(self):
  t,g=fixture()
  with self.assertRaises(AssertionError):verify(t,g,component=90,source_face_ids=list(range(12)),expected_binding={},current_binding={})
 def test_stale_part_binding(self):
  t,g=fixture()
  with self.assertRaises(AssertionError):call(t,g,binding=dict(completePartSHA256='0'*64,completeGroundSHA256=sha(g)))
 def test_stale_ground_binding(self):
  t,g=fixture()
  with self.assertRaises(AssertionError):call(t,g,binding=dict(completePartSHA256=sha(t),completeGroundSHA256='0'*64))
 def test_missing_original_face(self):
  t,g=fixture()
  with self.assertRaises(AssertionError):call(t[:-1],g)
 def test_duplicate_original_face_opens_skin(self):
  t,g=fixture();t[0]=t[1]
  with self.assertRaises(AssertionError):call(t,g)
 def test_zero_area_original_face_cannot_bridge(self):
  t,g=fixture();t[0]=t[0,0]
  with self.assertRaises(AssertionError):call(t,g)
 def test_disconnected_real_facet(self):
  t,g=fixture();t[0,:,0]+=100
  with self.assertRaises(AssertionError):call(t,g)
 def test_conflicting_original_winding(self):
  t,g=fixture();t[0]=t[0,::-1]
  with self.assertRaises(AssertionError):call(t,g)
 def test_no_genuine_grade_crossing(self):
  t,g=fixture();t[:,:,1]+=20
  with self.assertRaises(AssertionError):call(t,g)
 def test_upper_cap_hidden_by_actual_ground(self):
  t,g=fixture();g[:,:,1]+=20
  with self.assertRaises(AssertionError):call(t,g)
 def test_ground_projection_missing(self):
  t,g=fixture();g[:,:,0]+=1000
  with self.assertRaises(AssertionError):call(t,g)
 def test_nonfinite_source(self):
  t,g=fixture();t[0,0,0]=np.nan
  with self.assertRaises(AssertionError):call(t,g)
 def test_nonfinite_ground(self):
  t,g=fixture();g[0,0,0]=np.inf
  with self.assertRaises(AssertionError):call(t,g)
 def test_next_double_vertex_breaks_literal_shared_edge(self):
  t,g=fixture();t[0,0,0]=np.nextafter(t[0,0,0],np.inf)
  with self.assertRaises(AssertionError):call(t,g)

if __name__=='__main__':unittest.main()
