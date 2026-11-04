"""Meaningful negative tests for one exact ancillary-canopy identity relationship."""
import copy,importlib.util,unittest
import numpy as np
import science_attached_open_canopy_identity_20261009 as identity
from run import ROOT,HERE,read
class ScienceRelationshipTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  base=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-80343-current-inputs'
  cls.row=read(base/'check-selection.json.gz')['rows'][0];cls.previous=read(base/'indexed-preflight.json')['rows'][0]['identity']
  spec=importlib.util.spec_from_file_location('science_test_decode',HERE/'xl-second-pass.py');decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder);decoder.LOCAL=HERE/'local/xl-terrain-recovery-20261009-80343-current-inputs';cls.tri=decoder.glb_triangles(cls.row)
  spec=importlib.util.spec_from_file_location('science_test_forms',HERE/'xl-final-script-pass.py');final=importlib.util.module_from_spec(spec);spec.loader.exec_module(final);lo,hi=cls.tri.min(axis=(0,1)),cls.tri.max(axis=(0,1));cls.forms=[b for b,_,_ in final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])]
  cls.providers={u:read(identity.DOC/(u.split('/')[1].replace(':','-')+'-building.json')) for u in [identity.UID,identity.RELATED]}
 def execute(self,**kw):
  vals=dict(previous=copy.deepcopy(self.previous),row=copy.deepcopy(self.row),triangles=self.tri.copy(),current_forms=copy.deepcopy(self.forms),providers=copy.deepcopy(self.providers));vals.update(kw);return identity.named_proof(**vals)
 def test_actual_pinned_positive_has_no_physical_or_canopy_exemption(self):
  p=self.execute();self.assertTrue(p['passed']);self.assertFalse(p['physicalAccepted']);self.assertFalse(p['installationApproved']);self.assertFalse(p['currentCanopyCollisionExemption']);self.assertFalse(p['currentCanopyTerrainExemption']);self.assertFalse(p['currentCanopyRemoval']);self.assertEqual(p['allOtherCurrentFormsRetained'],self.forms);self.assertGreater(p['independentFullSourceSpatialChecks']['current']['rawExactRelatedCanopyExcessM2'],1)
 def test_y_only_original_mutation_rejected(self):
  tri=self.tri.copy();tri[0,0,1]+=.01
  with self.assertRaises(AssertionError):self.execute(triangles=tri)
 def test_changed_source_sha_rejected(self):
  row=copy.deepcopy(self.row);row['sourceSHA256']='0'*64
  with self.assertRaises(AssertionError):self.execute(row=row)
 def test_changed_source_model_rejected(self):
  row=copy.deepcopy(self.row);row['modelId']='B363491801601063C1'
  with self.assertRaises(AssertionError):self.execute(row=row)
 def test_source_graph_failure_rejected(self):
  p=copy.deepcopy(self.previous);p['originalOwnership']['sourceGraphVerified']=False
  with self.assertRaises(AssertionError):self.execute(previous=p)
 def test_other_raw_cell_failure_stays_held(self):
  p=copy.deepcopy(self.previous);p['reasons'].append('original-source-does-not-cover-whole-georef-cell');out=self.execute(previous=p);self.assertFalse(out['passed']);self.assertIn('original-source-does-not-cover-whole-georef-cell',out['reasons'])
 def test_same_named_foreign_canopy_is_not_exempt(self):
  forms=copy.deepcopy(self.forms);other=copy.deepcopy(next(b for b in forms if b['uid']==identity.RELATED));other['uid']='test/same-name-canopy:0';forms.append(other);out=self.execute(current_forms=forms);self.assertFalse(out['passed']);self.assertIn(other['uid'],out['allOtherActorsStillForeignUIDs'])
 def test_wrong_primary_type_rejected(self):
  p=copy.deepcopy(self.providers);p[identity.RELATED]['features'][0]['attributes']['BuildingBlockType']='Tower'
  with self.assertRaises(AssertionError):self.execute(providers=p)
 def test_primary_creation_lineage_mismatch_rejected(self):
  p=copy.deepcopy(self.providers);p[identity.RELATED]['features'][0]['attributes']['DateCreate']+=86400000
  with self.assertRaises(AssertionError):self.execute(providers=p)
 def test_primary_duplicate_record_rejected(self):
  p=copy.deepcopy(self.providers);p[identity.RELATED]['features'].append(p[identity.RELATED]['features'][0])
  with self.assertRaises(AssertionError):self.execute(providers=p)
 def test_primary_wrong_name_rejected(self):
  p=copy.deepcopy(self.providers);p[identity.RELATED]['features'][0]['attributes']['BuildingNameTC']='香港歷史博物館'
  with self.assertRaises(AssertionError):self.execute(providers=p)
 def test_current_attached_boundary_shift_rejected(self):
  forms=copy.deepcopy(self.forms);b=next(b for b in forms if b['uid']==identity.RELATED);b['rings']=[[[x+.001,z] for x,z in r] for r in b['rings']]
  with self.assertRaises(AssertionError):self.execute(current_forms=forms)
 def test_primary_boundary_shift_rejected(self):
  p=copy.deepcopy(self.providers);g=p[identity.RELATED]['features'][0]['geometry'];g['rings']=[[[x+.001,y] for x,y in r] for r in g['rings']]
  with self.assertRaises(AssertionError):self.execute(providers=p)
 def test_named_scope_rejected(self):
  row=copy.deepcopy(self.row);row['uid']='landsd/83471:0'
  with self.assertRaises(AssertionError):self.execute(row=row)
if __name__=='__main__':unittest.main()
