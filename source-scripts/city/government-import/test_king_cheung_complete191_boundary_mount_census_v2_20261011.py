"""Complete actual original opening census and conservative host nomination."""
import unittest,importlib.util
from pathlib import Path
import numpy as np
from run import ROOT,read
p=Path(__file__).with_name('xl-king-cheung-95691-complete191-detached-boundary-mount-diagnostic-v2-20261011.py');s=importlib.util.spec_from_file_location('king191draft',p);k=importlib.util.module_from_spec(s);s.loader.exec_module(k)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  b=ROOT/'docs/astra-city/government-import';g=read(b/'government-xl-king-cheung-95691-complete908-source-component-interfaces-v2-20261011/diagnostic.json.gz');r=next(x for x in g['rows']if x['arithmetic']=='providerOriginal');cls.parts=r['completeOriginalTopology']['sharedEdgeConnectedComponents'];cls.un=r['componentsWithoutCandidateSourcePath'];cls.w=np.asarray(read(b/'government-xl-king-cheung-95691-current-actual-ground-capture-v1-20261011/complete-four-stream-ground-inputs.json.gz')['completeWorldStreams']['providerOriginal']['completeWorldTriangles'])
 def test_actual_complete191_single_boundaries(self):
  self.assertEqual(len(self.un),191)
  for i in self.un:
   inv,edges,_,loops=k.boundary(self.w,self.parts[i]);self.assertEqual(len(edges),4 if len(self.parts[i])==10 else 8);self.assertEqual(sorted(map(len,loops)),[4,4]if len(self.parts[i])==24 else[len(edges)])
 def test_missing_original_facet_rejected(self):
  with self.assertRaises(AssertionError):k.boundary(self.w,self.parts[35][:-1])
 def test_duplicate_original_face_rejected(self):
  with self.assertRaises(AssertionError):k.boundary(self.w,self.parts[35]+self.parts[35][-1:])
 def test_disconnected_authored_parts_rejected(self):
  with self.assertRaises(AssertionError):k.boundary(self.w,sorted(self.parts[35]+self.parts[36]))
 def test_empty_host_scope_retained_as_empty(self):self.assertEqual(k.nearby_hosts(self.w,self.parts[35],[]),([],[]))
 def test_all_far_hosts_explicitly_excluded(self):
  n,e=k.nearby_hosts(self.w,self.parts[35],self.parts[34]);self.assertFalse(n);self.assertEqual(len(e),262)
 def test_exact_band_boundary_stays_nominated(self):
  w=np.asarray([[[0,0,0],[0,1,0],[0,0,1]],[[.1,0,0],[.1,1,0],[.1,0,1]]]);n,e=k.nearby_hosts(w,[0],[1]);self.assertEqual(n,[1]);self.assertFalse(e)
 def test_next_double_outside_band_excluded(self):
  w=np.asarray([[[0,0,0],[0,1,0],[0,0,1]],[[np.nextafter(.1,1),0,0],[np.nextafter(.1,1),1,0],[np.nextafter(.1,1),0,1]]]);n,e=k.nearby_hosts(w,[0],[1]);self.assertFalse(n);self.assertEqual(len(e),1)
 def test_diagonal_squared_distance_exclusion(self):
  w=np.asarray([[[0,0,0],[0,0,.01],[0,.01,0]],[[.08,.1,0],[.08,.2,0],[.08,.1,.01]]]);n,e=k.nearby_hosts(w,[0],[1]);self.assertFalse(n);self.assertEqual(len(e),1)
 def test_coordinate_permutation_preserves_actual_edge_geometry(self):
  edges=k.boundary(self.w,self.parts[35])[1]
  for edge in edges:
   original=np.asarray(edge)
   for perm in [[0,1,2],[1,0,2],[0,2,1]]:self.assertEqual(np.dot(original[1]-original[0],original[1]-original[0]),np.dot((original[1]-original[0])[perm],(original[1]-original[0])[perm]))
 def test_actual24face_body_preserves_both_openings(self):
  _,edges,_,loops=k.boundary(self.w,self.parts[84]);self.assertEqual(len(loops),2);self.assertEqual(len(edges),sum(map(len,loops)))
 def test_reversed_original_facet_rejected(self):
  w=self.w.copy();w[self.parts[84][0]]=w[self.parts[84][0]][::-1]
  with self.assertRaises(AssertionError):k.boundary(w,self.parts[84])
 def test_zero_area_facet_rejected(self):
  w=self.w.copy();w[self.parts[84][0]]=w[self.parts[84][0]][0]
  with self.assertRaises(AssertionError):k.boundary(w,self.parts[84])
if __name__=='__main__':unittest.main()
