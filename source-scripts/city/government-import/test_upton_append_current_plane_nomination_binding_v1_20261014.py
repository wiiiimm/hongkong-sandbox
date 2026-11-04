import unittest
from copy import deepcopy
from fractions import Fraction as F
from upton_append_current_plane_nomination_binding_v1_20261014 import append_bound_pieces,digest
from polyu_five_mask_source_plane_partition_v1_20261014 import packed_pieces,points,serial
class Binding(unittest.TestCase):
 def setUp(self):
  self.raw=[[[0.,0.,0.],[1.,0.,0.],[0.,0.,1.]]];self.pv=[{'old':True}]
  self.mesh={'position':[0.,0.,0.,1.,0.,0.,0.,0.,1.,123.,456.,789.],'index':[0,1,2],'source':{'historical':True}}
  self.protected=[{'newCandidate':0,'rawTripletSHA256':digest(self.raw[0])}]
  self.map=[{'oldCandidateFace':0,'newCandidateFaces':[0],'allOldRawBytesUnchanged':True}]
 def addition(self):
  ideal=[['0','0','0'],['1','1','0'],['0','0','1']]
  poly=[['0','0','0'],['1/3','1/3','0'],['0','0','1/2']]
  p=packed_pieces([points(poly)],ideal)[0]
  return {'packedPieceTriplet':p['packedPieceTriplet'],'provenance':{'candidateFace':1,'rawNominationFaceSHA256':digest(p['packedPieceTriplet']),'exactOriginalPlanePoints':serial(p['exactOwnPlanePoints'])}},p
 def test_prefix_unused_and_rational_plane(self):
  item,p=self.addition();old=deepcopy((self.raw,self.pv,self.mesh,self.protected,self.map));r=append_bound_pieces(self.raw,self.pv,self.mesh,[item],self.protected,self.map)
  self.assertEqual(old,(self.raw,self.pv,self.mesh,self.protected,self.map));self.assertEqual(r['newNativeMesh']['position'][:12],self.mesh['position']);self.assertEqual(r['newNativeMesh']['index'],[0,1,2,4,5,6]);self.assertEqual(r['protectedWholeCurrentTripletsUnchanged'],self.protected)
  self.assertEqual(p['exactOwnPlanePoints'][1][0],F(1,3));self.assertTrue(p['packingResidualsMeasuredNotWaived']);self.assertEqual(len(r['candidateRawPositionTriplets']),2)
 def test_wrong_old_mesh_rejected(self):
  self.mesh['position'][1]=1
  with self.assertRaises(AssertionError):append_bound_pieces(self.raw,self.pv,self.mesh,[],self.protected,self.map)
 def test_stale_protection_rejected(self):
  self.protected[0]['rawTripletSHA256']='0'*64
  with self.assertRaises(AssertionError):append_bound_pieces(self.raw,self.pv,self.mesh,[],self.protected,self.map)
 def test_incomplete_cumulative_rejected(self):
  self.map[0]['newCandidateFaces']=[]
  with self.assertRaises(AssertionError):append_bound_pieces(self.raw,self.pv,self.mesh,[],self.protected,self.map)
 def test_stale_new_index_rejected(self):
  item,_=self.addition();item['provenance']['candidateFace']=2
  with self.assertRaises(AssertionError):append_bound_pieces(self.raw,self.pv,self.mesh,[item],self.protected,self.map)
 def test_unpacked_added_tuple_rejected(self):
  item,_=self.addition();item['packedPieceTriplet'][1][0]=1/3
  with self.assertRaises(AssertionError):append_bound_pieces(self.raw,self.pv,self.mesh,[item],self.protected,self.map)
if __name__=='__main__':unittest.main()
