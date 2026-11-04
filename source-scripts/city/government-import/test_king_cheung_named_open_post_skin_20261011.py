import copy, gzip, hashlib, json, unittest
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from run import ROOT
from king_cheung_named_open_post_skin_20261011 import IDS, verify, cycle
P=ROOT/'docs/astra-city/government-import/government-xl-king-cheung-95691-current-actual-ground-capture-v1-20261011/complete-four-stream-ground-inputs.json.gz'
class NamedPostTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=json.load(gzip.open(P,'rt'))
 def setUp(self):
  self.t=np.asarray(self.data['completeWorldStreams']['providerOriginal']['completeWorldTriangles'],dtype='<f8')[IDS];self.g=np.asarray(self.data['completeDrawnGround'],dtype='<f8')
 def binding(self,t,g):return dict(completePartSHA256=hashlib.sha256(t.tobytes()).hexdigest(),completeGroundSHA256=hashlib.sha256(g.tobytes()).hexdigest())
 def run_role(self,t=None,g=None,**kw):
  t=self.t if t is None else t;g=self.g if g is None else g;b=self.binding(t,g)
  opts=dict(source_face_ids=IDS,interpreted_role='King Cheung original ancillary isolated post43 lateral skin',expected_binding=b,current_binding=b);opts.update(kw)
  return verify(t,g,**opts)
 def rejected(self,t=None,g=None,**kw):
  with self.assertRaises(AssertionError):self.run_role(t,g,**kw)
 def test_complete_original(self):self.assertTrue(self.run_role()['wholeUpperPerimeterStrictlyExposed'])
 def test_actual_literal(self):self.assertTrue(self.run_role(np.asarray(self.data['completeWorldStreams']['actualLiteral']['completeWorldTriangles'],dtype='<f8')[IDS])['everyLateralFaceCrossesActualGrade'])
 def test_left_f32(self):self.run_role(np.asarray(self.data['completeWorldStreams']['explicitLeftAssociatedF32ModelMatrix']['completeWorldTriangles'],dtype='<f8')[IDS])
 def test_balanced_f32(self):self.run_role(np.asarray(self.data['completeWorldStreams']['explicitBalancedF32ModelMatrix']['completeWorldTriangles'],dtype='<f8')[IDS])
 def test_no_volume_support_or_install_credit(self):
  r=self.run_role();self.assertFalse(r['closedSolidCertified']);self.assertFalse(r['canopySupportCredit']);self.assertFalse(r['installationApproved'])
 def test_wrong_face_ids(self):self.rejected(source_face_ids=list(range(2811,2819)))
 def test_foreign_role(self):self.rejected(interpreted_role='unrelated foreign post')
 def test_stale_ground(self):b=self.binding(self.t,self.g);b['completeGroundSHA256']='0'*64;self.rejected(expected_binding=b,current_binding=b)
 def test_stale_current(self):self.rejected(current_binding={})
 def test_source_changed_without_fresh_binding(self):
  t=self.t.copy();t[0,0,0]+=1;self.rejected(t,expected_binding=self.binding(self.t,self.g),current_binding=self.binding(self.t,self.g))
 def test_omitted_face(self):self.rejected(self.t[:-1])
 def test_duplicate_face(self):t=self.t.copy();t[0]=t[1];self.rejected(t)
 def test_collapsed_face(self):t=self.t.copy();t[0,0]=t[0,1];self.rejected(t)
 def test_open_sheet(self):t=self.t.copy();t[0,:,0]+=1;self.rejected(t)
 def test_disconnected_upper_rim(self):t=self.t.copy();t[0,0,1]+=.01;self.rejected(t)
 def test_no_grade(self):g=self.g.copy();g[:,:,1]=12;self.rejected(g=g)
 def test_hidden_upper_rim(self):g=self.g.copy();g[:,:,1]=17;self.rejected(g=g)
 def test_only_bottom_boundary_contact(self):g=self.g.copy();g[:,:,1]=self.t[:,:,1].min();self.rejected(g=g)
 def test_nonfinite(self):t=self.t.copy();t[0,0,0]=np.nan;self.rejected(t)
 def test_branched_ring(self):
  pts=[(F(0),F(14),F(0)),(F(1),F(14),F(0)),(F(1),F(14),F(1)),(F(0),F(14),F(1))]
  with self.assertRaises(AssertionError):cycle([(pts[0],pts[1]),(pts[0],pts[2]),(pts[0],pts[3]),(pts[1],pts[2])],nodes=4)
 def test_crossed_ring(self):
  p=[(F(0),F(14),F(0)),(F(1),F(14),F(1)),(F(0),F(14),F(1)),(F(1),F(14),F(0))]
  with self.assertRaises(AssertionError):cycle([tuple(sorted((a,b)))for a,b in zip(p,p[1:]+p[:1])],nodes=4)
if __name__=='__main__':unittest.main()
