"""Negative evidence tests for the sole named related-podium identity contract."""
import copy,unittest
from unittest.mock import patch
import miami_two_related_podium_identity_20261009 as identity
from run import ROOT,read
class ExactRelatedPodiumTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.five=identity.verify_five();cls.primary=read(identity.DOC/'related-podium-provider-context.json.gz');cls.originals=read(identity.DOC.parent/'government-xl-miami-five-grounded-originals-20261009/selection.json.gz')['rows']
 def execute(self,five=None,primary=None):
  original_read=identity.read
  def reader(path):
   if path==identity.DOC/'related-podium-provider-context.json.gz':return copy.deepcopy(primary or self.primary)
   return original_read(path)
  with patch.object(identity,'verify_five',return_value=copy.deepcopy(five or self.five)),patch.object(identity,'read',side_effect=reader):return identity.verify_collection()
 def test_original_positive_has_no_physical_exemption(self):
  p=self.execute();self.assertEqual(p['unrelatedExcessM2'],0);self.assertFalse(p['physicalAccepted']);self.assertFalse(p['installationApproved']);self.assertEqual(p['explicitRelatedUID'],identity.RELATED)
  self.assertTrue(all(not r['currentPodiumCollisionExemption'] and not r['currentPodiumTerrainExemption'] for r in p['rawRelatedExcessOverlaps']))
 def test_same_named_same_permit_actor_remains_unrelated(self):
  five=copy.deepcopy(self.five);actor=copy.deepcopy(next(r['source']['building'] for r in self.originals if r['uid']==identity.RELATED));actor['uid']='test/same-name-and-permit:0';five['allOtherCurrentFormsRetained'].append(actor)
  with self.assertRaises(AssertionError):self.execute(five=five)
 def test_unrelated_actor_in_excess_is_never_ignored(self):
  five=copy.deepcopy(self.five);actor=copy.deepcopy(next(r['source']['building'] for r in self.originals if r['uid']==identity.RELATED));actor.update(uid='test/unrelated-excess:0',name='Independent foreign actor',buildingCSUID='9999999999P20060311');five['allOtherCurrentFormsRetained'].append(actor)
  with self.assertRaises(AssertionError):self.execute(five=five)
 def test_missing_complete_original_podium_proof_rejected(self):
  five=copy.deepcopy(self.five);five['rows']=[r for r in five['rows'] if r['uid']!=identity.RELATED]
  with self.assertRaises((AssertionError,StopIteration)):self.execute(five=five)
 def test_wrong_original_podium_hash_rejected(self):
  five=copy.deepcopy(self.five);next(r for r in five['rows'] if r['uid']==identity.RELATED)['sourceSHA256']='0'*64
  with self.assertRaises(AssertionError):self.execute(five=five)
 def test_inactive_provider_podium_rejected(self):
  primary=copy.deepcopy(self.primary);next(r for r in primary['rows'] if r['uid']==identity.RELATED)['provider']['features'][0]['attributes']['Status']='Inactive'
  with self.assertRaises(AssertionError):self.execute(primary=primary)
 def test_generic_same_permit_without_podium_role_rejected(self):
  primary=copy.deepcopy(self.primary);next(r for r in primary['rows'] if r['uid']==identity.RELATED)['opStructures']['features'][0]['attributes']['OPBlockType']='Tower'
  with self.assertRaises(AssertionError):self.execute(primary=primary)
 def test_missing_required_tower_podium_permit_relation_rejected(self):
  primary=copy.deepcopy(self.primary);next(r for r in primary['rows'] if r['uid']==identity.RELATED)['opStructures']['features'].pop()
  with self.assertRaises(AssertionError):self.execute(primary=primary)
if __name__=='__main__':unittest.main()
