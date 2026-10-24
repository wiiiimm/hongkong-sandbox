"""Run the existing exact-source transform/cache/mosaic checks for this area."""
import json,gzip,sys,unittest
from run import module,HERE
sys.path.insert(0,str(HERE.parent/'mui-wo-models'))
shared=module('shared_model_tests',HERE.parent/'mui-wo-models/test_models.py');shared.HERE=HERE
class TaiOModelTests(shared.ModelExtensionTests):
 minimum_new_models=531
 def test_python_render_sampler_retains_zero_and_raw_source_values(self):
  fine=module('render_terrain_audit',HERE.parent/'mui-wo-buildings/fine_terrain_audit.py')
  data={'w':2,'h':2,'elev':[5,5,5,5],'renderedElev':[0,None,None,None],'meta':{'georef':{'bE':834500,'bN':816500,'aE':5,'aN':-5}}}
  self.assertEqual(fine.DemSampler(data,rendered=True).ground(0,0),0)
  self.assertEqual(fine.DemSampler(data).ground(0,0),5)
  self.assertEqual(fine.DemSampler(data,rendered=True).ground(2.5,0),2.5)
 def test_bounded_slice_counts_and_source_ids(self):
  data=json.loads(gzip.decompress((HERE/'model-geometries.json.gz').read_bytes()))
  selection=json.loads(gzip.decompress((HERE/'building-selection.json.gz').read_bytes()))
  by_uid={b['uid']:b for b in selection['buildings']}
  self.assertEqual(len(by_uid),1030);self.assertEqual(data['counts']['sourceModelEntries'],535)
  self.assertEqual(len(data['byBuildingUid']),532);self.assertEqual(data['counts']['unmatchedEntries'],3)
  for uid,model in data['byBuildingUid'].items():
   original=by_uid[uid];self.assertEqual(original['buildingCSUID'],model['buildingCSUID'])
   match=model['officialMatches'][0]
   self.assertEqual(original['baseHeightHKPD'],match['sourceBaseHeight'])
   self.assertEqual(original['topHeightHKPD'],match['sourceTopHeight'])
if __name__=='__main__':unittest.main()
