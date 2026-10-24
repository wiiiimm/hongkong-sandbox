import copy,unittest
from no1_preserved_parent_child_provenance_scope_v2_20261010 import boundaries
class Tests(unittest.TestCase):
 def setUp(self):
  self.parent=dict(w=2,h=2,cell=5,elev=[1,2,3,4],coarseCells=[1,1,2,2],meta={'georef':{'aE':5}},patches=[dict(meta={'source':{'files':[{'path':'old.bin','sha256':'a'*64}]},'targetUids':['landsd/'+str(i)+':0']},nativeMesh={'position':[0,0,0,1,0,0,0,0,1],'index':[0,1,2],'sourceOverlap':{'evidencePath':'old/proof.json'}}) for i in range(8)])
  self.candidate=copy.deepcopy(self.parent);self.candidate['patches'].append(dict(meta={'source':{'files':[{'path':'own.bin','sha256':'b'*64}]}},nativeMesh={'position':[0,0,0],'index':[0]}))
 def verify(self):return boundaries(self.candidate,self.parent,expected_parent_sha='a'*64,current_parent_sha='a'*64,evidence_equal=lambda a,b:a=='copied/proof.json' and b=='old/proof.json')
 def test_eight_metadata_only(self):
  r=self.verify();self.assertEqual(len(r),8);self.assertTrue(all(x['pointer'].endswith('/meta/source') for x in r));self.assertNotIn('/patches/8/meta/source',[x['pointer'] for x in r])
 def test_relocated_equal(self):self.candidate['patches'][1]['nativeMesh']['sourceOverlap']['evidencePath']='copied/proof.json';self.assertEqual(len(self.verify()),8)
 def test_geometry_changed(self):
  self.candidate['patches'][0]['nativeMesh']['position'][1]=.1
  with self.assertRaises(AssertionError):self.verify()
 def test_index_changed(self):
  self.candidate['patches'][0]['nativeMesh']['index'][0]=1
  with self.assertRaises(AssertionError):self.verify()
 def test_grid_changed(self):
  self.candidate['elev'][0]=2
  with self.assertRaises(AssertionError):self.verify()
 def test_provenance_changed(self):
  self.candidate['patches'][2]['meta']['source']['files'][0]['sha256']='c'*64
  with self.assertRaises(AssertionError):self.verify()
 def test_omitted_child(self):
  self.candidate['patches'].pop(0)
  with self.assertRaises(AssertionError):self.verify()
 def test_relocated_foreign(self):
  self.candidate['patches'][1]['nativeMesh']['sourceOverlap']['evidencePath']='foreign/proof.json'
  with self.assertRaises(AssertionError):self.verify()
 def test_parent_changed(self):
  with self.assertRaises(AssertionError):boundaries(self.candidate,self.parent,expected_parent_sha='a'*64,current_parent_sha='b'*64,evidence_equal=lambda a,b:True)
class ActualFixture(unittest.TestCase):
 def setUp(self):
  import json
  from pathlib import Path
  root=Path(__file__).resolve().parents[3]
  self.parent=json.loads((root/'3d-viewer/city/data/terrain-government-xl-central-pier-successor-installed-v2-20261007.json').read_text())
  self.candidate=json.loads((Path(__file__).parent/'local/government-xl-no1-garden-literal-parent-complete-current-physical-v5-20261010/terrain-central-no1-literal-villa-parent-current.json').read_text())
 def verify(self):return boundaries(self.candidate,self.parent,expected_parent_sha='9e14d2a11e25e930b184ef4f104df57aaf8c4af7b0096197b84c0b04894ac8fa',current_parent_sha='9e14d2a11e25e930b184ef4f104df57aaf8c4af7b0096197b84c0b04894ac8fa',evidence_equal=lambda a,b:False)
 def test_actual_grid_and_seven_native(self):
  rows=self.verify();self.assertEqual(len(rows),8);self.assertEqual(rows[1]['actualChildNumericKind'],'exact-preserved-existing-93890-grid')
 def test_grid_elevation_change(self):
  self.candidate['patches'][1]['elev'][0]+=.1
  with self.assertRaises(AssertionError):self.verify()
 def test_grid_rendered_change(self):
  self.candidate['patches'][1]['renderedElev'][0]+=.1
  with self.assertRaises(AssertionError):self.verify()
 def test_grid_native_injection(self):
  self.candidate['patches'][1]['nativeMesh']={'position':[0,0,0],'index':[0,0,0]}
  with self.assertRaises(AssertionError):self.verify()
 def test_grid_source_change(self):
  self.candidate['patches'][1]['meta']['source']={}
  with self.assertRaises(AssertionError):self.verify()
 def test_grid_unexpected_identity(self):
  for x in [self.parent,self.candidate]:x['patches'][1]['meta']['targetUids']=['landsd/99999:0']
  with self.assertRaises(AssertionError):self.verify()
if __name__=='__main__':unittest.main()
