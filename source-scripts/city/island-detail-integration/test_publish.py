"""Exercise publication failure before and during installation without live writes."""
import importlib.util,json,pathlib,sys,tempfile,unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('publisher',pathlib.Path(__file__).with_name('publish.py'));pub=importlib.util.module_from_spec(spec);spec.loader.exec_module(pub)
class Publication(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.temp.name);self.old=(pub.ROOT,pub.DOC);pub.ROOT=self.root;pub.DOC=self.root/'docs'
  self.building={'uid':'landsd/1:0','objectId':1,'buildingCSUID':'one','baseHeightHKPD':2,'topHeightHKPD':10,'base':2,'height':8}
  self.write('3d-viewer/city/data/tiles/0_0.json',{'buildings':[self.building],'roads':[],'parks':[]})
  self.manifest={'counts':{'buildings':1},'tiles':[{'url':'city/data/tiles/0_0.json','bytes':1}],'officialModelCatalogues':[]};self.write('3d-viewer/city/data/manifest.json',self.manifest)
  self.write('3d-viewer/city/data/catalogue.json',[]);self.write('3d-viewer/city/data/overview.json',{})
  asset=self.root/'staged/models/one.glb.gz';asset.parent.mkdir(parents=True);asset.write_bytes(b'verified fixture')
  self.meta={'uid':'landsd/1:0','objectId':1,'buildingCSUID':'one','recordedBaseHeight':2,'recordedTopHeight':10,'asset':'models/one.glb.gz','bytes':asset.stat().st_size,'sha256':pub.sha(asset)}
  self.write('staged/catalogue.json',{'counts':{'packedModels':1},'models':[self.meta]})
  self.write('plan.json',{'areas':[{'area':'fixture','catalogue':'staged/catalogue.json','destination':'city/data/official-models/test/catalogue.json'}]})
 def tearDown(self):pub.ROOT,pub.DOC=self.old;self.temp.cleanup()
 def write(self,name,data):
  p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data));return p
 def run_publish(self):
  with patch.object(sys,'argv',['publish.py','plan.json','--apply']),patch.object(pub.subprocess,'check_output',return_value='abc123\n'):pub.main()
 def test_source_identity_mismatch_does_not_write(self):
  self.meta['buildingCSUID']='wrong';self.write('staged/catalogue.json',{'counts':{'packedModels':1},'models':[self.meta]})
  with self.assertRaisesRegex(AssertionError,'identity'):self.run_publish()
  self.assertEqual(pub.load(self.root/'3d-viewer/city/data/manifest.json'),self.manifest);self.assertFalse((self.root/'3d-viewer/city/data/official-models/test/catalogue.json').exists())
 def test_failed_manifest_install_restores_files_and_removes_new_assets(self):
  replace=pub.os.replace
  def fail_manifest(src,dest):
   if pathlib.Path(dest).name=='manifest.json':raise OSError('simulated disk failure')
   replace(src,dest)
  with patch.object(pub.os,'replace',side_effect=fail_manifest),self.assertRaisesRegex(OSError,'simulated'):self.run_publish()
  self.assertEqual(pub.load(self.root/'3d-viewer/city/data/manifest.json'),self.manifest)
  self.assertFalse((self.root/'3d-viewer/city/data/official-models/test/catalogue.json').exists());self.assertFalse((self.root/'3d-viewer/city/data/official-models/test/models/one.glb.gz').exists())
 def test_success_installs_assets_and_retains_source_record(self):
  self.run_publish();self.assertEqual(pub.load(self.root/'3d-viewer/city/data/tiles/0_0.json')['buildings'][0],self.building)
  self.assertTrue((self.root/'3d-viewer/city/data/official-models/test/models/one.glb.gz').exists());self.assertEqual(pub.load(pub.DOC/'publication.json')['beforeCommit'],'abc123')
if __name__=='__main__':unittest.main()
