"""Actual original fixtures and negative identity/actor/source counterexamples."""
from copy import deepcopy
import importlib.util, tempfile, unittest
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read
from popcorn_two_attached_podium_identity_20261009 import named_proof,PARTS,PODIUM,BASE,PRIMARY,RELATION,PARENT_INPUT,REASON

class AttachedPodiumTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.directory=tempfile.TemporaryDirectory();local=Path(cls.directory.name);(local/'assets').mkdir()
  spec=importlib.util.spec_from_file_location('podium_identity_test_decoder',HERE/'xl-second-pass.py');decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder);decoder.LOCAL=local
  finalspec=importlib.util.spec_from_file_location('podium_identity_test_forms',HERE/'xl-final-script-pass.py');final=importlib.util.module_from_spec(finalspec);finalspec.loader.exec_module(final)
  cls.fixtures={}
  for row in read(BASE/'government-xl-popcorn-current-overlapping-original-recovery-20261009/selection.json.gz')['rows']:
   if row['uid'] not in PARTS:continue
   row['triangles']=row['native']['model']['triangles'];(local/'assets'/(row['sourceSHA256']+'.glb.gz')).write_bytes((ROOT/row['candidate']['path']).read_bytes());tri=decoder.glb_triangles(row)
   lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=[b for b,_,_ in final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])];stem=row['uid'].split('/')[1].replace(':','-')
   previous=read(BASE/'government-xl-popcorn-primary-excess-ownership-v2-20261009'/(stem+'-identity.json'))
   providers={row['uid']:read(PRIMARY/(stem+'-provider.json')),PODIUM:read(RELATION/'295538-0-primary.json')}
   parent=next(b for b in read(PARENT_INPUT)['rows'] if b['uid']==PODIUM)
   cls.fixtures[row['uid']]=(previous,row,tri,forms,providers,parent)
 @classmethod
 def tearDownClass(cls):cls.directory.cleanup()
 def setUp(self):
  original=self.fixtures['landsd/295421:0'];self.previous=deepcopy(original[0]);self.row=deepcopy(original[1]);self.tri=original[2];self.forms=deepcopy(original[3]);self.providers=deepcopy(original[4]);self.parent=original[5]
 def review(self):return named_proof(self.previous,self.row,self.tri,self.forms,self.providers,self.parent)
 def reject(self):
  with self.assertRaises(AssertionError):self.review()
 def test_both_complete_actual_originals_pass_identity_only(self):
  for fixture in self.fixtures.values():
   result=named_proof(*fixture);self.assertTrue(result['passed']);self.assertEqual(result['rawPodiumForeignReasonsRetained'],[REASON]);self.assertFalse(result['installationApproved']);self.assertFalse(result['physicalAccepted']);self.assertFalse(result['podiumCollisionExemption']);self.assertFalse(result['podiumGroundSupportCredit']);self.assertFalse(result['podiumRemoval']);self.assertGreater(result['independentFullSourceSpatialChecks']['primary']['rawRelatedPodiumExcessM2'],2)
 def test_wrong_source_uid_rejected(self):self.row['uid']='landsd/309558:0';self.reject()
 def test_part_source_sha_rejected(self):self.row['sourceSHA256']='a'*64;self.reject()
 def test_wrong_model_id_rejected(self):self.row['modelId']='Bwrong';self.reject()
 def test_incomplete_source_rejected(self):self.tri=self.tri[:-1];self.reject()
 def test_y_only_source_pose_change_rejected(self):self.tri=self.tri.copy();self.tri[:,:,1]+=.001;self.reject()
 def test_unverified_source_graph_rejected(self):self.previous['originalOwnership']['sourceGraphVerified']=False;self.reject()
 def test_missing_raw_podium_failure_rejected(self):self.previous['reasons']=[];self.reject()
 def test_duplicate_primary_podium_rejected(self):self.providers[PODIUM]['features']*=2;self.reject()
 def test_retired_primary_podium_rejected(self):self.providers[PODIUM]['features'][0]['attributes']['Status']='Retired';self.reject()
 def test_same_name_wrong_stable_id_rejected(self):self.providers[PODIUM]['features'][0]['attributes']['BuildingID']+=1;self.reject()
 def test_wrong_primary_type_rejected(self):self.providers[PODIUM]['features'][0]['attributes']['BuildingBlockType']='Tower';self.reject()
 def test_wrong_primary_creation_rejected(self):self.providers[PODIUM]['features'][0]['attributes']['DateCreate']+=86400000;self.reject()
 def test_wrong_crs_rejected(self):self.providers[PODIUM]['spatialReference']={'wkid':3857};self.reject()
 def test_changed_primary_podium_footprint_rejected(self):
  self.providers[PODIUM]['features'][0]['geometry']['rings']=[[[834500,816500],[834501,816500],[834501,816501],[834500,816500]]];self.reject()
 def test_primary_vertical_relation_rejected(self):self.providers[PODIUM]['features'][0]['attributes']['TopHeight']=20;self.reject()
 def test_original_podium_world_binding_rejected(self):self.parent={**self.parent,'worldTriangleSHA256':'b'*64};self.reject()
 def test_all_other_failure_reasons_preserved(self):self.previous['reasons'].append('whole-original-roof-coverage-failure');result=self.review();self.assertFalse(result['passed']);self.assertIn('whole-original-roof-coverage-failure',result['reasons'])
 def test_same_parent_extra_actor_still_foreign(self):
  actor=deepcopy(next(b for b in self.forms if b['uid']==PODIUM));actor['uid']='landsd/unrelated:0';self.forms.append(actor);result=self.review();self.assertFalse(result['passed']);self.assertIn(actor['uid'],result['allOtherActorsStillForeignUIDs'])
 def test_duplicate_current_actor_rejected(self):self.forms.append(deepcopy(self.forms[0]));self.reject()
 def test_same_name_and_osm_parent_not_used(self):
  parent=next(b for b in self.forms if b['uid']==PODIUM);parent['name']='Changed';parent['parent']='other-parent';self.assertTrue(self.review()['passed'])

if __name__=='__main__':unittest.main()
