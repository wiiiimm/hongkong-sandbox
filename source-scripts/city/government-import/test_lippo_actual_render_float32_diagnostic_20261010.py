from copy import deepcopy
import unittest
from run import ROOT,read
from lippo_actual_render_float32_diagnostic_20261010 import reconstruct,verify
from lippo_current_bound_six_roof_identity_v1_20261010 import DOC
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

class ActualRender(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.export=read(DOC.parent/'government-xl-lippo-actual-render-attributes-and-float32-world-diagnostic-v1-20261010/actual-render-attribute-geometry.json.gz')
  cls.literal=read(DOC/'literal-production-geometry.json.gz')
  cls.originals={r['uid']:decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes()) for r in read(DOC/'selection.json.gz')['rows']}
  cls.forms=read(DOC/'current-inputs.json.gz')['forms'];cls.primary=read(DOC/'exact-current-primary.json')['features']
 def bad(self,change):
  e=deepcopy(self.export);change(e)
  with self.assertRaises(AssertionError):reconstruct(e,self.literal)
 def test_complete_actual_independent_streams(self):
  s,p=reconstruct(self.export,self.literal);self.assertEqual(len(p),6)
  self.assertEqual(sum(len(a) for a in s['roundedWorldPositionFloat32'].values()),29580)
 def test_complete_exact_roles_and_foreign_scope(self):
  p=verify(self.export,self.literal,self.originals,self.forms,self.primary)
  self.assertEqual(len(p['completeRepresentationChecks']),2);self.assertFalse(p['currentIdentityAccepted'])
 def test_missing_source(self):self.bad(lambda e:e['rows'].pop())
 def test_duplicate_source(self):self.bad(lambda e:e['rows'].__setitem__(1,e['rows'][0]))
 def test_wrong_source_hash(self):self.bad(lambda e:e['rows'][0].__setitem__('sourceSHA256','0'*64))
 def test_nonfinite_attribute(self):self.bad(lambda e:e['rows'][0]['actualRenderMeshes'][0]['completeOriginalVertexAttribute'].__setitem__(0,float('nan')))
 def test_non_f32_attribute(self):self.bad(lambda e:e['rows'][0]['actualRenderMeshes'][0]['completeOriginalVertexAttribute'].__setitem__(0,.10000000000000001))
 def test_wrong_attribute_type(self):self.bad(lambda e:e['rows'][0]['actualRenderMeshes'][0].__setitem__('positionAttributeArrayType','Float64Array'))
 def test_missing_mesh(self):self.bad(lambda e:e['rows'][0]['actualRenderMeshes'].clear())
 def test_index_omission(self):self.bad(lambda e:e['rows'][0]['actualRenderMeshes'][0]['completeOriginalIndex'].pop())
 def test_negative_index(self):self.bad(lambda e:e['rows'][0]['actualRenderMeshes'][0]['completeOriginalIndex'].__setitem__(0,-1))
 def test_changed_literal_matrix(self):self.bad(lambda e:e['rows'][0]['actualRenderMeshes'][0]['matrixWorldFloat64'].__setitem__(12,999.0))
 def test_changed_f32_uniform(self):self.bad(lambda e:e['rows'][0]['actualRenderMeshes'][0]['modelMatrixUniformFloat32'].__setitem__(12,999.0))
 def test_changed_f32_world(self):self.bad(lambda e:e['rows'][0]['explicitFloat32ModelMatrixWorldPosition'].__setitem__(1,999.0))
 def test_changed_rounded_world(self):self.bad(lambda e:e['rows'][0]['roundedWorldPositionFloat32'].__setitem__(1,999.0))
 def test_changed_float64_world(self):self.bad(lambda e:e['rows'][0]['worldPositionFloat64'].__setitem__(1,999.0))
 def test_missing_normal(self):self.bad(lambda e:e['rows'][0]['actualRenderMeshes'][0]['completeNormalAttribute'].pop())
 def test_missing_colour(self):self.bad(lambda e:e['rows'][0]['actualRenderMeshes'][0]['completeColorAttribute'].pop())
 def test_missing_final_fence(self):self.bad(lambda e:e.__setitem__('startAndEndInputHashesVerified',False))
 def test_non_affine_matrix(self):self.bad(lambda e:e['rows'][0]['actualRenderMeshes'][0]['matrixWorldFloat64'].__setitem__(3,.1))

if __name__=='__main__':unittest.main()
