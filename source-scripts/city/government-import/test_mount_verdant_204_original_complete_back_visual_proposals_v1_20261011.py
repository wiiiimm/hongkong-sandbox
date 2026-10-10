"""Actual complete Mount source fixtures and adverse visual-association cases."""
import copy,unittest
from unittest.mock import patch
import numpy as np
from run import ROOT,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import mount_verdant_204_original_complete_back_visual_proposals_v1_20261011 as kernel
class ActualBackAssociationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  p=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261011-mount-verdant-two-current-render-attribute-capture-v1/literal-source-inputs.json.gz'; data=read(p); worlds=[]
  for row in data['rows']:
   asset=ROOT/row['path'];assert digest(asset.read_bytes())==row['entry']['sha256'];worlds.append(decode_original_world_triangles(asset.read_bytes()))
  cls.world=np.concatenate(worlds);cls.data=kernel.membership();cls.hosts=cls.data['conditionalHostGlobalFaces'];cls.open=cls.data['exactOriginalMembership']['6'];cls.closed=cls.data['exactOriginalMembership']['316'];cls.binding=dict(sourceSHA256ByUID={'landsd/261717:0':kernel.SOURCE_T,'landsd/75782:0':kernel.SOURCE_P},complete15579WorldSHA256=kernel.sha(cls.world),membershipBytesSHA256=kernel.MEMBERSHIP_SHA256,completeHostFaceIdsSHA256=kernel.canonical(cls.hosts))
 def test_actual_complete_open_back_positive_not_root(self):
  r=kernel.association(self.world,self.open,self.hosts);self.assertTrue(r['mountAssociationVerified']);self.assertFalse(r['structuralRootCredit']);self.assertFalse(r['structuralBridgeCredit']);self.assertEqual(len(r['completeWholeBackingPerimeterProofs']),4)
 def test_actual_complete_six_facet_back_positive_not_solid(self):
  r=kernel.association(self.world,self.closed,self.hosts);self.assertEqual(len(r['completeAllBackingFacetProofs']),6);self.assertFalse(r['closedSolidCertification']);self.assertFalse(r['hostTransferCredit'])
 def test_partial_original_body_rejects(self):
  e=copy.deepcopy(self.open);e['allBodyFaces']=e['allBodyFaces'][:-1]
  with self.assertRaises(AssertionError):kernel.association(self.world,e,self.hosts)
 def test_partial_six_facet_back_rejects(self):
  e=copy.deepcopy(self.closed);e['backPatchFaces']=e['backPatchFaces'][:-1]
  with self.assertRaises(AssertionError):kernel.association(self.world,e,self.hosts)
 def test_other_side_cannot_replace_whole_back(self):
  e=copy.deepcopy(self.closed);e['backPatchFaces']=e['allBodyFaces'][:6]
  with self.assertRaises(AssertionError):kernel.association(self.world,e,self.hosts)
 def test_detached_actual_host_rejects(self):
  t=self.world.copy();t[self.hosts]+=np.array([1000.,0.,0.])
  with self.assertRaises(AssertionError):kernel.association(t,self.open,self.hosts)
 def test_detached_actual_closed_back_rejects(self):
  t=self.world.copy();t[self.hosts]+=np.array([1000.,0.,0.])
  with self.assertRaises(AssertionError):kernel.association(t,self.closed,self.hosts)
 def test_face_pose_change_breaks_complete_back(self):
  t=self.world.copy();t[self.open['allBodyFaces'][0],0,0]+=.25
  with self.assertRaises(AssertionError):kernel.association(t,self.open,self.hosts)
 def test_reversed_authored_face_rejects(self):
  t=self.world.copy();i=self.open['allBodyFaces'][0];t[i]=t[i][[0,2,1]]
  with self.assertRaises(AssertionError):kernel.association(t,self.open,self.hosts)
 def test_self_hosting_is_not_a_mount(self):
  with self.assertRaises(AssertionError):kernel.association(self.world,self.open,sorted(set(self.hosts+self.open['allBodyFaces'])))
 def test_horizontal_open_bottom_is_separate_route(self):
  parts=kernel.census(self.world[:14938],list(range(14938)))['sharedEdgeConnectedComponents'];e=dict(kind='complete-original-incidence-one-opening',allBodyFaces=parts[311],backPatchFaces=None)
  with self.assertRaises(AssertionError):kernel.association(self.world,e,self.hosts)
 def test_changed_whole_world_rejected_even_with_matching_caller_hash(self):
  t=self.world.copy();t[0,0,0]+=.25;b={**self.binding,'complete15579WorldSHA256':kernel.sha(t)}
  with self.assertRaises(AssertionError):kernel.verify(t,'providerOriginal',expected_binding=b,current_binding=b)
 def test_false_source_binding_rejects(self):
  b=copy.deepcopy(self.binding);b['sourceSHA256ByUID']['landsd/261717:0']='0'*64
  with self.assertRaises(AssertionError):kernel.verify(self.world,'providerOriginal',expected_binding=b,current_binding=b)
 def test_changed_membership_bytes_rejects(self):
  with patch.object(kernel.Path,'read_bytes',return_value=b'{}'):
   with self.assertRaises(AssertionError):kernel.membership()
 def test_source_binding_mutation_rejects(self):
  b={**self.binding,'completeHostFaceIdsSHA256':'0'*64}
  with self.assertRaises(AssertionError):kernel.verify(self.world,'providerOriginal',expected_binding=b,current_binding=b)
 def test_nonfinite_input_rejects(self):
  t=self.world.copy();t[self.open['allBodyFaces'][0],0,0]=float('nan')
  with self.assertRaises(AssertionError):kernel.association(t,self.open,self.hosts)
if __name__=='__main__':unittest.main()
