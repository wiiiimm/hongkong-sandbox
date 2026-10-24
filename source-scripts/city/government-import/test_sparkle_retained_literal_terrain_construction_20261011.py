import copy,json,unittest
from pathlib import Path
import numpy as np
from sparkle_retained_literal_terrain_construction_20261011 import dyadic_facet_boxes,strictly_separate_boxes_from_owned,merge_literal_ground_snapshots,whole_ground_faces_touching_boxes,copy_complete_aligned_old_grid,clip_new_planes_outside

def face(x=0,z=0):return np.array([[x,2,z],[x+1,2,z],[x,2,z+1]],float)
def grid(w,h,x=0,z=0,step=5):return dict(w=w,h=h,cell=step,elev=list(range(w*h)),renderedElev=[v+.5 for v in range(w*h)],vegetation=[v%2 for v in range(w*h)],meta=dict(georef=dict(W=w,H=h,aE=step,aN=-step,bE=x,bN=z)))
class Construction(unittest.TestCase):
 def test_clipped_source_plane_not_sampled_or_flattened(self):
  import shapely
  t=face();t[:,1]=2+t[:,0]+3*t[:,2];out=clip_new_planes_outside([t],shapely.box(.2,.2,.3,.3))
  self.assertTrue(np.allclose(out[:,:,1],2+out[:,:,0]+3*out[:,:,2],atol=1e-14,rtol=0));self.assertAlmostEqual(sum(shapely.Polygon(f[:,[0,2]]).area for f in out),.49)
 def test_clipping_preserves_winding(self):
  import shapely
  t=face();out=clip_new_planes_outside([t],shapely.box(.1,.1,.2,.2));self.assertTrue(all(np.dot(np.cross(f[1]-f[0],f[2]-f[0]),np.cross(t[1]-t[0],t[2]-t[0]))>0 for f in out))
 def test_collapsed_new_terrain_is_not_height_plane(self):
  import shapely
  with self.assertRaises(AssertionError):clip_new_planes_outside([[[0,0,0],[0,1,0],[0,1,1]]],shapely.box(2,2,3,3))
 def test_fully_removed_surface_not_fake_complete(self):
  import shapely
  with self.assertRaises(AssertionError):clip_new_planes_outside([face()],shapely.box(-1,-1,2,2))
 def test_exact_outward_enclosure(self):
  t=face(.00001,.00003);b=dyadic_facet_boxes([np.array([t])]);self.assertEqual(b.shape,(1,4));self.assertTrue(np.all(b[0,:2]<=t[:,[0,2]].min(axis=0)));self.assertTrue(np.all(b[0,2:]>=t[:,[0,2]].max(axis=0)))
 def test_zero_projection_has_positive_closed_rectangle(self):
  b=dyadic_facet_boxes([np.array([[[1,0,2],[1,1,2],[1,2,2]]])]);self.assertTrue(np.all(b[:,:2]<b[:,2:]))
 def test_touching_is_not_disjoint(self):
  with self.assertRaises(AssertionError):strictly_separate_boxes_from_owned([[0,0,1,1]],[np.array([face(1,0)])])
 def test_dyadic_expansion_conflict_is_not_waived(self):
  t=face();b=dyadic_facet_boxes([np.array([t])],collar_cells=1)
  with self.assertRaises(AssertionError):strictly_separate_boxes_from_owned(b,[np.array([face(1.0005,0)])])
 def test_true_separation(self):self.assertTrue(strictly_separate_boxes_from_owned([[0,0,1,1]],[np.array([face(2,2)])])['allClosedBoxesStrictlySeparated'])
 def test_nonfinite_rejected(self):
  t=face();t[0,0]=np.nan
  with self.assertRaises(AssertionError):dyadic_facet_boxes([np.array([t])])
 def test_duplicate_drawn_multiplicity_not_dropped(self):
  t=face();a=merge_literal_ground_snapshots([np.array([t,t]),np.array([t])]);self.assertEqual(len(a),2)
 def test_distinct_winding_not_merged(self):
  t=face();self.assertEqual(len(merge_literal_ground_snapshots([np.array([t]),np.array([t[[0,2,1]]])])),2)
 def test_ground_closed_edge_touch_included(self):
  g=np.array([face(),face(5,5)]);ids,selected=whole_ground_faces_touching_boxes(g,[[1,0,2,1]]);self.assertEqual(ids.tolist(),[0]);np.testing.assert_array_equal(selected,np.array([face()]))
 def test_complete_scalar_grid_and_absolute_nodes_preserved(self):
  old=grid(3,3,10,-10);new=grid(6,6);out,p=copy_complete_aligned_old_grid(new,old);self.assertEqual(p['completeOldCells'],4);self.assertEqual(p['completeOldNodes'],9)
  for oi,ni in p['completeOldNodeIndexMapping']:
   for k in p['copiedKeys']:self.assertEqual(out[k][ni],old[k][oi])
  self.assertEqual(new,grid(6,6))
 def test_same_values_wrong_georef_rejected(self):
  old=grid(3,3,10.1,-10)
  with self.assertRaises(AssertionError):copy_complete_aligned_old_grid(grid(6,6),old)
 def test_changed_pitch_rejected(self):
  with self.assertRaises(AssertionError):copy_complete_aligned_old_grid(grid(6,6,step=2.5),grid(3,3))
 def test_old_region_outside_candidate_rejected(self):
  with self.assertRaises(AssertionError):copy_complete_aligned_old_grid(grid(2,2),grid(3,3))
 def test_actual_current_old_grid_all4047nodes(self):
  root=Path(__file__).resolve().parents[3];old=json.loads((root/'3d-viewer/city/data/government-native-138091-0.json').read_text());new=copy.deepcopy(old);new['w']=new['meta']['georef']['W']=85;new['meta']['georef']['bE']-=70
  for k in ['elev','renderedElev','vegetation']:new[k]=[0]*(new['w']*new['h'])
  out,p=copy_complete_aligned_old_grid(new,old);self.assertEqual(p['completeOldNodes'],4047);self.assertEqual(p['completeOldCells'],3920)
  for oi,ni in p['completeOldNodeIndexMapping']:
   for k in p['copiedKeys']:self.assertEqual(out[k][ni],old[k][oi])
if __name__=='__main__':unittest.main()
