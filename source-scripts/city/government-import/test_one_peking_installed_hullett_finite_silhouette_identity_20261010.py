"""Actual complete government originals and adverse identity/source mutations."""
import copy,unittest
import numpy as np
from run import ROOT,read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import one_peking_installed_hullett_finite_silhouette_identity_20261010 as k
BASE=ROOT/'docs/astra-city/government-import'
class ActualSource(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  ctx=read(BASE/'government-xl-one-peking-hullett-complete-original-boundary-context-v1-20261010/diagnostic.json.gz');rows={r['uid']:r for r in ctx['sources']};p=read(BASE/'government-xl-one-peking-hullett-three-exact-original-primary-context-v2-20261010/diagnostic.json.gz')
  cls.fixture=dict(own_triangles=decode_original_world_triangles((ROOT/rows[k.OWN]['source']['path']).read_bytes()),foreign_triangles=decode_original_world_triangles((ROOT/rows[k.FOREIGN]['source']['path']).read_bytes()),current_forms=[x['building'] for x in ctx['completeCurrentForms']],primary_features=[r['freshPrimary'] for r in p['rows']],installed_entries=[rows[k.FOREIGN]['entry']],own_source_sha=k.OWN_SHA)
 def altered(self):return copy.deepcopy(self.fixture)
 def reject(self,f):
  with self.assertRaises((AssertionError,KeyError,ValueError)):k.verify(**f)
 def test_actual_complete_originals_keep_raw_negative(self):
  r=k.verify(**self.fixture);self.assertGreater(r['rawCurrentBasicProxyForeignExcessM2'],5);self.assertLess(r['currentCompleteInstalledOriginalForeignExcessM2'],.03);self.assertEqual(len(r['allOriginalAffectedFaces']),36);self.assertEqual(len(r['completeOriginalExactPositiveContacts']),12);self.assertFalse(r['physicalAccepted']);self.assertFalse(r['collisionExemption']);self.assertFalse(r['identityAccepted'])
 def test_missing_foreign_faces(self):
  f=self.altered();f['foreign_triangles']=f['foreign_triangles'][:-1];self.reject(f)
 def test_missing_own_faces(self):
  f=self.altered();f['own_triangles']=f['own_triangles'][:-1];self.reject(f)
 def test_foreign_geometry_changed_y(self):
  f=self.altered();f['foreign_triangles'][20000,0,1]+=.001;self.reject(f)
 def test_own_geometry_changed_x(self):
  f=self.altered();f['own_triangles'][0,0,0]+=.001;self.reject(f)
 def test_foreign_geometry_nonfinite(self):
  f=self.altered();f['foreign_triangles'][0,0,0]=np.nan;self.reject(f)
 def test_own_source_sha_changed(self):
  f=self.altered();f['own_source_sha']='0'*64;self.reject(f)
 def test_omitted_current_actor(self):
  f=self.altered();f['current_forms']=f['current_forms'][:-1];self.reject(f)
 def test_duplicate_current_actor(self):
  f=self.altered();f['current_forms'][1]=f['current_forms'][0];self.reject(f)
 def test_added_current_actor(self):
  f=self.altered();f['current_forms'].append(copy.deepcopy(f['current_forms'][0]));self.reject(f)
 def test_changed_current_foreign_geometry(self):
  f=self.altered();next(b for b in f['current_forms'] if b['uid']==k.FOREIGN)['rings'][0][0][0]+=.01;self.reject(f)
 def test_changed_other_foreign_geometry(self):
  f=self.altered();next(b for b in f['current_forms'] if b['uid']=='landsd/225163:0')['rings'][0][0][0]+=.01;self.reject(f)
 def test_changed_current_height(self):
  f=self.altered();f['current_forms'][0]['height']+=1;self.reject(f)
 def test_missing_primary_identity(self):
  f=self.altered();f['primary_features']=[p for p in f['primary_features'] if p['attributes']['BuildingCSUID']!=k.PRIMARY[k.FOREIGN][0]];self.reject(f)
 def test_duplicate_primary_identity(self):
  f=self.altered();f['primary_features'].append(copy.deepcopy(f['primary_features'][0]));self.reject(f)
 def test_changed_primary_status(self):
  f=self.altered();f['primary_features'][0]['attributes']['Status']='Inactive';self.reject(f)
 def test_changed_primary_geometry(self):
  f=self.altered();f['primary_features'][0]['geometry']['rings'][0][0][0]+=.001;self.reject(f)
 def test_changed_primary_buildingid(self):
  f=self.altered();f['primary_features'][0]['attributes']['BuildingID']+=1;self.reject(f)
 def test_uninstalled_foreign(self):
  f=self.altered();f['installed_entries']=[];self.reject(f)
 def test_ambiguous_installed_foreign(self):
  f=self.altered();f['installed_entries']*=2;self.reject(f)
 def test_changed_installed_source_sha(self):
  f=self.altered();f['installed_entries'][0]['sha256']='0'*64;self.reject(f)
 def test_wrong_installed_uid(self):
  f=self.altered();f['installed_entries'][0]['uid']='landsd/211916:0';self.reject(f)
 def test_unapproved_installed_entry(self):
  f=self.altered();f['installed_entries'][0]['publicationApproved']=False;self.reject(f)
 def test_changed_installed_root(self):
  f=self.altered();f['installed_entries'][0]['rootTranslation'][0]+=1;self.reject(f)
 def test_changed_installed_worldbounds(self):
  f=self.altered();f['installed_entries'][0]['worldBounds'][0][0]+=.003;self.reject(f)
 def test_procedural_foreign_not_actual_original(self):
  f=self.altered();f['installed_entries'][0]['proceduralWindows']=True;self.reject(f)
if __name__=='__main__':unittest.main()
