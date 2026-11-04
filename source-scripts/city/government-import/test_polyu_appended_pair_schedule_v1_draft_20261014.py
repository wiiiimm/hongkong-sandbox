import unittest
from polyu_appended_pair_schedule_v1_draft_20261014 import schedule
class Scheduling(unittest.TestCase):
 def test_all_new_old_and_new_new_once_not_old_old(self):
  ids=[0,1,3,4];hits=schedule([3,4],ids,[0,0,0,0,1,1,1,1],[0,1,2,3,0,1,2,3],3)
  self.assertEqual(hits,[(0,3),(0,4),(1,3),(1,4),(3,4)])
 def test_two_chunks_keep_new_new_pair_once(self):
  ids=[0,2,4,9];a=schedule([4],ids,[0,0,0,0],[0,1,2,3],4);b=schedule([9],ids,[0,0,0,0],[0,1,2,3],4)
  self.assertEqual(a+b,[(0,4),(2,4),(0,9),(2,9),(4,9)])
 def test_duplicate_query_hit_is_not_silently_deduplicated(self):
  with self.assertRaises(AssertionError):schedule([3],[0,3],[0,0],[0,0],3)
 def test_old_face_query_and_bad_indices_rejected(self):
  with self.assertRaises(AssertionError):schedule([2],[0,2],[0],[0],3)
  with self.assertRaises(AssertionError):schedule([3],[0,3],[1],[0],3)
if __name__=='__main__':unittest.main()
