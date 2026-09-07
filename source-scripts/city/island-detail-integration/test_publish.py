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
 def terrain_fixture(self,cells=(2,2,4,4),destination='city/data/terrain-new.json'):
  root={'w':11,'h':11,'cell':10,'elev':[1]*121,'vegetation':[0]*121,'meta':{'georef':{'W':11,'H':11,'aE':10,'aN':-10,'bE':100,'bN':200}}}
  self.write('3d-viewer/city/data/terrain.json',root)
  x0,z0,x1,z1=cells;w=(x1-x0)*2+1;h=(z1-z0)*2+1
  data={'w':w,'h':h,'cell':5,'coarseCells':list(cells),'elev':[2]*(w*h),'vegetation':[0]*(w*h),'meta':{'georef':{'W':w,'H':h,'aE':5,'aN':-5,'bE':100+x0*10,'bN':200-z0*10},'source':{'provider':'survey fixture','verticalDatum':'HKPD'}}}
  source=self.write('staged/'+pathlib.Path(destination).name,data)
  entry={'source':str(source.relative_to(self.root)),'destination':destination,'sha256':pub.sha(source),'area':'Fixture terrain','resolution':5}
  plan=pub.load(self.root/'plan.json');plan.setdefault('topLevelTerrainPatches',[]).append(entry);self.write('plan.json',plan)
  return source,entry
 def live_snapshot(self):return {str(p.relative_to(self.root)):p.read_bytes() for p in (self.root/'3d-viewer').rglob('*') if p.is_file()}
 def test_top_level_patch_preserves_existing_terrain_and_provenance(self):
  source,entry=self.terrain_fixture()
  existing=pub.load(source);existing['coarseCells']=[0,2,2,4];existing['meta']['georef']['bE']=100
  old=self.write('3d-viewer/city/data/terrain-existing.json',existing);old_bytes=old.read_bytes();root_bytes=(self.root/'3d-viewer/city/data/terrain.json').read_bytes()
  self.manifest['terrainPatches']=[{'url':'city/data/terrain-existing.json','resolution':5,'area':'Existing'}];self.write('3d-viewer/city/data/manifest.json',self.manifest)
  self.run_publish();manifest=pub.load(self.root/'3d-viewer/city/data/manifest.json')
  self.assertEqual(old.read_bytes(),old_bytes);self.assertEqual((self.root/'3d-viewer/city/data/terrain.json').read_bytes(),root_bytes)
  self.assertEqual(manifest['terrainPatches'][0],self.manifest['terrainPatches'][0]);new=manifest['terrainPatches'][1]
  self.assertEqual(new['sha256'],entry['sha256']);self.assertEqual(new['source'],pub.load(source)['meta']['source']);self.assertEqual((self.root/'3d-viewer'/new['url']).read_bytes(),source.read_bytes())
  self.assertIsNone(pub.load(pub.DOC/'publication.json')['before']['3d-viewer/'+entry['destination']])
 def test_top_level_patch_rejects_existing_or_planned_overlap_before_writes(self):
  for prior in ('existing','planned'):
   with self.subTest(prior=prior):
    source,entry=self.terrain_fixture();plan=pub.load(self.root/'plan.json');plan['topLevelTerrainPatches']=[entry]
    if prior=='existing':
     self.write('3d-viewer/city/data/terrain-existing.json',pub.load(source));self.manifest['terrainPatches']=[{'url':'city/data/terrain-existing.json'}]
    else:
     self.manifest['terrainPatches']=[];plan['topLevelTerrainPatches'].append({**entry,'destination':'city/data/terrain-second.json'})
    self.write('3d-viewer/city/data/manifest.json',self.manifest);self.write('plan.json',plan);before=self.live_snapshot()
    with self.assertRaisesRegex(AssertionError,'Overlapping terrain'):self.run_publish()
    self.assertEqual(self.live_snapshot(),before)
 def test_top_level_patch_stale_source_hash_does_not_write(self):
  source,entry=self.terrain_fixture();source.write_text(source.read_text()+' ');before=self.live_snapshot()
  with self.assertRaisesRegex(AssertionError,'source hash changed'):self.run_publish()
  self.assertEqual(self.live_snapshot(),before)
 def test_top_level_patch_rolls_back_with_model_assets(self):
  self.terrain_fixture();before=self.live_snapshot();replace=pub.os.replace
  def fail_manifest(src,dest):
   if pathlib.Path(dest).name=='manifest.json':raise OSError('simulated terrain transaction failure')
   replace(src,dest)
  with patch.object(pub.os,'replace',side_effect=fail_manifest),self.assertRaisesRegex(OSError,'terrain transaction'):self.run_publish()
  self.assertEqual(self.live_snapshot(),before)
 def test_top_level_patch_rejects_malformed_grid_or_reused_destination(self):
  mutations=[('origin',lambda d:d['meta']['georef'].update(bE=121)),('dimensions',lambda d:d['meta']['georef'].update(W=4)),('arrays',lambda d:d['elev'].pop()),('bounds',lambda d:d.update(coarseCells=[2,2,12,4]))]
  for name,mutate in mutations:
   with self.subTest(name=name):
    source,entry=self.terrain_fixture();data=pub.load(source);mutate(data);self.write(entry['source'],data)
    plan=pub.load(self.root/'plan.json');plan['topLevelTerrainPatches']=[{**entry,'sha256':pub.sha(source)}];self.write('plan.json',plan);before=self.live_snapshot()
    with self.assertRaises(AssertionError):self.run_publish()
    self.assertEqual(self.live_snapshot(),before)
  source,entry=self.terrain_fixture();self.write('3d-viewer/'+entry['destination'],{'existing':'keep'});before=self.live_snapshot()
  with self.assertRaisesRegex(AssertionError,'overwrite'):self.run_publish()
  self.assertEqual(self.live_snapshot(),before)
 def replacement_fixture(self):
  source,_=self.terrain_fixture();old=pub.load(source);old['id']='existing-child';old['meta']['targetUids']=['landsd/1:0']
  other=json.loads(json.dumps(old));other['id']='unrelated-child';other['coarseCells']=[6,6,8,8];other['meta']['georef'].update(bE=160,bN=140)
  parentpath=self.root/'3d-viewer/city/data/terrain.json';parent=pub.load(parentpath);parent['patches']=[old,other];self.write(str(parentpath.relative_to(self.root)),parent)
  new=json.loads(json.dumps(old));new.update(w=9,h=9,coarseCells=[1,1,5,5],elev=[3]*81,vegetation=[0]*81);new['meta']['georef'].update(W=9,H=9,bE=110,bN=190)
  bundle=self.write('staged/replacement.json',{'parentTerrainURL':'city/data/terrain.json','parentSha256':pub.sha(parentpath),'patches':[new]})
  entry={'bundle':'staged/replacement.json','oldChildId':old['id'],'oldChildSha256':pub.hashlib.sha256(pub.encoded(old)).hexdigest()}
  plan=pub.load(self.root/'plan.json');plan.pop('topLevelTerrainPatches');plan['areas'][0]['terrainReplacements']=[entry];self.write('plan.json',plan)
  return parentpath,parent,new,entry
 def test_terrain_replacement_preserves_parent_arrays_and_unrelated_children(self):
  parentpath,parent,new,_=self.replacement_fixture();self.run_publish();after=pub.load(parentpath)
  self.assertEqual(after['patches'],[new,parent['patches'][1]])
  self.assertEqual({k:v for k,v in after.items() if k!='patches'},{k:v for k,v in parent.items() if k!='patches'})
  self.assertEqual(pub.load(self.root/'3d-viewer/city/data/tiles/0_0.json')['buildings'][0],self.building)
 def test_terrain_replacement_stale_child_hash_rejected_before_writes(self):
  self.replacement_fixture();plan=pub.load(self.root/'plan.json');plan['areas'][0]['terrainReplacements'][0]['oldChildSha256']='0'*64;self.write('plan.json',plan);before=self.live_snapshot()
  with self.assertRaisesRegex(AssertionError,'child hash changed'):self.run_publish()
  self.assertEqual(self.live_snapshot(),before)
 def test_terrain_replacement_rolls_back_original_child_and_models(self):
  self.replacement_fixture();before=self.live_snapshot();replace=pub.os.replace
  def fail_manifest(src,dest):
   if pathlib.Path(dest).name=='manifest.json':raise OSError('replacement rollback fixture')
   replace(src,dest)
  with patch.object(pub.os,'replace',side_effect=fail_manifest),self.assertRaisesRegex(OSError,'replacement rollback'):self.run_publish()
  self.assertEqual(self.live_snapshot(),before)
 def test_terrain_replacement_rejects_loss_of_original_target(self):
  self.replacement_fixture();bundle=pub.load(self.root/'staged/replacement.json');bundle['patches'][0]['meta']['targetUids']=[];self.write('staged/replacement.json',bundle);before=self.live_snapshot()
  with self.assertRaisesRegex(AssertionError,'original target'):self.run_publish()
  self.assertEqual(self.live_snapshot(),before)
 def replacement_estimate_fixture(self):
  parentpath,_,_,_=self.replacement_fixture()
  estimate={'uid':'landsd/2:0','objectId':2,'buildingCSUID':'two','previousBase':8,'base':3,'height':3,'baseSource':'terrain-estimated'}
  self.write('3d-viewer/city/data/tiles/0_0.json',{'buildings':[self.building,{'uid':estimate['uid'],'objectId':2,'buildingCSUID':'two','base':8,'height':3,'baseSource':'terrain-estimated','heightSource':'estimated','baseHeightHKPD':None,'topHeightHKPD':None}]})
  self.write('staged/estimates.json',{'parentSha256':pub.sha(parentpath),'refinementSha256':pub.sha(self.root/'staged/replacement.json'),'buildings':[estimate]})
  plan=pub.load(self.root/'plan.json');plan['areas'][0]['estimates']=['staged/estimates.json'];self.write('plan.json',plan)
 def test_replacement_pairs_null_source_estimate_with_exact_bundle(self):
  self.replacement_estimate_fixture();self.run_publish();records=pub.load(self.root/'3d-viewer/city/data/tiles/0_0.json')['buildings']
  self.assertEqual(records[0],self.building);self.assertEqual(records[1]['base'],3);self.assertEqual(records[1]['height'],3);self.assertIsNone(records[1]['baseHeightHKPD']);self.assertIsNone(records[1]['topHeightHKPD'])
 def test_replacement_estimate_rejects_different_terrain_bundle(self):
  self.replacement_estimate_fixture();estimate=pub.load(self.root/'staged/estimates.json');estimate['refinementSha256']='0'*64;self.write('staged/estimates.json',estimate);before=self.live_snapshot()
  with self.assertRaisesRegex(AssertionError,'exact terrain bundle'):self.run_publish()
  self.assertEqual(self.live_snapshot(),before)
if __name__=='__main__':unittest.main()
