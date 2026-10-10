import copy,hashlib,unittest
import numpy as np
from original_triangular_opening_panel_source_role_v1_20261011 import verify,canonical

def fixture():
 inner=np.array([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]])
 outer=np.array([[-2.,-2.,0.],[4.,-2.,0.],[-2.,4.,0.]])
 host=[]
 for i in range(3):
  j=(i+1)%3;host.extend([[outer[i],outer[j],inner[j]],[outer[i],inner[j],inner[i]]])
 panel=inner.copy();panel[:,2]=.01
 return np.asarray(host+[panel]),list(zip(inner.tolist(),np.roll(inner,-1,axis=0).tolist()))
def binding(w,face,loop):return dict(completeOriginalWorldSHA256=hashlib.sha256(w.tobytes()).hexdigest(),completeOriginalFaces=len(w),sourceFace=face,completeOriginalSourceFacetSHA256=hashlib.sha256(w[face].tobytes()).hexdigest(),completeClaimedHostLoopSHA256=canonical(loop))
def run(w,loop,face=6,expected=None):return verify(w,source_face=face,host_loop_edges=loop,expected_source_binding=expected or binding(w,face,loop))

class OpeningPanelTests(unittest.TestCase):
 def test_authentic_complete_opening_positive(self):
  w,l=fixture();r=run(w,l);self.assertTrue(r['exactParallelPlanes']);self.assertFalse(r['visualRoleAccepted']);self.assertFalse(r['structuralRootCredit']);self.assertFalse(r['wholeFacetInteriorProximityCertified']);self.assertTrue(r['independentlyGroundedActualHostRequired'])
 def test_nonparallel_rejected(self):
  w,l=fixture();w[6,2,2]+=.001
  with self.assertRaises(AssertionError):run(w,l)
 def test_outside_band_rejected(self):
  w,l=fixture();w[6,:,2]=.100001
  with self.assertRaises(AssertionError):run(w,l)
 def test_fixed_boundary_inside(self):
  w,l=fixture();w[6,:,2]=.1;self.assertTrue(run(w,l)['exactParallelPlanes'])
 def test_nonrendering_rejected(self):
  w,l=fixture();w[6,2]=w[6,1]
  with self.assertRaises(AssertionError):run(w,l)
 def test_source_mutation_stale_binding_rejected(self):
  w,l=fixture();b=binding(w,6,l);w[6,:,2]+=.001
  with self.assertRaises(AssertionError):run(w,l,expected=b)
 def test_loop_mutation_stale_binding_rejected(self):
  w,l=fixture();b=binding(w,6,l);l=copy.deepcopy(l);l[0][0][0]+=.01
  with self.assertRaises(AssertionError):run(w,l,expected=b)
 def test_partial_loop_rejected(self):
  w,l=fixture()
  with self.assertRaises(AssertionError):run(w,l[:2])
 def test_duplicate_loop_edge_rejected(self):
  w,l=fixture();l[2]=l[1]
  with self.assertRaises(AssertionError):run(w,l)
 def test_hidden_second_incidence_rejected(self):
  w,l=fixture();w=np.concatenate([w,w[1:2]])
  with self.assertRaises(AssertionError):run(w,l)
 def test_branched_boundary_rejected(self):
  w,l=fixture();w=np.concatenate([w,np.array([[[0,0,0],[-1,-1,1],[-2,-1,1]]])])
  with self.assertRaises(AssertionError):run(w,l)
 def test_unrelated_host_rejected(self):
  w,l=fixture();w[6,:,0]+=10
  with self.assertRaises(AssertionError):run(w,l)
 def test_missing_host_triangle_rejected(self):
  w,l=fixture();w[1]=[[20,20,0],[21,20,0],[20,21,0]]
  with self.assertRaises(AssertionError):run(w,l)
 def test_nonfinite_rejected(self):
  w,l=fixture();w[0,0,0]=float('nan')
  with self.assertRaises(AssertionError):run(w,l)
 def test_actual_original_8434_complete_loop(self):
  from run import ROOT,read
  from exact_packed_world_geometry_20261009 import decode_original_world_triangles
  d=read(ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261011-langham-single-panel-original-host-boundary-loops-v1/diagnostic.json.gz')
  panel=next(p for p in d['allDisconnectedSinglePanels']if p['sourceFace']==8434)
  group=d['completeOriginalHostBoundaryGroups'][panel['completeReciprocalBoundaryMatches'][0]]
  p=next(r for r in d['evidenceRefs']if r['path'].endswith('.glb.gz'))
  raw=(ROOT/p['path']).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),p['sha256'])
  w=decode_original_world_triangles(raw);l=[e['originalEdge']for e in group['allOriginalHostBoundaryEdges']]
  r=run(w,l,8434);self.assertEqual(len(r['completeOriginalHostBoundaryIncidences']),3);self.assertFalse(r['structuralBridgeCredit'])

if __name__=='__main__':unittest.main()
