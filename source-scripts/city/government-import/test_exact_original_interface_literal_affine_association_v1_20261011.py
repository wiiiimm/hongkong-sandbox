import hashlib,unittest
import numpy as np
from exact_original_interface_literal_affine_association_v1_20261011 import verify,barycentric
from exact_original_shell_intersections_20261009 import rational_face

def fixtures():
 a=np.array([[0.,0.,0.],[2.,0.,0.],[0.,2.,0.]])
 b=np.array([[0.,0.,0.],[2.,0.,0.],[0.,0.,2.]])
 return a,b,a.copy(),b.copy()
def binding(values):return {n:hashlib.sha256(a.tobytes()).hexdigest()for n,a in zip(['originalFaceASHA256','originalFaceBSHA256','actualLiteralFaceASHA256','actualLiteralFaceBSHA256'],values)}
def run(values,expected=None):return verify(*values,expected_binding=expected or binding(values))

class AffineAssociationTests(unittest.TestCase):
 def test_original_line_positive(self):
  r=run(fixtures());self.assertEqual(r['completeOriginalExactInterface']['dimension'],1);self.assertTrue(r['wholeConvexOriginalInterfaceAssociationProved']);self.assertFalse(r['structuralBridgeCredit'])
 def test_literal_separation_retained(self):
  v=list(fixtures());v[3][:,2]+=.001;r=run(v);self.assertTrue(r['wholeConvexOriginalInterfaceAssociationProved']);self.assertFalse(r['actualLiteralPositiveDimensionalContact']);self.assertEqual(r['actualLiteralExactContact']['dimension'],-1)
 def test_large_separation_negative(self):
  v=list(fixtures());v[3][:,2]+=.100001;self.assertFalse(run(v)['wholeConvexOriginalInterfaceAssociationProved'])
 def test_fixed_band_boundary(self):
  v=list(fixtures());v[3][:,2]+=.1;self.assertTrue(run(v)['wholeConvexOriginalInterfaceAssociationProved'])
 def test_contact_area_all_vertices(self):
  a,b,_,_=fixtures();v=[a,a.copy(),a.copy(),a.copy()];v[3][:,2]+=.002;r=run(v);self.assertEqual(r['completeOriginalExactInterface']['dimension'],2);self.assertEqual(len(r['completeSeparateAffineInterfaceVertices']),3)
 def test_one_bad_endpoint_rejects_whole(self):
  v=list(fixtures());v[3][1,2]+=.2;self.assertFalse(run(v)['wholeConvexOriginalInterfaceAssociationProved'])
 def test_no_original_contact_rejected(self):
  v=list(fixtures());v[1][:,2]+=1
  with self.assertRaises(AssertionError):run(v)
 def test_original_point_only_rejected(self):
  a=np.array([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]])
  b=np.array([[0.,0.,0.],[-1.,0.,0.],[0.,-1.,0.]])
  with self.assertRaises(AssertionError):run([a,b,a,b])
 def test_degenerate_rejected(self):
  v=list(fixtures());v[3][2]=v[3][0]
  with self.assertRaises(AssertionError):run(v)
 def test_nonfinite_rejected(self):
  v=list(fixtures());v[3][2,0]=float('nan')
  with self.assertRaises(AssertionError):run(v)
 def test_stale_binding_rejected(self):
  v=list(fixtures());b=binding(v);v[3][:,2]+=.001
  with self.assertRaises(AssertionError):run(v,b)
 def test_interior_extrema_convex_affine_bound(self):
  v=list(fixtures());v[3][0,2]+=.05;v[3][1,2]-=.05;r=run(v);self.assertTrue(r['wholeConvexOriginalInterfaceAssociationProved']);self.assertEqual(len(r['completeSeparateAffineInterfaceVertices']),2)
 def test_barycentric_rejects_off_plane(self):
  from fractions import Fraction as F
  with self.assertRaises(AssertionError):barycentric(rational_face(fixtures()[0]),(F(0),F(0),F(1)))
 def test_barycentric_rejects_outside_face(self):
  from fractions import Fraction as F
  with self.assertRaises(AssertionError):barycentric(rational_face(fixtures()[0]),(F(3),F(0),F(0)))
 def test_actual_langham_565_selected_authored_interface(self):
  from run import ROOT,HERE,read
  from exact_packed_world_geometry_20261009 import decode_original_world_triangles
  from exact_original_shell_intersections_20261009 import intersection_points
  from exact_original_component_contacts_20261009 import contact_measure
  doc=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-langham-upper-complete-original-current-probe-v1-20261011'
  row=next(r for r in read(doc/'selection.json.gz')['rows']if r['uid']=='landsd/79318:0')
  raw=(ROOT/row['candidate']['path']).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sourceSHA256'])
  original=decode_original_world_triangles(raw)
  r=next(r for r in read(HERE/'local'/doc.name/'runtime-geometry.json.gz')['rows']if r['uid']==row['uid'])
  indices=np.asarray(r['index'],int).reshape(-1,3);literal=np.asarray(r['position']).reshape(-1,3)[indices]
  result=run([original[4592],original[8511],literal[4592],literal[8511]])
  self.assertEqual(result['completeOriginalExactInterface']['dimension'],1)
  self.assertEqual(result['actualLiteralExactContact']['dimension'],-1)
  self.assertTrue(result['wholeConvexOriginalInterfaceAssociationProved'])
  self.assertFalse(result['structuralRootCredit'])
  self.assertLess(float(result['maxExactSquaredAffineSeparationM2'].split('/')[0])/float(result['maxExactSquaredAffineSeparationM2'].split('/')[-1]),1e-20)
  actualdoc=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261011-langham-two-current-render-attribute-capture-v1'
  actual=next(r for r in read(actualdoc/'actual-render-attributes.json.gz')['rows']if r['uid']==row['uid'])
  for key in ['completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:
   w=np.asarray(actual[key]).reshape(-1,3)[indices]
   points=intersection_points(rational_face(w[4592]),rational_face(w[8511]))
   self.assertTrue(points);self.assertGreater(contact_measure(points)['dimension'],0)

if __name__=='__main__':unittest.main()
