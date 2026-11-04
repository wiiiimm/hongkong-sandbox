"""UNEXECUTED boundary/adverse fixtures for the acquisition-only local mask."""
import copy,hashlib,math,unittest
from fractions import Fraction as F
import numpy as np
import southside_saved_local_core_parent_adapter_v1_20261012 as a

def fixture(t=None):
 t=t or [[36.,1.,36.],[39.,2.,36.],[36.,1.,39.]]
 triangle=np.asarray([t],dtype='<f8');sha=hashlib.sha256(triangle.tobytes()).hexdigest()
 worlds={'landsd/315025:0':dict(sourceSHA256='a'*64,completeWorldStreams={m:dict(completeWorldTriangles=triangle.tolist(),completeWorldTriangleSHA256=sha)for m in a.MODES})}
 captures={'landsd/315025:0':dict(sourceSHA256='a'*64,completeFaces=1,completeOriginalIndex=[0,1,2],completeOriginalPOSITIONProof=dict(originalUnreferencedPositionVertices=0,allOriginalPositionVerticesAccounted=True,completeOriginalPositionVertices=3,worldTrianglesSHA256=sha),completeLiteralWorldPosition=t,completeExplicitLeftAssociatedFloat32WorldPosition=t,completeExplicitBalancedFloat32WorldPosition=t)}
 return worlds,captures

class LocalCoreTests(unittest.TestCase):
 def test_actual_four_modes_complete_baseline(self):
  w,c=fixture();self.assertTrue(a.bind_positions(w,c));core,collar,p=a.mask(w,c,[0,0,100,100]);self.assertEqual(p['completeSourceFaceSlots'],4);self.assertEqual(core,{(7,7)});self.assertEqual(len(collar),24)
 def test_missing_mode_rejected(self):
  w,c=fixture();del w[next(iter(w))]['completeWorldStreams'][a.MODES[3]]
  with self.assertRaises(AssertionError):a.bind_positions(w,c)
 def test_changed_stream_sha_rejected(self):
  w,c=fixture();w[next(iter(w))]['completeWorldStreams'][a.MODES[1]]['completeWorldTriangleSHA256']='b'*64
  with self.assertRaises(AssertionError):a.bind_positions(w,c)
 def test_wrong_source_rejected(self):
  w,c=fixture();c[next(iter(c))]['sourceSHA256']='b'*64
  with self.assertRaises(AssertionError):a.bind_positions(w,c)
 def test_missing_unused_position_coverage_rejected(self):
  w,c=fixture();c[next(iter(c))]['completeOriginalPOSITIONProof']['originalUnreferencedPositionVertices']=1
  with self.assertRaises(AssertionError):a.bind_positions(w,c)
 def test_missing_index_vertex_rejected(self):
  w,c=fixture();c[next(iter(c))]['completeOriginalIndex']=[0,1,1]
  with self.assertRaises(AssertionError):a.bind_positions(w,c)
 def test_actual_position_parity_rejected(self):
  w,c=fixture();c[next(iter(c))]['completeLiteralWorldPosition']=copy.deepcopy(c[next(iter(c))]['completeLiteralWorldPosition']);c[next(iter(c))]['completeLiteralWorldPosition'][0][1]=math.nextafter(1.,2.)
  with self.assertRaises(AssertionError):a.bind_positions(w,c)
 def test_exact_zero_point_on_closed_cell_corner_retained(self):
  w,c=fixture([[40.,1.,40.]]*3);core,_,p=a.mask(w,c,[0,0,100,100]);self.assertEqual(core,{(7,7),(8,7),(7,8),(8,8)});self.assertTrue(all(r['zero3DArea']for r in p['completeSourceFaceModeRecords']))
 def test_vertical_closed_skin_retained(self):
  w,c=fixture([[40.,1.,36.],[40.,3.,36.],[40.,1.,39.]]);core,_,p=a.mask(w,c,[0,0,100,100]);self.assertEqual(core,{(7,7),(8,7)});self.assertTrue(all(r['zeroXZArea']and not r['zero3DArea']for r in p['completeSourceFaceModeRecords']))
 def test_cell_inside_large_triangle_with_no_vertex_inside(self):
  w,c=fixture([[25.,1.,25.],[65.,1.,25.],[25.,1.,65.]]);core,_,_=a.mask(w,c,[0,0,100,100]);self.assertIn((7,7),core)
 def test_next_double_above_boundary_has_no_false_left_touch(self):
  x=math.nextafter(40.,math.inf);w,c=fixture([[x,1.,36.],[x,3.,36.],[x,1.,39.]]);core,_,_=a.mask(w,c,[0,0,100,100]);self.assertEqual(core,{(8,7)})
 def test_source_outside_domain_rejected(self):
  w,c=fixture([[-1.,1.,36.],[2.,1.,36.],[-1.,1.,39.]])
  with self.assertRaises(AssertionError):a.mask(w,c,[0,0,100,100])
 def test_complete_collar_must_stay_inside_domain(self):
  w,c=fixture([[1.,1.,36.],[3.,1.,36.],[1.,1.,39.]])
  with self.assertRaises(AssertionError):a.mask(w,c,[0,0,100,100])
 def test_mask_rectangles_preserve_hole_and_disconnected_cells(self):
  cells={(c,r)for c in range(3)for r in range(3)}-{(1,1)};cells.add((8,8));rects=a.rectangles(cells,[0,0,100,100]);got=set()
  for c in range(10):
   for r in range(10):
    x,z=F(5*c)+F(5,2),F(5*r)+F(5,2)
    if any(q[0]<x<q[2]and q[1]<z<q[3]for q in rects):got.add((c,r))
  self.assertEqual(got,cells)
 def test_boundary_owned_vertical_skin_not_duplicated(self):
  t=a.points([[5,1,1],[5,3,1],[5,1,4]]);inside,outside=a.split(t,a.rect_planes([F(5),F(0),F(10),F(5)]),0);self.assertEqual(inside,t);self.assertEqual(outside,[])
 def test_exact_split_conserves_every_real_piece(self):
  t=a.points([[0,1,0],[10,1,0],[0,1,10]]);inside,outside=a.split(t,a.rect_planes([F(2),F(2),F(4),F(4)]),1);self.assertEqual(a.old.intrinsic_area(t,1),a.old.intrinsic_area(inside,1)+sum(a.old.intrinsic_area(p,1)for p in outside));self.assertTrue(outside)
 def test_tiny_real_triangle_never_epsilon_omitted(self):
  tiny=F(1,10**300);t=[(F(0),F(1),F(0)),(tiny,F(1),F(0)),(F(0),F(1),tiny)];inside,outside=a.split(t,a.rect_planes([F(0),F(0),F(5),F(5)]),1);self.assertGreater(a.old.intrinsic_area(inside,1),0);self.assertEqual(outside,[])
 def test_distinct_height_layers_both_retained_in_core(self):
  rows=[]
  for y in [1,2]:
   t=a.points([[35,y,35],[39,y,35],[35,y,39]]);inside,outside=a.split(t,a.rect_planes([F(35),F(35),F(40),F(40)]),1);self.assertEqual(outside,[]);rows.extend(a.old.fan(inside))
  self.assertEqual(len(rows),2);self.assertNotEqual(rows[0],rows[1])
 def test_collar_exact_core_one_outer_zero(self):
  core=[[F(35),F(35),F(40),F(40)]];self.assertEqual(a.alpha_at(F(35),F(36),core),1);self.assertEqual(a.alpha_at(F(25),F(36),core),0);self.assertEqual(a.alpha_at(F(30),F(36),core),F(1,2))
 def test_shared_collar_node_uses_same_affine_endpoint(self):
  core=[[F(35),F(35),F(40),F(40)]];p=(F(30),a.alpha_at(F(30),F(30),core),F(30));left=[p,(F(35),F(1),F(30)),(F(30),F(1),F(35))];right=[(F(25),F(0),F(30)),p,(F(30),F(0),F(25))];self.assertEqual(a.old.plane_height(left,p),a.old.plane_height(right,p))
 def test_budget_increase_rejected_before_any_construction(self):
  with self.assertRaises(AssertionError):a.construction(dict(completeInputFacets=774477,triangleBudget=25001),{},dict(cell=5),{}, {})
 def test_incomplete_original_inventory_rejected_before_construction(self):
  with self.assertRaises(AssertionError):a.construction(dict(completeInputFacets=774476,triangleBudget=25000),{},dict(cell=5),{}, {})

if __name__=='__main__':unittest.main()
