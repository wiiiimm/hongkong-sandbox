"""Publication must prepare before fencing and reject stale inputs/ownership."""
import contextlib,hashlib,importlib.util,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('guarded_publisher',Path(__file__).with_name('publish.py'))
publisher=importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher)

class PublicationTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  self.oldroot,self.olddoc,self.oldguard=publisher.ROOT,publisher.DOC,publisher.PUBLICATION_GUARD
  publisher.ROOT=self.root;publisher.DOC=self.root/'evidence'
  self.manifest=self.root/'3d-viewer/city/data/manifest.json'
  self.catalogue=self.root/'3d-viewer/city/data/new/catalogue.json'
  def save(rel,value):
   p=self.root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value));return p
  self.tile=save('3d-viewer/city/data/tile.json',{'buildings':[{'uid':'landsd/1:0','objectId':1,'buildingCSUID':'one','baseHeightHKPD':2,'topHeightHKPD':10}]})
  save('3d-viewer/city/data/manifest.json',{'counts':{'buildings':1},'tiles':[{'url':'city/data/tile.json'}],'officialModelCatalogues':[]})
  self.before=self.manifest.read_bytes()
  for name in ['catalogue','overview']:save('3d-viewer/city/data/'+name+'.json',{})
  blob=self.root/'staged/model.glb.gz';blob.parent.mkdir();blob.write_bytes(b'unchanged-fixture')
  save('staged/catalogue.json',{'counts':{'packedModels':1},'models':[{'uid':'landsd/1:0','objectId':1,'buildingCSUID':'one','recordedBaseHeight':2,'recordedTopHeight':10,'asset':'model.glb.gz','sha256':hashlib.sha256(blob.read_bytes()).hexdigest(),'bytes':blob.stat().st_size}]})
  save('plan.json',{'areas':[{'area':'fixture','catalogue':'staged/catalogue.json','destination':'city/data/new/catalogue.json'}]})
 def tearDown(self):
  publisher.ROOT,publisher.DOC,publisher.PUBLICATION_GUARD=self.oldroot,self.olddoc,self.oldguard
  publisher.PINNED_INPUTS.clear();self.temp.cleanup()
 def run_publish(self):
  with patch.object(sys,'argv',['publish.py','plan.json','--apply']),patch.object(publisher.subprocess,'check_output',return_value='fixture\n'),contextlib.redirect_stdout(__import__('io').StringIO()):publisher.main()
 def assert_unchanged(self):
  self.assertEqual(self.manifest.read_bytes(),self.before);self.assertFalse(self.catalogue.exists());self.assertFalse(self.catalogue.with_name('model.glb.gz').exists())
 def test_preparation_outside_guard_and_manifest_committed_last(self):
  calls=[]
  @contextlib.contextmanager
  def guard():
   self.assertIn(self.tile.resolve(),publisher.PINNED_INPUTS)
   self.assertGreaterEqual(len(publisher.PINNED_INPUTS),7);self.assert_unchanged();calls.append(True);yield
  publisher.PUBLICATION_GUARD=guard;self.run_publish()
  self.assertEqual(calls,[True]);self.assertTrue(self.catalogue.exists())
  self.assertEqual(json.loads(self.manifest.read_text())['officialModelCatalogues'],['city/data/new/catalogue.json'])
 def test_input_changed_after_preparation_blocks_all_writes(self):
  @contextlib.contextmanager
  def guard():self.tile.write_text('{"changed":true}');yield
  publisher.PUBLICATION_GUARD=guard
  with self.assertRaisesRegex(AssertionError,'input changed before commit'):self.run_publish()
  self.assert_unchanged()
 def test_lost_ownership_blocks_all_writes(self):
  @contextlib.contextmanager
  def guard():raise RuntimeError('lease lost');yield
  publisher.PUBLICATION_GUARD=guard
  with self.assertRaisesRegex(RuntimeError,'lease lost'):self.run_publish()
  self.assert_unchanged()
 def test_manifest_write_failure_rolls_back_assets(self):
  publisher.PUBLICATION_GUARD=contextlib.nullcontext
  replace=os.replace;failed=[]
  def fail_once(src,dest):
   if Path(dest)==self.manifest and not failed:failed.append(True);raise OSError('fixture disk failure')
   return replace(src,dest)
  with patch.object(publisher.os,'replace',side_effect=fail_once),self.assertRaisesRegex(OSError,'disk failure'):self.run_publish()
  self.assert_unchanged()

if __name__=='__main__':unittest.main()
