"""Unexecuted exact clipping/accounting and actual-bounds adverse fixtures."""
import copy,hashlib,unittest
from fractions import Fraction as F
import numpy as np
import southside_exact_private_terrain_adapter_v1_20261012 as h
def parent():return dict(w=5,h=5,elev=[2]*25,vegetation=[0]*25,meta=dict(georef=dict(aE=10,aN=-10,bE=834500,bN=816500)))
def build(triangles):
 whole=np.asarray(triangles,dtype='<f8');return h.construct(whole,parent(),[0,0,4,4],[0,0,40,40],[10,10,30,30],expected_sha256=hashlib.sha256(whole.tobytes()).hexdigest(),expected_count=len(whole))
REAL=[[11,5,11],[12,5,11],[11,5,12]]
def native_fixture():
 b=[[100,0,100],[101,10,101]];mesh=dict(wholePositionVerticesIncludingUnused=True,completePositionVertices=3,completeIndexedFaces=1,completeLiteralBounds=b,completeLeftAssociatedF32Bounds=b,completeBalancedF32Bounds=b)
 rows=[dict(uid=f'landsd/{i}:0',sourceSHA256='a'*64,sourceFacesOmitted=0,wholeUnusedPositionVerticesIncluded=True,completePositionVertices=3,completeFaces=1,actualRenderMeshes=[copy.deepcopy(mesh)],completeOriginalPOSITIONProof=dict(allOriginalPositionVerticesAccounted=True,originalWholeSourceBounds=copy.deepcopy(b)),completeLiteralBounds=copy.deepcopy(b),completeLeftAssociatedF32Bounds=copy.deepcopy(b),completeBalancedF32Bounds=copy.deepcopy(b))for i in range(6649)]
 return dict(completeNativeActors=6649,successfullyCapturedActors=6649,errors=[],rows=rows)
class Tests(unittest.TestCase):
 def test_01_tiny_true_area(self):self.assertTrue(h.area_real([[0,0,0],[1e-300,0,0],[0,0,1e-300]]))
 def test_02_exact_zero(self):self.assertFalse(h.area_real([[0,0,0],[1,1,1],[2,2,2]]))
 def test_03_vertical_real(self):self.assertTrue(h.area_real([[0,0,0],[0,1,0],[0,0,1]]));self.assertEqual(h.normal([[0,0,0],[0,1,0],[0,0,1]])[1],0)
 def test_04_original_numpy_double(self):self.assertTrue(h.area_real(np.asarray(REAL,dtype='<f8')))
 def test_05_closed_touch(self):self.assertTrue(h.closed_xz_touch([0,0,1,1],[1,1,2,2]));self.assertFalse(h.closed_xz_touch([0,0,1,1],[np.nextafter(1,2),1,2,2]))
 def test_06_core_keeps_vertices(self):
  p=list(map(h.point,REAL));self.assertEqual(h.rect(p,[10,10,30,30]),p)
 def test_07_rational_rectangle_partition(self):
  p=list(map(h.point,[[0,0,0],[2,0,0],[0,0,2]]));self.assertEqual(h.intrinsic_area(h.rect(p,[0,0,1,1]),1),1)
 def test_08_parent_plane_exact(self):
  t=list(map(h.point,[[0,2,0],[2,4,0],[0,6,2]]));self.assertEqual(h.plane_height(t,h.point([.5,0,.5])),F(7,2))
 def test_09_parent_winding(self):
  p=list(map(h.point,[[0,0,0],[2,0,0],[0,0,2]]));t=list(map(h.point,[[0,1,0],[1,1,0],[0,1,1]]));self.assertEqual(h.intrinsic_area(h.parent_clip(p,t),1),h.intrinsic_area(h.parent_clip(p,t[::-1]),1))
 def test_10_existing_rendered_floor_water(self):
  p=parent();p['elev'][0]=.5;p['elev'][1]=0;self.assertEqual(h.rendered_height(p,0),F(1.2));self.assertEqual(h.rendered_height(p,1),-4)
 def test_11_existing_rendered_override(self):
  p=parent();p['renderedElev']=[3]*25;self.assertEqual(h.rendered_height(p,0),3)
 def test_12_complete_bounds_cells(self):
  cells,bb,core=h.nominate_cells([[[110,0,110],[120,10,120]]],dict(w=40,h=40,elev=[2]*1600,meta=dict(georef=dict(aE=10,aN=-10,bE=834500,bN=816500))));self.assertEqual(cells,[9,9,14,14]);self.assertEqual(bb,[90,90,140,140]);self.assertEqual(core,[100,100,130,130])
 def test_13_parent_domain_failure(self):self.assertRaises(AssertionError,h.nominate_cells,[[[110,0,110],[120,10,120]]],parent())
 def test_14_parent_patch_touch(self):
  p=dict(path='p.json',sha256='a'*64,jsonPointer='',data=dict(w=2,h=2,meta=dict(georef=dict(aE=10,aN=-10,bE=834510,bN=816500),targetUids=['x'])));self.assertEqual(len(h.parent_child_obligations([0,0,10,10],[p])),1)
 def test_15_parent_mesh_spill(self):
  p=dict(w=2,h=2,meta=dict(georef=dict(aE=10,aN=-10,bE=834500,bN=816500)),nativeMesh=dict(position=[-.125,2,0,1,2,1,1,2,2]));self.assertEqual(h.terrain_bounds(p)[0],-.125)
 def test_16_alpha_branch_coverage(self):
  p=list(map(h.point,[[0,3,0],[2,3,0],[0,3,2]]));parts=list(h.alpha_branches(p,[0,0,2,2],1));self.assertEqual(sum(h.intrinsic_area(q,1)for _,_,q in parts),h.intrinsic_area(p,1))
 def test_17_vertical_alpha_tie_single_owner(self):
  p=list(map(h.point,[[.5,0,.5],[.5,1,.5],[.8,1,.8]]));parts=[q for _,_,q in h.alpha_branches(p,[0,0,2,2],1)if h.intrinsic_area(q,0)];self.assertEqual(len(parts),1)
 def test_18_source_core_complete(self):
  patch,q=build([REAL]);self.assertEqual(len(patch['nativeMesh']['index']),3);self.assertEqual(q['completeOutputFacetLineage'][0]['classification'],'source-core');self.assertEqual(q['completeSelectedOriginalFacetAccounts'][0]['exactIntrinsicAccountedArea'],'1/2')
 def test_19_zero_retained_uncredited(self):
  patch,q=build([[[11,3,11],[12,3,12],[13,3,13]],REAL]);self.assertEqual(q['exactZeroOriginalFacetIds'],[0]);self.assertFalse(q['completeSelectedOriginalFacetAccounts'][0]['renderCoverageOrBridgeCredit']);self.assertEqual(len(patch['nativeMesh']['index']),3)
 def test_20_vertical_core_not_omitted(self):
  patch,q=build([[[11,2,11],[11,3,11],[11,2,12]]]);self.assertEqual(q['allVerticalRealOriginalFacetIds'],[0]);self.assertEqual(len(patch['nativeMesh']['index']),3)
 def test_21_float32_collapse_preserved(self):
  patch,q=build([[[11,5,11],[11+1e-12,5,11],[11,5,11+1e-12]]]);self.assertEqual(q['realOutputFacetsCollapsedByFloat32'],[0]);self.assertEqual(len(patch['nativeMesh']['index']),3);self.assertFalse(q['physicalAccepted'])
 def test_22_outside_inventory_accounted(self):
  patch,q=build([REAL,[[50,3,50],[51,3,50],[50,3,51]]]);self.assertEqual(q['allOutsideAlteredDomainOriginalFacetIds'],[1]);self.assertEqual(q['completeInputFacets'],2)
 def test_23_transition_change_explicit(self):
  patch,q=build([[[0,10,1],[0,20,1],[0,10,2]],REAL]);trans=[r for r in q['completeOutputFacetLineage']if r['globalOriginalFacetId']==0];self.assertTrue(trans);self.assertTrue(all(r['classification']=='changed-transition'for r in trans));self.assertTrue(q['realOutputFacetsCollapsedByFloat32'])
 def test_24_full_native_touch_and_adverse_scope(self):
  n=native_fixture();n['rows'][0]['completeOriginalPOSITIONProof']['originalWholeSourceBounds']=[[10,0,0],[11,1,1]];q=h.nominate_natives([[0,0,0],[10,0,10]],n);self.assertEqual(len(q['nominated']),1);self.assertEqual(len(q['excluded']),6648)
  for defect in ['omission','unused','matrix_bounds']:
   with self.subTest(defect=defect):
    bad=copy.deepcopy(n)
    if defect=='omission':bad['rows'].pop()
    elif defect=='unused':bad['rows'][0]['wholeUnusedPositionVerticesIncluded']=False
    else:bad['rows'][0]['completeLiteralBounds'][1][0]=102
    self.assertRaises(AssertionError,h.nominate_natives,[[0,0,0],[10,0,10]],bad)
 def test_25_source_hash_and_count_fail_closed(self):
  whole=np.asarray([REAL],dtype='<f8')
  self.assertRaises(AssertionError,h.construct,whole,parent(),[0,0,4,4],[0,0,40,40],[10,10,30,30],expected_sha256='0'*64,expected_count=1)
  self.assertRaises(AssertionError,h.construct,whole,parent(),[0,0,4,4],[0,0,40,40],[10,10,30,30],expected_sha256=hashlib.sha256(whole.tobytes()).hexdigest(),expected_count=2)
 def test_26_refined_parent_grid_all_unused_nodes(self):
  step,w,hgt,nodes,raw,display,vegetation=h.refined_parent_grid(parent(),[0,0,4,4],[0,0,40,40])
  self.assertEqual(step,F(2));self.assertEqual((w,hgt),(21,21));self.assertEqual(len(nodes),441);self.assertEqual(nodes[-1],(F(40),F(2),F(40)))
  self.assertEqual(raw,[2.0]*441);self.assertEqual(display,[2.0]*441);self.assertEqual(vegetation,[0]*441)
if __name__=='__main__':unittest.main(verbosity=2)
