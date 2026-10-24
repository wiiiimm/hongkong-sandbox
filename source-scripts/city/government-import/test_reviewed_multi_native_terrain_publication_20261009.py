"""Real existing publication/review gates around the bounded plural adapter.

Patch mesh/grid validation is isolated: this suite tests replacement semantics,
not the already tested native mesh format. The unchanged real publisher performs
hash, destination, overlap, native receipt, retained actor and hydro checks.
"""
import copy,hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
from reviewed_multi_native_terrain_publication_20261009 import stage_top_level

class PluralNativePublicationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  path=Path(__file__).resolve().parents[1]/'island-detail-integration/publish.py'
  spec=importlib.util.spec_from_file_location('real_plural_test_publisher',path);self.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.m);self.m.ROOT=self.root
  self.m.validate_patch=lambda p,parent:None
  self.m.PINNED_INPUTS={}
  grid=dict(w=21,h=21,cell=10,elev=[0]*441,vegetation=[0]*441,meta=dict(georef=dict(W=21,H=21,aE=10,aN=-10,bE=0,bN=0)))
  self.put('3d-viewer/city/data/terrain.json',grid)
  self.old=[dict(nativeMesh=True,coarseCells=[1,1,3,3],hydro={'water':[]},meta={'targetUids':['old-a']}),dict(nativeMesh=True,coarseCells=[5,1,7,3],hydro={'water':[]},meta={'targetUids':['old-b']})]
  self.new=dict(nativeMesh=True,coarseCells=[1,1,7,3],hydro={'water':[]},cell=1,meta={'targetUids':['old-a','old-b','new']})
  newsha=self.put('staged/new.json',self.new)
  full=dict(aiCalls=0,modelGeometryChanges=0,rows=[dict(uid=u,passed=True,terrain=dict(newlyWhollyBuried=0,newlyUpwardWhollyBuried=0)) for u in ['old-a','old-b']])
  fullsha=self.put('proof/full.json',full);self.replacements=[]
  for i,old in enumerate(self.old):
   url=f'city/data/old-{i}.json';sha=self.put('3d-viewer/'+url,old)
   decision=dict(status='approved-for-integration',supersededURL=url,supersededSHA256=sha,replacementSHA256=newsha,sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,retainedUids=old['meta']['targetUids'],replacementTargetUids=self.new['meta']['targetUids'],fullMeshCheck=dict(path='proof/full.json',sha256=fullsha))
   reviewpath=f'proof/review-{i}.json';reviewsha=self.put(reviewpath,decision)
   self.replacements.append(dict(url=url,sha256=sha,retainedUids=old['meta']['targetUids'],nativeReview=dict(path=reviewpath,sha256=reviewsha)))
  self.original=dict(terrainPatches=[dict(url=r['url'],sha256=r['sha256']) for r in self.replacements])
  self.plan=dict(topLevelTerrainPatches=[dict(source='staged/new.json',destination='city/data/new.json',sha256=newsha,resolution=1,area='Fixture',replacesMany=self.replacements)])
 def put(self,path,value):
  p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);raw=json.dumps(value,sort_keys=True).encode();p.write_bytes(raw);return hashlib.sha256(raw).hexdigest()
 def replace_new(self):
  self.plan['topLevelTerrainPatches'][0]['sha256']=self.put('staged/new.json',self.new)
  for i in range(2):
   p=f'proof/review-{i}.json';d=json.loads((self.root/p).read_bytes());d['replacementSHA256']=self.plan['topLevelTerrainPatches'][0]['sha256'];self.replacements[i]['nativeReview']['sha256']=self.put(p,d)
 def run_adapter(self):
  manifest=copy.deepcopy(self.original);edits={};report={};before=copy.deepcopy(self.original)
  stage_top_level(self.m,self.plan,self.original,manifest,edits,report,self.m.stage_top_level_terrain)
  self.assertEqual(before,self.original)
  return manifest,edits,report
 def test_two_explicit_full_reviewed_native_parents_replaced_once(self):
  manifest,edits,report=self.run_adapter();self.assertEqual([p['url'] for p in manifest['terrainPatches']],['city/data/new.json']);self.assertEqual(len(edits),1);self.assertEqual(len(report['replacedTerrainPatches']),2)
  self.assertTrue(all((self.root/'3d-viewer'/r['url']).exists() for r in self.replacements))
 def test_unlisted_third_parent_overlap_still_rejects(self):
  self.put('3d-viewer/city/data/foreign.json',dict(coarseCells=[3,1,5,3]));self.original['terrainPatches'].append(dict(url='city/data/foreign.json'))
  with self.assertRaisesRegex(AssertionError,'Overlapping'):self.run_adapter()
 def test_changed_second_original_hash_rejects(self):
  self.put('3d-viewer/'+self.replacements[1]['url'],{**self.old[1],'changed':True})
  with self.assertRaises(AssertionError):self.run_adapter()
 def test_changed_second_review_rejects(self):
  (self.root/'proof/review-1.json').write_text('{}')
  with self.assertRaisesRegex(AssertionError,'review changed'):self.run_adapter()
 def test_failed_retained_native_full_mesh_rejects(self):
  full=json.loads((self.root/'proof/full.json').read_bytes());full['rows'][1]['passed']=False;sha=self.put('proof/full.json',full)
  for i in range(2):
   p=f'proof/review-{i}.json';d=json.loads((self.root/p).read_bytes());d['fullMeshCheck']['sha256']=sha;self.replacements[i]['nativeReview']['sha256']=self.put(p,d)
  with self.assertRaisesRegex(AssertionError,'full-mesh'):self.run_adapter()
 def test_retained_actor_omission_rejects(self):
  self.replacements[1]['retainedUids']=[]
  with self.assertRaisesRegex(AssertionError,'every original'):self.run_adapter()
 def test_duplicate_parent_rejects(self):
  self.replacements[1]['url']=self.replacements[0]['url']
  with self.assertRaises(AssertionError):self.run_adapter()
 def test_duplicate_retained_actor_rejects(self):
  self.replacements[1]['retainedUids']=['old-a']
  with self.assertRaisesRegex(AssertionError,'Repeated'):self.run_adapter()
 def test_does_not_contain_second_parent_rejects(self):
  self.new['coarseCells'][2]=6;self.replace_new()
  with self.assertRaises(AssertionError):self.run_adapter()
 def test_hydro_change_rejects(self):
  self.new['hydro']={'water':['changed']};self.replace_new()
  with self.assertRaises(AssertionError):self.run_adapter()
 def test_original_parent_overlap_rejects(self):
  self.old[1]['coarseCells']=[2,1,4,3];r=self.replacements[1];r['sha256']=self.put('3d-viewer/'+r['url'],self.old[1]);p='proof/review-1.json';d=json.loads((self.root/p).read_bytes());d['supersededSHA256']=r['sha256'];r['nativeReview']['sha256']=self.put(p,d)
  with self.assertRaisesRegex(AssertionError,'Overlapping'):self.run_adapter()
 def test_existing_destination_rejects(self):
  self.put('3d-viewer/city/data/new.json',{})
  with self.assertRaisesRegex(AssertionError,'overwrite'):self.run_adapter()
 def test_destination_traversal_rejects(self):
  self.plan['topLevelTerrainPatches'][0]['destination']='../escape.json'
  with self.assertRaisesRegex(AssertionError,'relative'):self.run_adapter()
 def test_unsupported_third_replacement_rejects(self):
  self.replacements.append(copy.deepcopy(self.replacements[0]))
  with self.assertRaises(AssertionError):self.run_adapter()
 def test_missing_review_rejects(self):
  self.replacements[1]['nativeReview']=None
  with self.assertRaisesRegex(AssertionError,'separate'):self.run_adapter()
 def test_ai_geometry_review_rejects(self):
  p='proof/review-1.json';d=json.loads((self.root/p).read_bytes());d['modelGeometryChanges']=1;self.replacements[1]['nativeReview']['sha256']=self.put(p,d)
  with self.assertRaises(AssertionError):self.run_adapter()

if __name__=='__main__':unittest.main()
