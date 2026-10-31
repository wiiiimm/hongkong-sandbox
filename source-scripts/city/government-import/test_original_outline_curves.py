import copy,math,unittest
from original_outline_curves import verify_ring,verify_polygon

class OriginalOutlineCurveTests(unittest.TestCase):
 def setUp(self):
  self.arc=[[10,0],{'c':[[0,10],[10/math.sqrt(2),10/math.sqrt(2)]]},[-10,-10],[10,0]]
  self.line=[[10*math.cos(a),10*math.sin(a)] for a in [i*math.pi/12 for i in range(7)]]+[[-10,-10],[10,0]]
 def test_actual_circle_with_straight_boundary(self):
  self.assertTrue(verify_ring(self.line,self.arc)['passed'])
 def test_reversed_and_rotated_ring(self):
  ring=list(reversed(self.line[:-1]));ring=ring[3:]+ring[:3];ring+=[ring[0]]
  self.assertTrue(verify_ring(ring,self.arc)['passed'])
 def test_radial_change_over_existing_limit(self):
  changed=copy.deepcopy(self.line);changed[3]=[v*1.0003 for v in changed[3]]
  self.assertFalse(verify_ring(changed,self.arc)['passed'])
 def test_opposite_arc_is_not_same_circle_path(self):
  changed=copy.deepcopy(self.line)
  for p in changed[1:6]:p[1]=-p[1]
  self.assertFalse(verify_ring(changed,self.arc)['passed'])
 def test_unordered_arc_vertices_rejected(self):
  changed=copy.deepcopy(self.line);changed[2],changed[3]=changed[3],changed[2]
  self.assertFalse(verify_ring(changed,self.arc)['passed'])
 def test_chord_without_arc_evidence_rejected(self):
  self.assertFalse(verify_ring([[10,0],[0,10],[-10,-10],[10,0]],self.arc)['passed'])
 def test_shifted_source_rejected(self):
  changed=[[x+.003,y+.003] for x,y in self.line]
  self.assertFalse(verify_ring(changed,self.arc)['passed'])
 def test_missing_straight_anchor_rejected(self):
  self.assertFalse(verify_ring(self.line[:-2]+[[10,0]],self.arc)['passed'])
 def test_missing_hole_rejected(self):
  self.assertFalse(verify_polygon([self.line],[self.arc,self.arc])['passed'])
 def test_exterior_hole_roles_not_exchangeable(self):
  hole=[[x*.1,y*.1] for x,y in self.line];curve=copy.deepcopy(self.arc)
  for p in curve:
   if isinstance(p,list):p[:]=[v*.1 for v in p]
   else:p['c']=[[v*.1 for v in q] for q in p['c']]
  self.assertTrue(verify_polygon([self.line,hole],[self.arc,curve])['passed'])
  self.assertFalse(verify_polygon([hole,self.line],[self.arc,curve])['passed'])
 def test_unsupported_curve_rejected(self):
  changed=copy.deepcopy(self.arc);changed[1]={'b':[[0,10],[1,2],[3,4]]}
  with self.assertRaisesRegex(AssertionError,'unsupported-curve'):verify_ring(self.line,changed)
if __name__=='__main__':unittest.main()
