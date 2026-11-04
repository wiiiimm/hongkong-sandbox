import copy,unittest
from revalidate_unchanged_original_identity_review_v1_20261027 import identical_identity_facts
class Revalidation(unittest.TestCase):
 def setUp(self):
  self.old=dict(sourceSHA256='source',sourceFormSHA256='form',reasons=['extent'],exactRouteManifestSHA256='old',exactRouteTileHashes={'tile':'old'},originalOwnership={'sourceGraphVerified':True},exactCurrentComponentRoute={'qualified':True},freshCurrentIdentity={'exactObjectAndCSUID':True},exactWholeCellCoverage={'covered':True});self.new=copy.deepcopy(self.old);self.new.update(exactRouteManifestSHA256='new',exactRouteTileHashes={'tile':'new'})
 def test_only_routing_may_change(self):self.assertEqual(identical_identity_facts(self.old,self.new),['exactRouteManifestSHA256','exactRouteTileHashes'])
 def test_source_change_rejects(self):
  self.new['sourceSHA256']='different'
  with self.assertRaises(AssertionError):identical_identity_facts(self.old,self.new)
 def test_identity_measurement_change_rejects(self):
  self.new['freshCurrentIdentity']['centroidDistance']=2
  with self.assertRaises(AssertionError):identical_identity_facts(self.old,self.new)
 def test_omitted_failure_rejects(self):
  self.new['reasons']=[]
  with self.assertRaises(AssertionError):identical_identity_facts(self.old,self.new)
 def test_missing_field_rejects(self):
  del self.new['exactWholeCellCoverage']
  with self.assertRaises(AssertionError):identical_identity_facts(self.old,self.new)
if __name__=='__main__':unittest.main()
