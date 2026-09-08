import unittest
from extend import build
class SourceExtension(unittest.TestCase):
 def test_order_independent_extension_preserves_existing_rows(self):
  old={'snapshotId':'old','parts':[{'uid':'a','candidate':{'sha256':'original'},'sourceProgress':'installed'}]};addition={'uid':'b','candidate':{'sha256':'new'},'sourceProgress':'prepared-for-review'}
  one=build(old,[{'parts':[addition]}]);two=build(old,[{'parts':[old['parts'][0],addition]}])
  self.assertEqual(one,two);self.assertEqual(one['parts'][0],old['parts'][0]);self.assertEqual(len(one['parts']),2)
 def test_conflicting_existing_source_requires_explicit_new_review(self):
  old={'snapshotId':'old','parts':[{'uid':'a','candidate':{'sha256':'original'}}]}
  with self.assertRaisesRegex(ValueError,'Conflicting'):build(old,[{'parts':[{'uid':'a','candidate':{'sha256':'changed'}}]}])
if __name__=='__main__':unittest.main()
