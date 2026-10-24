"""Representation fixtures only; no DB, captures, finite kernels or source decode."""
import copy,hashlib,unittest
import numpy as np
from upton_captured_ground_tuple_representation_v1_20261012 import adapt_captured_ground
class Tests(unittest.TestCase):
 def setUp(self):
  a=[[-0.0,1.,2.,3.,4.,5.,6.,7.,8.],[9.,10.,11.,12.,13.,14.,15.,16.,17.]]
  self.raw=[a[0],a[1],copy.deepcopy(a[0]),[0.]*9]
  self.row=dict(uid='whole-parent-domain',completeClosedWholeDomainCapture=True,completeAttributionMultisetMatchedActual=True,allActualFacesIncludingDegeneraciesRetained=True,completeCurrentDrawnDomainFacets=4,completeActualDrawnTriplets=copy.deepcopy(self.raw),completeAttributedSources=[dict(sourcePath='base',allSelectedMeshFaceIDs=[2,3],completeSelectedDrawnTriplets=[copy.deepcopy(self.raw[1]),copy.deepcopy(self.raw[0])]),dict(sourcePath='retained',allSelectedMeshFaceIDs=[4,5],completeSelectedDrawnTriplets=[copy.deepcopy(self.raw[3]),copy.deepcopy(self.raw[2])])])
  self.kw=dict(expected_faces=4,expected_ground_sha=hashlib.sha256(np.array(self.raw,dtype='<f8').tobytes()).hexdigest(),expected_source_counts=[('base',2),('retained',2)])
 def reject(self,row):
  with self.assertRaises(AssertionError):adapt_captured_ground(row,**self.kw)
 def test_exact_order_signedzero_duplicate_degenerate_preserved(self):
  a,p=adapt_captured_ground(self.row,**self.kw);self.assertEqual(a.shape,(4,3,3));self.assertEqual(a.tobytes(),np.array(self.raw,dtype='<f8').tobytes());self.assertTrue(np.signbit(a[0,0,0]));self.assertTrue(p['completeAttributionBinary64MultisetMatched'])
 def test_nested_triplets_rejected_not_guessed(self):
  r=copy.deepcopy(self.row);r['completeActualDrawnTriplets']=np.array(self.raw).reshape(4,3,3).tolist();self.reject(r)
 def test_flat9N_rejected_not_guessed(self):
  r=copy.deepcopy(self.row);r['completeActualDrawnTriplets']=np.array(self.raw).flatten().tolist();self.reject(r)
 def test_truncated_row_rejected(self):
  r=copy.deepcopy(self.row);r['completeActualDrawnTriplets'][0].pop();self.reject(r)
 def test_missing_complete_face_rejected(self):
  r=copy.deepcopy(self.row);r['completeActualDrawnTriplets'].pop();self.reject(r)
 def test_nonfinite_scalar_rejected(self):
  for x in [float('nan'),float('inf')]:
   r=copy.deepcopy(self.row);r['completeActualDrawnTriplets'][0][1]=x;self.reject(r)
 def test_coerced_string_and_boolean_rejected(self):
  for x in ['1',True]:
   r=copy.deepcopy(self.row);r['completeActualDrawnTriplets'][0][1]=x;self.reject(r)
 def test_raw_order_change_rejected_even_same_multiset(self):
  r=copy.deepcopy(self.row);r['completeActualDrawnTriplets'][0],r['completeActualDrawnTriplets'][1]=r['completeActualDrawnTriplets'][1],r['completeActualDrawnTriplets'][0];self.reject(r)
 def test_attribution_signedzero_change_rejected(self):
  r=copy.deepcopy(self.row);r['completeAttributedSources'][0]['completeSelectedDrawnTriplets'][1][0]=0.;self.reject(r)
 def test_attribution_multiplicity_change_rejected(self):
  r=copy.deepcopy(self.row);r['completeAttributedSources'][1]['completeSelectedDrawnTriplets'][1]=copy.deepcopy(self.raw[1]);self.reject(r)
 def test_attribution_source_identity_rejected(self):
  r=copy.deepcopy(self.row);r['completeAttributedSources'][0]['sourcePath']='other';self.reject(r)
 def test_attribution_face_ids_duplicate_rejected(self):
  r=copy.deepcopy(self.row);r['completeAttributedSources'][0]['allSelectedMeshFaceIDs']=[2,2];self.reject(r)
 def test_false_complete_capture_flag_rejected(self):
  r=copy.deepcopy(self.row);r['completeAttributionMultisetMatchedActual']=False;self.reject(r)
if __name__=='__main__':unittest.main()
