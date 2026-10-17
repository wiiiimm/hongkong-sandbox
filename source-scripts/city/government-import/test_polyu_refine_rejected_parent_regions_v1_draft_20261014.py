from fractions import Fraction as F
import copy,unittest
from polyu_refine_rejected_parent_regions_v1_draft_20261014 import refine
P=[[0,3,0],[4,5,0],[0,3,4]]
def pack(t,parent,shared):return [dict(packedTriplet=[[float(v)for v in p]for p in t],syntheticOnly=True)]
def yes(t,w):return dict(eligible=True)
def no(t,w):return dict(eligible=False,actualNegativeMustRemain=True)
class Refinement(unittest.TestCase):
 def test_complete_acceptance_preserves_inputs_and_plane(self):
  original=copy.deepcopy(P);r=refine(P,P,{},packer=pack,checker=yes);self.assertEqual(P,original);self.assertEqual(r['unresolvedIdealTwiceProjectedArea'],0)
  self.assertEqual(r['requiredIdealTwiceProjectedArea'],16)
 def test_rejected_full_triangle_is_not_returned(self):
  def check(t,w):return dict(eligible=max(p[0]for p in t)-min(p[0]for p in t)<=2)
  r=refine(P,P,{},packer=pack,checker=check,max_depth=8);self.assertGreater(r['attempts'],1);self.assertFalse(r['completeAttemptJournal'][0]['eligible']);self.assertTrue(all(check(a['packing']['packedTriplet'],{})['eligible']for a in r['acceptedPieces']))
 def test_depth_stop_preserves_negative_and_complete_area(self):
  r=refine(P,P,{},packer=pack,checker=no,max_depth=2);self.assertEqual(r['acceptedPieces'],[]);self.assertEqual(r['unresolvedIdealTwiceProjectedArea'],16)
 def test_budget_stop_accounts_entire_remaining_queue(self):
  r=refine(P,P,{},packer=pack,checker=no,max_attempts=1);self.assertEqual(r['attempts'],1);self.assertEqual(r['unresolvedIdealTwiceProjectedArea'],16)
 def test_empty_packing_has_no_eligibility(self):
  r=refine(P,P,{},packer=lambda*t:[],checker=yes,max_depth=0);self.assertFalse(r['acceptedPieces']);self.assertEqual(r['unresolvedIdealTwiceProjectedArea'],16)
 def test_mixed_pieces_never_partially_admit_failed_attempt(self):
  def split(t,p,s):return [dict(packedTriplet=[[float(v)for v in q]for q in t]),dict(packedTriplet=[[float(q[0])+10,float(q[1]),float(q[2])]for q in t])]
  r=refine(P,P,{},packer=split,checker=lambda t,w:dict(eligible=t[0][0]<10),max_depth=0);self.assertFalse(r['acceptedPieces'])
 def test_wrong_source_plane_rejected(self):
  bad=copy.deepcopy(P);bad[0][1]+=1
  with self.assertRaises(AssertionError):refine(bad,P,{},packer=pack,checker=yes)
 def test_deterministic_order_and_true_source_subdivision(self):
  a=refine(P,P,{},packer=pack,checker=no,max_depth=3);b=refine(P,P,{},packer=pack,checker=no,max_depth=3);self.assertEqual(a,b)
  for row in a['completeAttemptJournal']:
   for x,y,z in row['idealTriangle']:self.assertEqual(y,3+x/2)
 def test_nonconvex_saved_region_rejected(self):
  q=[[0,3,0],[4,5,0],[1,F(7,2),1],[0,3,4]]
  with self.assertRaises(AssertionError):refine(q,P,{},packer=pack,checker=yes)
if __name__=='__main__':unittest.main()
