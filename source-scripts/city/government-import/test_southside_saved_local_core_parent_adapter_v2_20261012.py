"""UNEXECUTED boundary/adverse fixtures for the acquisition-only local mask."""
import copy,hashlib,math,unittest
from fractions import Fraction as F
import numpy as np
import southside_saved_local_core_parent_adapter_v2_20261012 as a

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


class TrueBoundaryPartitionTests(unittest.TestCase):
 def tri(self,x0=0,z0=0,x1=10,z1=10,y=1):return a.points([[x0,y,z0],[x1,y,z0],[x0,y,z1]])
 def area(self,parts,axis=1):return sum((a.old.intrinsic_area(p,axis)for p in parts),F(0))
 def values(self,parts,p):
  values=[a.affine_value(plane,p)for poly,plane,_ in parts if a.old.rect([p],[min(v[0]for v in poly),min(v[2]for v in poly),max(v[0]for v in poly),max(v[2]for v in poly)])]
  return values
 def test_full_union_containment_returns_original_uncut(self):
  t=self.tri();inside,outside,full=a.union_partition(t,[[F(0),F(0),F(5),F(10)],[F(5),F(0),F(10),F(10)]],1);self.assertTrue(full);self.assertEqual(inside,[t]);self.assertEqual(outside,[])
 def test_hole_inside_triangle_prevents_bypass(self):
  t=self.tri(0,0,20,20);rs=a.rectangles({(c,r)for c in range(4)for r in range(4)}-{(1,1)},[0,0,20,20]);inside,outside,full=a.union_partition(t,rs,1);self.assertFalse(full);self.assertGreater(self.area(outside),0);self.assertEqual(self.area(inside+outside),self.area([t]))
 def test_disconnected_union_is_not_bbox_coverage(self):
  t=self.tri();inside,outside,full=a.union_partition(t,[[F(0),F(0),F(2),F(10)],[F(8),F(0),F(10),F(10)]],1);self.assertFalse(full);self.assertGreater(self.area(outside),0)
 def test_closed_vertical_tie_preserves_single_skin(self):
  t=a.points([[5,0,1],[5,4,1],[5,0,9]]);inside,outside,full=a.union_partition(t,[[F(0),F(0),F(5),F(10)],[F(5),F(0),F(10),F(10)]],0);self.assertTrue(full);self.assertEqual(inside,[t]);self.assertFalse(outside)
 def test_partial_union_has_exact_intrinsic_account(self):
  t=self.tri();inside,outside,full=a.union_partition(t,[[F(2),F(2),F(4),F(4)]],1);self.assertFalse(full);self.assertEqual(self.area(inside+outside),self.area([t]))
 def test_tiny_real_full_union_is_not_omitted(self):
  e=F(1,10**300);t=[(F(0),F(1),F(0)),(e,F(1),F(0)),(F(0),F(1),e)];inside,outside,full=a.union_partition(t,[[F(0),F(0),F(1),F(1)]],1);self.assertTrue(full);self.assertEqual(inside,[t]);self.assertGreater(self.area(inside),0)
 def test_independent_original_height_layers_are_not_merged(self):
  rs=[[F(0),F(0),F(10),F(10)]];results=[a.union_partition(self.tri(y=y),rs,1)[0]for y in [1,2]];self.assertEqual([len(q)for q in results],[1,1]);self.assertNotEqual(results[0],results[1])
 def test_outside_width_retains_uncut_zero_alpha(self):
  t=self.tri(30,30,31,31);parts=a.envelope_partition(t,[[F(0),F(0),F(5),F(5)]],1);self.assertEqual(parts,[(t,(F(0),F(0),F(0)),None)])
 def test_complete_core_alpha_is_exactly_one(self):
  t=self.tri(1,1,2,2);parts=a.envelope_partition(t,[[F(0),F(0),F(5),F(5)]],1);self.assertEqual(self.area([p for p,_,_ in parts]),self.area([t]));self.assertTrue(all(a.affine_value(a0,p)==1 for poly,a0,_ in parts for p in poly))
 def test_side_branch_is_continuous_exact_half_alpha(self):
  t=self.tri(-5,1,-4,2);parts=a.envelope_partition(t,[[F(0),F(0),F(5),F(5)]],1);self.assertTrue(all(a.affine_value(a0,p)==1+p[0]/10 for poly,a0,_ in parts for p in poly))
 def test_nearest_union_crossover_conserves_every_piece(self):
  t=self.tri(5,-5,15,5);rs=[[F(0),F(0),F(5),F(5)],[F(15),F(0),F(20),F(5)]];parts=a.envelope_partition(t,rs,1);self.assertEqual(self.area([p for p,_,_ in parts]),self.area([t]));self.assertGreater(len(parts),1)
 def test_vertical_alpha_tie_never_duplicates_real_skin(self):
  t=a.points([[-5,0,-5],[-5,4,-5],[-4,0,-4]]);parts=a.envelope_partition(t,[[F(0),F(0),F(5),F(5)]],0);self.assertEqual(self.area([p for p,_,_ in parts],0),self.area([t],0))
 def test_reordered_rectangles_keep_exact_alpha_at_all_vertices(self):
  t=self.tri(5,-5,15,5);rs=[[F(0),F(0),F(5),F(5)],[F(15),F(0),F(20),F(5)]]
  for r in [rs,list(reversed(rs))]:
   parts=a.envelope_partition(t,r,1);self.assertTrue(all(a.affine_value(a0,p)==a.alpha_at(p[0],p[2],rs)for poly,a0,_ in parts for p in poly))
 def test_duplicate_mask_rectangle_adds_no_losing_cuts(self):
  t=self.tri(-5,1,-4,2);r=[F(0),F(0),F(5),F(5)];self.assertEqual(a.envelope_partition(t,[r],1),a.envelope_partition(t,[r,r],1))
 def test_true_core_and_active_boundary_endpoint_heights(self):
  rs=[[F(0),F(0),F(5),F(5)]]
  for x,expected in [(F(0),F(1)),(F(-10),F(0))]:
   p=(x,F(7),F(2));alpha=a.alpha_at(x,p[2],rs);self.assertEqual(alpha,expected);self.assertEqual(alpha*p[1]+(1-alpha)*F(3),F(7)if expected else F(3))
 def test_actual_preserved_float32_collapse_remains_real(self):
  raw=[['1405/2','9027665539/465489920','30555602301/6649856'],['359687/512','910965784899/46976204800','9410401/2048'],['1405/2','9044347831/466350080','30612064329/6662144']];t=[tuple(F(v)for v in p)for p in raw];self.assertTrue(any(a.normal(t)));packed=[[a.old.f32(v)for v in p]for p in t];self.assertFalse(a.old.area_real(packed))
 def test_alpha_corner_requires_real_branch_not_node_chord(self):
  t=self.tri(-5,-5,-1,-1);rs=[[F(0),F(0),F(5),F(5)]];parts=a.envelope_partition(t,rs,1);self.assertGreater(len(parts),1);self.assertEqual(self.area([p for p,_,_ in parts]),self.area([t]))
 def test_vertex_blend_is_declared_changed_not_quadratic_exact(self):
  # Even one affine alpha times two different affine heights is quadratic.
  h=lambda x:(F(1)+x/10)*(F(10)+x)+(F(0)-x/10)*F(2)
  self.assertNotEqual(h(F(-5)),(h(F(-6))+h(F(-4)))/2)

if __name__=='__main__':unittest.main()
