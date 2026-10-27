import copy,unittest
from north_pair_retained_terrain_review_v1_20261027 import terrain_rows,PAIRS
class TerrainOnly(unittest.TestCase):
 def setUp(self):
  self.current={u:dict(sha256=u)for pair in PAIRS.items()for u in pair}
  self.rows=[dict(uid=u,passed=u not in PAIRS,triangles=2,vertices=4,terrain=dict(newlyWhollyBuried=0,newlyUpwardWhollyBuried=0,maximumBurialIncrease=0,minimumGapBefore=7,minimumGapAfter=7,whollyBuriedBefore=0,whollyBuriedAfter=0,upwardWhollyBuriedBefore=0,upwardWhollyBuriedAfter=0))for u in [*PAIRS,*[f'other/{i}'for i in range(65)]]]
  self.n=dict(nativeRows=self.rows,requiredNativeUids=[r['uid']for r in self.rows],forms=786,basicFlags=[])
  self.c={u:dict(nativeUid=u,supportUid=s,proposalTerrainNonRegressionProved=True,existingNativeReaccepted=False,rawSupportPolicyPassed=False,rawNativeRegression=copy.deepcopy(next(r for r in self.rows if r['uid']==u)),rows=[dict(uid=k,sourceSHA256=k,exactRenderedTerrainMultisetUnchanged=True,rootCoarseMaskUnchangedAcrossCompleteBounds=True)for k in [u,s]])for u,s in PAIRS.items()}
 def run_review(self):return terrain_rows(self.n,self.c,self.current)
 def test_preserves_negatives(self):
  before=copy.deepcopy(self.n);rows=self.run_review();self.assertEqual(self.n,before);self.assertEqual(sum(not r['rawMeshAndSupportReview']['passed']for r in rows),2);self.assertTrue(all(not r['existingSupportReapproved']for r in rows))
 def test_changed_source(self):
  self.current[next(iter(PAIRS.values()))]['sha256']='changed'
  with self.assertRaises(AssertionError):self.run_review()
 def test_missing_support(self):
  self.c[next(iter(PAIRS))]['rows'].pop()
  with self.assertRaises(AssertionError):self.run_review()
 def test_changed_terrain(self):
  self.c[next(iter(PAIRS))]['rows'][0]['exactRenderedTerrainMultisetUnchanged']=False
  with self.assertRaises(AssertionError):self.run_review()
 def test_extra_failure(self):
  self.rows[-1]['passed']=False
  with self.assertRaises(AssertionError):self.run_review()
 def test_new_burial(self):
  self.rows[-1]['terrain']['newlyWhollyBuried']=1
  with self.assertRaises(AssertionError):self.run_review()
 def test_changed_warning(self):
  self.rows[0]['terrain']['minimumGapAfter']=8
  with self.assertRaises(AssertionError):self.run_review()
 def test_missing_native(self):
  self.rows.pop()
  with self.assertRaises(AssertionError):self.run_review()
if __name__=='__main__':unittest.main()
