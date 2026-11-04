import copy,unittest
from polyu_compact_runtime_mesh_projection_v1_draft_20261014 import mesh_binding
import numpy as np
from polyu_four_parent_current_capture_binding_v3_draft_20261014 import append_binding,scene_delta,terrain_disjoint,UPTON_CAT,AQUA_CAT,UPTON_PATCH,OLD_PATCH
def scenes():
 old=dict(officialModelCatalogues=['old'],terrainPatches=[dict(url=OLD_PATCH),dict(url='other')],unchanged=dict(x=1))
 new=copy.deepcopy(old);new['officialModelCatalogues']+=[UPTON_CAT,AQUA_CAT];new['terrainPatches']=[dict(url=UPTON_PATCH),dict(url='other')]
 return old,new
def patch():return dict(w=2,h=2,meta=dict(georef=dict(W=2,H=2,aE=1,aN=-1,bE=834500,bN=816500)),elev=[0]*4,renderedElev=[0]*4,vegetation=[0]*4,nativeMesh=dict(position=[0,0,0,1,0,0,0,0,1],index=[0,1,2]))
class Binding(unittest.TestCase):
 def test_exact_two_delta_preserves_original(self):
  old,new=scenes();saved=copy.deepcopy((old,new));self.assertEqual(scene_delta(old,new)['addedCatalogueURLs'],[UPTON_CAT,AQUA_CAT]);self.assertEqual((old,new),saved)
 def test_other_field_rejected(self):
  old,new=scenes();new['unchanged']['x']=2
  with self.assertRaises(AssertionError):scene_delta(old,new)
 def test_catalogue_order_rejected(self):
  old,new=scenes();new['officialModelCatalogues'][-2:]=[AQUA_CAT,UPTON_CAT]
  with self.assertRaises(AssertionError):scene_delta(old,new)
 def test_another_terrain_change_rejected(self):
  old,new=scenes();new['terrainPatches'].append(dict(url='extra'))
  with self.assertRaises(AssertionError):scene_delta(old,new)
 def test_remove_and_append_terrain_order_rejected(self):
  old,new=scenes();new['terrainPatches'].reverse()
  with self.assertRaises(AssertionError):scene_delta(old,new)
 def test_unused_native_position_cannot_be_ignored(self):
  p=patch();p['nativeMesh']['position']+=[10,0,10]
  with self.assertRaises(AssertionError):terrain_disjoint(p,[9,9,11,11])
 def test_closed_touch_rejected(self):
  with self.assertRaises(AssertionError):terrain_disjoint(patch(),[1,1,2,2])
def synthetic_append():
 old=dict(nativeMesh=dict(position=[0.,-0.,0.,1.,0.,0.,0.,0.,1.,99.,-0.,99.],index=[0,1,2]))
 piece=dict(fan=1,path=[],packing=dict(packedTriplet=[[0.,0.,0.],[1.,0.,0.],[1.,0.,1.]],packedYNotAboveOwnAuthenticatedParentPlane=True),completeNewPieceOrdinaryCompatibility=dict(eligible=True))
 mesh=copy.deepcopy(old['nativeMesh']);mesh['position']+=sum(piece['packing']['packedTriplet'],[]);mesh['index']+=[4,5,6]
 regions=[dict(target=t,completeRefinement=dict(acceptedPieces=[piece]if i==0 else[]))for i,t in enumerate([[1,2590,1,1],[8,0,0,0],[8,4,0,34],[8,18,1,87],[3,40,1,3]])]
 n=dict(newNativeMesh=mesh,previousCompleteMeshBinding=mesh_binding(old['nativeMesh']),newCompleteMeshBinding=mesh_binding(mesh),appendedFaces=[dict(candidateFace=1,completeSelectedRegion=0,**piece)],completeSelectedRegions=regions,
 allPriorPositionAndIndexBytesIncludingUnusedAndSignedZeroPreserved=True,all780OldRejectedPiecesRemainRejected=True,noKnownConflictingTriangleRestored=True,sourceOverlapRequiresFreshGeometryBinding=True,originalGovernmentGeometryAndPoseUnchanged=True,currentAcceptance=False)
 return n,old
class RefinedBinding(unittest.TestCase):
 def test_dynamic_prefix_and_unused_signedzero(self):
  n,o=synthetic_append();self.assertEqual(append_binding(n,o)['completeIndexedFaces'],2)
 def test_refined_node_must_match_exact_accepted_provenance(self):
  n,o=synthetic_append();n['appendedFaces'][0]['path']=[1]
  with self.assertRaises(AssertionError):append_binding(n,o)
 def test_prefix_signzero_change_cannot_be_hidden_by_numeric_equality(self):
  n,o=synthetic_append();n['newNativeMesh']['position'][1]=0.;n['newCompleteMeshBinding']=mesh_binding(n['newNativeMesh'])
  with self.assertRaises(AssertionError):append_binding(n,o)
if __name__=='__main__':unittest.main()
