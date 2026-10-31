import copy,unittest
from north_pair_install_transition_v1_20261027 import verify,SOURCES,EXISTING
class Transition(unittest.TestCase):
 def setUp(self):
  self.before=[dict(uid=EXISTING,sha256='original',supportDependencies=['preserve'])]+[dict(uid='old/'+str(i))for i in range(6988)]
  self.new=[dict(uid=u,sha256=s)for u,s in SOURCES.items()];self.group=sorted([*SOURCES,EXISTING]);self.after=copy.deepcopy(self.before);self.after[0]['activationGroup']=self.group;self.after+=self.new
 def test_exact_transition(self):self.assertTrue(verify(self.before,self.after,self.new,self.group))
 def test_source_edit_rejected(self):
  self.after[0]['sha256']='changed'
  with self.assertRaises(AssertionError):verify(self.before,self.after,self.new,self.group)
 def test_support_edit_rejected(self):
  self.after[0]['supportDependencies']=[]
  with self.assertRaises(AssertionError):verify(self.before,self.after,self.new,self.group)
 def test_other_entry_edit_rejected(self):
  self.after[1]['reviewed']=True
  with self.assertRaises(AssertionError):verify(self.before,self.after,self.new,self.group)
 def test_missing_old_rejected(self):
  self.after.pop(1)
  with self.assertRaises(AssertionError):verify(self.before,self.after,self.new,self.group)
 def test_wrong_new_source_rejected(self):
  self.new[0]['sha256']='changed'
  with self.assertRaises(AssertionError):verify(self.before,self.after,self.new,self.group)
if __name__=='__main__':unittest.main()
