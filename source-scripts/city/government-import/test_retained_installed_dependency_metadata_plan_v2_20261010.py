import copy,unittest
from run import ROOT,read,digest
from retained_installed_dependency_metadata_plan_20261010 import EXPECTED,corrected,verify
class ExactMetadata(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  doc=ROOT/'docs/astra-city/government-import/government-xl-one-peking-retained-installed-dependency-metadata-plan-v2-20261010'
  p=doc/'proposal.json.gz';result=read(doc/'result.json');rel=str(p.relative_to(ROOT));refs=[r for r in result['evidenceRefs'] if r['path']==rel];assert len(refs)==1 and digest(p.read_bytes())==refs[0]['sha256']
  proposal=read(p);cls.entries={r['uid']:r['entry'] for r in proposal['actors']};assert len(cls.entries)==4
  assert set(cls.entries)==set(EXPECTED)|{d[0] for d in EXPECTED.values()}
 def fixtures(self):
  for uid,(target,_) in EXPECTED.items():yield self.entries[uid],self.entries[target]
 def test_actual_two_exact_corrections(self):
  for a,b in self.fixtures():
   c=corrected(a,b);self.assertTrue(verify(a,c,b));self.assertEqual(c['supportDependencies'][0]['state'],'installed');self.assertEqual(c['supportDependencies'][0]['csuid'],b['buildingCSUID'])
 def test_every_other_field_immutable(self):
  for a,b in self.fixtures():
   c=corrected(a,b);aa=copy.deepcopy(a);cc=copy.deepcopy(c);aa.pop('supportDependencies');cc.pop('supportDependencies');self.assertEqual(aa,cc)
 def test_source_hash_change_rejected(self):
  for a,b in self.fixtures():
   c=corrected(a,b);c['sha256']='0'*64
   with self.assertRaises(AssertionError):verify(a,c,b)
 def test_source_root_change_rejected(self):
  for a,b in self.fixtures():
   c=corrected(a,b);c['rootTranslation']=[0,0,0]
   with self.assertRaises(AssertionError):verify(a,c,b)
 def test_new_edge_rejected(self):
  for a,b in self.fixtures():
   c=corrected(a,b);c['supportDependencies'].append(copy.deepcopy(c['supportDependencies'][0]))
   with self.assertRaises(AssertionError):verify(a,c,b)
 def test_wrong_support_uid_rejected(self):
  for a,b in self.fixtures():
   b=copy.deepcopy(b);b['uid']='landsd/999:0'
   with self.assertRaises(AssertionError):corrected(a,b)
 def test_wrong_stable_csuid_rejected(self):
  for a,b in self.fixtures():
   b=copy.deepcopy(b);b['buildingCSUID']='wrong'
   with self.assertRaises(AssertionError):corrected(a,b)
 def test_existing_sha_binding_rejected(self):
  a=self.entries['landsd/268032:0'];b=copy.deepcopy(self.entries['landsd/101781:0']);b['sha256']='0'*64
  with self.assertRaises(AssertionError):corrected(a,b)
 def test_duplicate_dependency_rejected(self):
  for a,b in self.fixtures():
   a=copy.deepcopy(a);a['supportDependencies']*=2
   with self.assertRaises(AssertionError):corrected(a,b)
 def test_removed_fields_rejected(self):
  for a,b in self.fixtures():
   c=corrected(a,b);c.pop('publicationApproved')
   with self.assertRaises(AssertionError):verify(a,c,b)
 def test_installed_state_cannot_be_reinterpreted(self):
  for a,b in self.fixtures():
   a=copy.deepcopy(a);a['supportDependencies'][0]['state']='held'
   with self.assertRaises(AssertionError):corrected(a,b)
if __name__=='__main__':unittest.main()
