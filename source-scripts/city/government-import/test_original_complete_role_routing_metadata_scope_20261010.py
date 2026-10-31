import copy,unittest
from original_complete_role_routing_metadata_scope_20261010 import role_boundaries,verify_role_boundaries

class CompleteRoleMetadata(unittest.TestCase):
 def fixture(self):
  u=['landsd/75697:0'];candidate_ref={'path':'docs/astra-city/government-import/test/terrain-candidates.json','sha256':'c'*64};manifest_ref={'path':'3d-viewer/city/data/manifest.json','sha256':'d'*64};e={'url':'city/data/remote.json','source':{'rawOriginal':{'path':'archival.bin','sha256':'a'*64}}}
  role=dict(uids=u,independentPhysicalChecksPassed=True,unresolvedIndependentPhysicalReasons=[],installationApproved=False,publication=False,sourceGeometryChanges=0,completeOriginalFaces=2160,completeOriginalComponents=4,manifestSHA256='d'*64,evidenceRefs=[candidate_ref,manifest_ref],completeCurrentTerrainRouting=[{'entry':e,'asset':{'path':'3d-viewer/city/data/remote.json','sha256':'b'*64},'testedBounds':[[10,10,12,12]]}]);manifest={'terrainPatches':[copy.deepcopy(e)]};c=[dict(uids=u,path='source-scripts/city/government-import/local/test/terrain.json',sha256='e'*64,bounds=[0,0,2,2],triangles=602)];kw=dict(candidate_ref=candidate_ref,manifest_ref=manifest_ref,expected_uids=u);return role,manifest,c,kw
 def test_only_provenance(self):
  r,m,c,k=self.fixture();p=role_boundaries(r,m,c,**k);self.assertEqual(verify_role_boundaries(r,m,c,p,**k),{'/completeCurrentTerrainRouting/0/entry/source'})
 def test_wrong_uid(self):
  r,m,c,k=self.fixture();k['expected_uids']=['landsd/1:0']
  with self.assertRaises(AssertionError):role_boundaries(r,m,c,**k)
 def test_missing_pinned_candidate(self):
  r,m,c,k=self.fixture();r['evidenceRefs']=r['evidenceRefs'][1:]
  with self.assertRaises(AssertionError):role_boundaries(r,m,c,**k)
 def test_wrong_manifest(self):
  r,m,c,k=self.fixture();k['manifest_ref']={**k['manifest_ref'],'sha256':'f'*64}
  with self.assertRaises(AssertionError):role_boundaries(r,m,c,**k)
 def test_candidate_touch(self):
  r,m,c,k=self.fixture();c[0]['bounds']=[0,0,10,10]
  with self.assertRaises(AssertionError):role_boundaries(r,m,c,**k)
 def test_wrong_candidate_path(self):
  r,m,c,k=self.fixture();k['candidate_ref']={**k['candidate_ref'],'path':'docs/astra-city/core-source.json'}
  with self.assertRaises(AssertionError):role_boundaries(r,m,c,**k)
 def test_omitted_routing_asset(self):
  r,m,c,k=self.fixture();del r['completeCurrentTerrainRouting'][0]['asset']
  with self.assertRaises(KeyError):role_boundaries(r,m,c,**k)
 def test_cannot_leaf_core(self):
  r,m,c,k=self.fixture();p=role_boundaries(r,m,c,**k);p[0]['pointer']='/completeProviderRootAndStreams'
  with self.assertRaises(AssertionError):verify_role_boundaries(r,m,c,p,**k)
 def test_cannot_leaf_ground(self):
  r,m,c,k=self.fixture();p=role_boundaries(r,m,c,**k);p[0]['pointer']='/wholeOriginalAndActualRenderedFiniteClearance'
  with self.assertRaises(AssertionError):verify_role_boundaries(r,m,c,p,**k)
 def test_cannot_leaf_actors(self):
  r,m,c,k=self.fixture();p=role_boundaries(r,m,c,**k);p[0]['pointer']='/completeCurrentActorScope'
  with self.assertRaises(AssertionError):verify_role_boundaries(r,m,c,p,**k)
 def test_source_mutation(self):
  r,m,c,k=self.fixture();p=role_boundaries(r,m,c,**k);r['completeCurrentTerrainRouting'][0]['entry']['source']['rawOriginal']['sha256']='0'*64
  with self.assertRaises(AssertionError):verify_role_boundaries(r,m,c,p,**k)
 def test_failed_role(self):
  r,m,c,k=self.fixture();r['unresolvedIndependentPhysicalReasons']=['failed']
  with self.assertRaises(AssertionError):role_boundaries(r,m,c,**k)
 def test_arbitrary_pointer_removed(self):
  r,m,c,k=self.fixture();p=role_boundaries(r,m,c,**k);p=[]
  with self.assertRaises(AssertionError):verify_role_boundaries(r,m,c,p,**k)
if __name__=='__main__':unittest.main()
