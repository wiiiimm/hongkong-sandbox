"""Hermetic real installed-catalogue fixtures and adverse metadata proofs."""
import copy
import unittest
from run import ROOT,read,digest
from verified_installed_dependency_metadata_20261010 import proposal,verify
class InstalledDependencyMetadata(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  doc=ROOT/'docs/astra-city/government-import/government-xl-all-installed-dependency-metadata-proposal-v2-20261010'
  cls.packet=read(doc/'proposal.json.gz');receipt=read(doc/'result.json');p=str((doc/'proposal.json.gz').relative_to(ROOT));pins=[r for r in receipt['evidenceRefs'] if r['path']==p];assert len(pins)==1 and pins[0]['sha256']==digest((doc/'proposal.json.gz').read_bytes())
  cls.before=cls.packet['beforeCatalogues'];cls.after=cls.packet['afterCatalogues'];cls.forms={a['uid']:a['currentViewer'] for a in cls.packet['actors']};cls.assets={a['uid']:dict(sha256=a['asset']['sha256'],bytes=a['assetBytes']) for a in cls.packet['actors']};cls.reviews={a['uid']:(a['review']['state'],a['review']['sourceSHA256']) for a in cls.packet['actors']}
  cls.first=cls.packet['changes'][0];cls.owner=cls.first['uid'];cls.support=cls.first['supportUID'];cls.path=cls.first['catalogue']
 def run_proposal(self,before=None,reviews=None,forms=None,assets=None):return proposal(self.before if before is None else before,self.reviews if reviews is None else reviews,self.forms if forms is None else forms,self.assets if assets is None else assets)
 def owner_entry(self,before):return next(e for e in before[self.path]['models'] if e['uid']==self.owner)
 def test_real210_exact_edges(self):
  p=verify(self.before,self.after,self.reviews,self.forms,self.assets);self.assertEqual(len(p['changes']),210);self.assertEqual(len({r['uid'] for r in p['changes']}),206);self.assertEqual(p['changes'],self.packet['changes'])
 def test_no_source_physics_or_review_credit(self):
  p=self.run_proposal()
  for k in ['newlyInstalled','sourceGeometryChanges','reviewStateChanges']:self.assertEqual(p[k],0)
  self.assertFalse(p['identityAcceptance']);self.assertFalse(p['physicalAcceptance'])
 def test_all_source_and_pose_fields_preserved(self):
  for path,before in self.before.items():
   old=copy.deepcopy(before);new=copy.deepcopy(self.after[path])
   for cat in [old,new]:
    for e in cat['models']:e.pop('supportDependencies',None)
   self.assertEqual(old,new)
 def test_all_original_edge_directions_preserved(self):
  for path,cat in self.before.items():
   for before,after in zip(cat['models'],self.after[path]['models']):
    for x,y in zip(before.get('supportDependencies',[]),after.get('supportDependencies',[])):
     self.assertEqual(x if isinstance(x,str) else x['uid'],y if isinstance(y,str) else y['uid'])
 def test_candidate_support_missing_rejected(self):
  before=copy.deepcopy(self.before);e=self.owner_entry(before);e['supportDependencies'][self.first['dependencyIndex']]['uid']='landsd/99999999:0'
  with self.assertRaises(AssertionError):self.run_proposal(before=before)
 def test_self_edge_rejected(self):
  before=copy.deepcopy(self.before);self.owner_entry(before)['supportDependencies'][self.first['dependencyIndex']]['uid']=self.owner
  with self.assertRaises(AssertionError):self.run_proposal(before=before)
 def test_wrong_support_csuid_rejected(self):
  before=copy.deepcopy(self.before);self.owner_entry(before)['supportDependencies'][self.first['dependencyIndex']]['csuid']='wrong'
  with self.assertRaises(AssertionError):self.run_proposal(before=before)
 def test_wrong_existing_source_hash_rejected(self):
  before=copy.deepcopy(self.before);self.owner_entry(before)['supportDependencies'][self.first['dependencyIndex']]['sha256']='0'*64
  with self.assertRaises(AssertionError):self.run_proposal(before=before)
 def test_pending_owner_cannot_be_installed(self):
  r=copy.deepcopy(self.reviews);r[self.owner]=('held',r[self.owner][1])
  with self.assertRaises(AssertionError):self.run_proposal(reviews=r)
 def test_pending_support_cannot_be_installed(self):
  r=copy.deepcopy(self.reviews);r[self.support]=('held',r[self.support][1])
  with self.assertRaises(AssertionError):self.run_proposal(reviews=r)
 def test_mismatched_installed_review_rejected(self):
  r=copy.deepcopy(self.reviews);r[self.support]=('installed-verified','0'*64)
  with self.assertRaises(AssertionError):self.run_proposal(reviews=r)
 def test_changed_asset_bytes_rejected(self):
  a=copy.deepcopy(self.assets);a[self.support]['sha256']='0'*64
  with self.assertRaises(AssertionError):self.run_proposal(assets=a)
 def test_changed_asset_length_rejected(self):
  a=copy.deepcopy(self.assets);a[self.support]['bytes']+=1
  with self.assertRaises(AssertionError):self.run_proposal(assets=a)
 def test_changed_current_stable_identity_rejected(self):
  f=copy.deepcopy(self.forms);f[self.support]['buildingCSUID']='wrong'
  with self.assertRaises(AssertionError):self.run_proposal(forms=f)
 def test_changed_current_original_object_id_rejected(self):
  f=copy.deepcopy(self.forms);f[self.support]['objectId']='wrong'
  with self.assertRaises(AssertionError):self.run_proposal(forms=f)
 def test_duplicate_runtime_actor_rejected(self):
  b=copy.deepcopy(self.before);b[self.path]['models'].append(copy.deepcopy(self.owner_entry(b)))
  with self.assertRaises(AssertionError):self.run_proposal(before=b)
 def test_changed_root_translation_rejected(self):
  after=copy.deepcopy(self.after);after[self.path]['rootTranslation'][0]+=.001
  with self.assertRaises(AssertionError):verify(self.before,after,self.reviews,self.forms,self.assets)
 def test_changed_source_record_rejected(self):
  after=copy.deepcopy(self.after);self.owner_entry(after)['sha256']='0'*64
  with self.assertRaises(AssertionError):verify(self.before,after,self.reviews,self.forms,self.assets)
 def test_added_edge_rejected(self):
  after=copy.deepcopy(self.after);self.owner_entry(after)['supportDependencies'].append(dict(uid=self.support,state='installed'))
  with self.assertRaises(AssertionError):verify(self.before,after,self.reviews,self.forms,self.assets)
 def test_existing_fallback_and_legacy_relations_retained(self):
  p=self.run_proposal()
  for path,cat in self.before.items():
   for before,after in zip(cat['models'],p['catalogues'][path]['models']):
    for x,y in zip(before.get('supportDependencies',[]),after.get('supportDependencies',[])):
     if not isinstance(x,dict) or x.get('state') not in ['candidate','installed']:self.assertEqual(x,y)
 def test_cycle_cannot_be_relabelled(self):
  b=copy.deepcopy(self.before)
  for cat in b.values():
   for e in cat['models']:
    if e['uid']==self.support:e['supportDependencies']=[dict(uid=self.owner,state='candidate')]
  with self.assertRaises(AssertionError):self.run_proposal(before=b)
if __name__=='__main__':unittest.main()
