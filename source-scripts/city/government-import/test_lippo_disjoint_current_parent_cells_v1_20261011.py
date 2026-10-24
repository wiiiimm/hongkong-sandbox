"""Actual source/parent fixtures and adverse candidate-only bounds checks."""
import unittest,copy,numpy as np
from run import ROOT,read
from lippo_disjoint_current_parent_cells_v1_20261011 import proposed_cells,extent,overlap,CELLS,PARENT_URL,complete_geometry_containment
from lippo_pair_current_identity_v1_20261011 import UIDS
DOC=ROOT/'docs/astra-city/government-import/government-xl-lippo-current-bound-six-roof-inputs-v2-20261010'
class Cases(unittest.TestCase):
 def setUp(self):
  self.rows=[r for r in read(DOC/'selection.json.gz')['rows'] if r['uid'] in UIDS]
  self.parent=read(ROOT/'3d-viewer'/PARENT_URL)
 def bad(self):
  with self.assertRaises(AssertionError):proposed_cells(self.rows,self.parent)
 def test_actual_complete_pair_disjoint_all_ten(self):
  self.assertEqual(proposed_cells(self.rows,self.parent),CELLS)
  self.assertFalse(any(overlap(CELLS,p['coarseCells']) for p in self.parent['patches']))
  self.assertEqual(extent(CELLS,self.parent),[947.5,-1087.5,1087.5,-962.5])
 def test_old_padding_really_overlaps_hullett(self):
  self.assertEqual([p['id'] for p in self.parent['patches'] if overlap([531,0,559,26],p['coarseCells'])],['government-native-central-hullett-house'])
 def test_missing_original(self):self.rows.pop();self.bad()
 def test_duplicate_uid(self):self.rows[1]['uid']=self.rows[0]['uid'];self.bad()
 def test_source_outside_proposed_cell(self):self.rows[0]['native']['model']['worldBounds'][1][2]=-960;self.bad()
 def test_reduced_transition_truncated(self):self.rows[0]['native']['model']['worldBounds'][1][2]=-969;self.bad()
 def test_nonfinite_bounds(self):self.rows[0]['native']['model']['worldBounds'][0][0]=float('nan');self.bad()
 def test_new_overlapping_child(self):self.parent['patches'][0]['coarseCells']=CELLS;self.bad()
 def test_missing_current_child(self):self.parent['patches'].pop();self.bad()
 def test_duplicate_child_identity(self):self.parent['patches'][1]['id']=self.parent['patches'][0]['id'];self.bad()
 def test_changed_grid(self):self.parent['meta']['georef']['aE']=10;self.bad()
 def test_zero_width_source(self):self.rows[0]['native']['model']['worldBounds'][1][0]=self.rows[0]['native']['model']['worldBounds'][0][0];self.bad()

class CompleteGeometryCases(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  from exact_packed_world_geometry_20261009 import decode_original_world_triangles
  from lippo_actual_render_float32_diagnostic_20261010 import reconstruct
  cls.rows=[r for r in read(DOC/'selection.json.gz')['rows'] if r['uid'] in UIDS]
  cls.parent=read(ROOT/'3d-viewer'/PARENT_URL)
  literal=read(DOC/'literal-production-geometry.json.gz');streams,_=reconstruct(read(DOC/'actual-render-attribute-geometry.json.gz'),literal)
  cls.representations={kind:{u:t for u,t in actors.items() if u in UIDS} for kind,actors in streams.items()}
  cls.representations['completeOriginal']={r['uid']:decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes()) for r in cls.rows}
  cls.representations['literalWorldFloat64']={r['uid']:np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)] for r in literal['rows'] if r['uid'] in UIDS}
 def bad(self,representations):
  with self.assertRaises(AssertionError):complete_geometry_containment(self.rows,self.parent,representations)
 def test_complete_original_literal_both_f32_streams(self):
  proof=complete_geometry_containment(self.rows,self.parent,self.representations)
  self.assertEqual(len(proof['completeFourRepresentationBindings']),8)
 def test_missing_gpu_reconstruction(self):
  a=dict(self.representations);a.pop('explicitFloat32ModelMatrixWorldPosition');self.bad(a)
 def test_missing_original_face(self):
  a=copy.deepcopy(self.representations);u=sorted(UIDS)[0];a['completeOriginal'][u]=a['completeOriginal'][u][:-1];self.bad(a)
 def test_actual_render_outside_core(self):
  a=copy.deepcopy(self.representations);a['explicitFloat32ModelMatrixWorldPosition'][sorted(UIDS)[0]][0,0,2]=-960;self.bad(a)
 def test_nonfinite_literal(self):
  a=copy.deepcopy(self.representations);a['literalWorldFloat64'][sorted(UIDS)[0]][0,0,0]=float('nan');self.bad(a)
if __name__=='__main__':unittest.main()
