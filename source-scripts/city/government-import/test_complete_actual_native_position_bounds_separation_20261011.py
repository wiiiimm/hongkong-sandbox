import copy,unittest,math
from complete_actual_native_position_bounds_separation_20261011 import verify,strict_planar_separation,OWNED_MODES,NATIVE_MODES
class ActualWholeBoundsTests(unittest.TestCase):
 def fixture(self):
  owned={m:[[0,0,0],[1,1,1]] for m in OWNED_MODES};mesh=dict(wholePositionVerticesIncludingUnused=True,completePositionVertices=7,completeIndexedFaces=2)
  for field in NATIVE_MODES.values():mesh[field]=[[2,0,0],[3,1,1]]
  actor=dict(uid='landsd/1:0',sourceSHA256='1'*64,sourceFacesOmitted=0,wholeUnusedPositionVerticesIncluded=True,actualRenderMeshes=[mesh],completePositionVertices=7,completeFaces=2)
  for field in NATIVE_MODES.values():actor[field]=copy.deepcopy(mesh[field])
  return owned,[actor]
 def reject(self,fn):
  a,b=self.fixture();fn(a,b)
  with self.assertRaises((AssertionError,KeyError,ValueError,TypeError)):verify(a,b)
 def test_all_twelve_declared_mode_pairs(self):a,b=self.fixture();r=verify(a,b);self.assertEqual(len(r['rows'][0]['completePairProofs']),12);self.assertFalse(r['physicalAccepted'])
 def test_closed_touch_rejected(self):
  with self.assertRaises(AssertionError):strict_planar_separation([[0,0,0],[1,1,1]],[[1,0,0],[2,1,1]])
 def test_tiny_exact_positive_gap(self):self.assertEqual(strict_planar_separation([[0,0,0],[0,1,1]],[[2**-100,0,0],[1,1,1]])['exactPositiveGapM'],'1/1267650600228229401496703205376')
 def test_Y_gap_not_planar_separation(self):
  with self.assertRaises(AssertionError):strict_planar_separation([[0,0,0],[1,1,1]],[[0,2,0],[1,3,1]])
 def test_z_separation(self):self.assertEqual(strict_planar_separation([[0,0,0],[1,1,1]],[[0,0,2],[1,1,3]])['axis'],2)
 def test_missing_owned_stream(self):self.reject(lambda a,b:a.pop('providerOriginal'))
 def test_unused_vertex_omitted(self):self.reject(lambda a,b:b[0].update(completePositionVertices=6))
 def test_false_full_position_flag(self):self.reject(lambda a,b:b[0].update(wholeUnusedPositionVerticesIncluded=False))
 def test_omitted_native_face(self):self.reject(lambda a,b:b[0].update(sourceFacesOmitted=1))
 def test_duplicate_actor(self):self.reject(lambda a,b:b.append(copy.deepcopy(b[0])))
 def test_mesh_union_incorrect(self):self.reject(lambda a,b:b[0].update(completeLiteralBounds=[[20,0,0],[30,1,1]]))
 def test_F32_touch_not_inherited_from_literal(self):
  def change(a,b):
   key='completeBalancedF32Bounds';b[0][key]=[[1,0,0],[2,1,1]];b[0]['actualRenderMeshes'][0][key]=copy.deepcopy(b[0][key])
  self.reject(change)
 def test_nonfinite_position_bounds(self):self.reject(lambda a,b:a['actualLiteral'][0].__setitem__(0,float('nan')))
 def test_inverted_bounds(self):self.reject(lambda a,b:a['actualLiteral'][0].__setitem__(0,2))
if __name__=='__main__':unittest.main()
