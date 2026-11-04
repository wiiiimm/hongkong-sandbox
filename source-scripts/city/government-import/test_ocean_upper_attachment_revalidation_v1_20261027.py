import unittest
from copy import deepcopy
from ocean_upper_attachment_revalidation_v1_20261027 import validate_binding
class AttachmentBindings(unittest.TestCase):
 def setUp(self):
  modes=['original','literal','leftF32','balancedF32'];hashes={'upper':'a','podium':'b'}
  self.old=dict(supportedUid='upper',supportUid='podium',sourceSHA256ByUid=hashes,rows=[dict(mode=m,support=dict(unresolved=[dict(position=[1,2,3],classification='rim')]),sourceWorldSHA256ByUid=hashes)for m in modes]);self.new=deepcopy(self.old)
  self.attachment=dict(targetUid='upper',sourceSHA256ByUid=hashes,rows=[dict(mode=m,disconnected=0,witnesses=1,finiteAttachmentPaths=1,pathsWithinEndpointHeight=1)for m in modes])
  self.contacts=dict(sourceSHA256ByUid=hashes,rows=[dict(mode=m,sourceWorldSHA256ByUid=hashes)for m in modes])
 def test_same_exact_witnesses_and_worlds_reuse(self):self.assertTrue(validate_binding(self.old,self.new,self.attachment,self.contacts))
 def test_same_count_changed_witness_rejected(self):
  self.new['rows'][0]['support']['unresolved'][0]['position'][0]+=1e-10
  with self.assertRaises(AssertionError):validate_binding(self.old,self.new,self.attachment,self.contacts)
 def test_changed_world_or_invalid_attachment_rejected(self):
  self.new['rows'][0]['sourceWorldSHA256ByUid']={'upper':'changed','podium':'b'}
  with self.assertRaises(AssertionError):validate_binding(self.old,self.new,self.attachment,self.contacts)
  self.new=deepcopy(self.old);self.attachment['rows'][1]['pathsWithinEndpointHeight']=0
  with self.assertRaises(AssertionError):validate_binding(self.old,self.new,self.attachment,self.contacts)
if __name__=='__main__':unittest.main()
