"""Actual unchanged-source fixtures and adverse identity/foreign-role mutations."""
import unittest,copy,importlib.util
import numpy as np
import harbourfront_attached_road_margin_identity_20261009 as identity
from run import ROOT,HERE,read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

class BoundaryIdentityTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.evidence=read(identity.DOC/'attached-original-road-margin-diagnostic.json.gz');cls.tri=decode_original_world_triangles((ROOT/cls.evidence['originalPath']).read_bytes());cls.provider=read(identity.DOC/'current-unique-primary-record.json')
  cls.row=next(r for r in read(ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-118230-current-inputs/check-selection.json.gz')['rows'] if r['uid']==identity.UID)
  cls.row['source']['building']=cls.evidence['currentTargetForm']
  spec=importlib.util.spec_from_file_location('boundary_test_complete_current_forms',HERE/'xl-final-script-pass.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);lo,hi=cls.tri.min(axis=(0,1)),cls.tri.max(axis=(0,1));cls.forms=[b for b,_,_ in m.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])]
  cls.previous={'uid':identity.UID,'sourceSHA256':identity.SOURCE_SHA,'worldTrianglesSHA256':identity.WORLD_SHA,'originalOwnership':{'sourceGraphVerified':True},'reasons':sorted(identity.REASONS)}
 def values(self):return [copy.deepcopy(self.previous),copy.deepcopy(self.row),self.tri.copy(),copy.deepcopy(self.forms),copy.deepcopy(self.provider),copy.deepcopy(self.evidence)]
 def reject(self,edit):
  args=self.values();edit(args)
  try:result=identity.named_proof(*args)
  except (AssertionError,ValueError,KeyError):return
  self.assertFalse(result['passed'])
 def test_complete_actual_original_role_only_passes(self):
  p=identity.named_proof(*self.values());self.assertTrue(p['passed']);self.assertFalse(p['physicalAccepted']);self.assertFalse(p['installationApproved']);self.assertEqual(p['sourceSpecificBoundaryFaceIds'],identity.FACE_IDS);self.assertEqual(p['allOtherActorsStillForeignUIDs'],sorted(b['uid'] for b in self.forms if b['uid']!=identity.UID));self.assertGreater(p['independentFullSourceSpatialChecks']['current']['fullOriginalRawMaximumExtentM'],11)
 def test_vertical_only_original_mutation_rejected(self):self.reject(lambda a:a[2].__setitem__((16743,0,1),a[2][16743,0,1]+.01))
 def test_extra_far_original_face_rejected(self):self.reject(lambda a:a[2].__setitem__((500,0,0),a[2][500,0,0]+30))
 def test_original_face_removed_rejected(self):self.reject(lambda a:a.__setitem__(2,a[2][:-1]))
 def test_nonfinite_original_rejected(self):self.reject(lambda a:a[2].__setitem__((0,0,0),np.nan))
 def test_other_named_building_rejected(self):self.reject(lambda a:a[1].__setitem__('uid','landsd/118231:0'))
 def test_other_original_source_version_rejected(self):self.reject(lambda a:a[1].__setitem__('sourceSHA256','0'*64))
 def test_source_graph_not_verified_rejected(self):self.reject(lambda a:a[0]['originalOwnership'].__setitem__('sourceGraphVerified',False))
 def test_missing_original_component_accounting_rejected(self):self.reject(lambda a:a[5]['completeConnectedComponentFaceIds'].pop())
 def test_missing_boundary_face_rejected(self):self.reject(lambda a:a[5]['allFarFaceIds'].pop())
 def test_unpinned_road_geometry_rejected(self):self.reject(lambda a:a[5]['roadMarginRows'][0]['geometry'].__setitem__('coordinates',[[[0,0],[1,1]]]))
 def test_wrong_cartographic_role_rejected(self):self.reject(lambda a:a[5]['roadMarginStyle'][0].__setitem__('id','/WL,E'))
 def test_wrong_primary_building_identity_rejected(self):self.reject(lambda a:a[4]['features'][0]['attributes'].__setitem__('BuildingID',1108242699))
 def test_inactive_primary_rejected(self):self.reject(lambda a:a[4]['features'][0]['attributes'].__setitem__('Status','Demolished'))
 def test_duplicate_primary_rejected(self):self.reject(lambda a:a[4]['features'].append(copy.deepcopy(a[4]['features'][0])))
 def test_wrong_primary_creation_lineage_rejected(self):self.reject(lambda a:a[4]['features'][0]['attributes'].__setitem__('DateCreate',0))
 def test_shifted_primary_polygon_rejected(self):
  def edit(a):
   for ring in a[4]['features'][0]['geometry']['rings']:
    for p in ring:p[0]+=100
  self.reject(edit)
 def test_same_name_foreign_actor_is_not_exempt(self):
  def edit(a):
   lo,hi=self.tri[:,:,[0,2]].min(axis=(0,1)),self.tri[:,:,[0,2]].max(axis=(0,1));b=copy.deepcopy(self.evidence['currentTargetForm']);b['uid']='landsd/foreign:0';b['rings']=[[[lo[0]-1,lo[1]-1],[hi[0]+1,lo[1]-1],[hi[0]+1,hi[1]+1],[lo[0]-1,hi[1]+1],[lo[0]-1,lo[1]-1]]];a[3].append(b)
  self.reject(edit)
 def test_unrelated_raw_failure_preserved(self):
  a=self.values();a[0]['reasons'].append('unsupported-roof-component');p=identity.named_proof(*a);self.assertFalse(p['passed']);self.assertIn('unsupported-roof-component',p['reasons'])
 def test_whole_cell_failure_preserved(self):
  a=self.values();a[0]['reasons'].append('original-source-does-not-cover-whole-georef-cell');self.assertFalse(identity.named_proof(*a)['passed'])

if __name__=='__main__':unittest.main()
