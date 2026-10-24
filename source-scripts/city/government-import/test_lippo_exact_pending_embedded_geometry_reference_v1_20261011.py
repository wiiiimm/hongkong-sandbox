"""Actual immutable embedded source references and adverse scope/geometry cases."""
import gzip,json,unittest
from copy import deepcopy
from pathlib import Path
import lippo_exact_pending_embedded_geometry_reference_v1_20261011 as m
ROOT=Path(__file__).resolve().parents[3]
class TypedReferences(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.capture=(ROOT/m.CAPTURE_PATH).read_bytes();cls.tile_raw=(ROOT/m.TILE_PATH).read_bytes()
  cls.resolver=m.BoundResolver(cls.capture,cls.tile_raw);cls.pointer=next(iter(m.POINTERS))
  cls.record=m.at(cls.resolver.context,cls.pointer.rsplit('/',1)[0]);cls.actor=next(b for b in cls.resolver.tile['buildings'] if b.get('uid')==cls.record['uid'])
 def check(self,record=None,actor=None,pointer=None,reference=None,actors=None):
  r=deepcopy(self.record) if record is None else record;a=deepcopy(self.actor) if actor is None else actor
  return m.verify_record(pointer or self.pointer,r,r['sourceEvidence'] if reference is None else reference,[a] if actors is None else actors)
 def changed_record(self,f):
  r=deepcopy(self.record);f(r)
  with self.assertRaises((AssertionError,KeyError,ValueError)):self.check(record=r)
 def changed_actor(self,f):
  a=deepcopy(self.actor);f(a)
  with self.assertRaises((AssertionError,KeyError,ValueError)):self.check(actor=a)
 def test_all_six_exact_complete_typed_refs(self):
  for p in m.POINTERS:
   ref=m.at(self.resolver.context,p);v=self.resolver.resolve(m.CAPTURE_PATH,p,ref)
   self.assertFalse(v['numericGeometryExcluded']);self.assertFalse(v['metadataBoundarySkipped']);self.assertFalse(v['physicalAccepted'])
 def test_wrong_document(self):
  self.assertFalse(self.resolver.handles('other.json.gz',self.pointer))
  with self.assertRaises(AssertionError):self.resolver.resolve('other.json.gz',self.pointer,self.record['sourceEvidence'])
 def test_same_ref_other_pointer(self):
  with self.assertRaises(AssertionError):self.resolver.resolve(m.CAPTURE_PATH,self.pointer+'/other',self.record['sourceEvidence'])
 def test_candidate_pointer_not_allowed(self):self.assertFalse(self.resolver.handles(m.CAPTURE_PATH,self.pointer.replace('sourceEvidence','candidate')))
 def test_other_actor_index(self):
  with self.assertRaises(AssertionError):self.check(pointer=self.pointer.replace('/1530/','/1531/'))
 def test_wrong_actor_uid(self):self.changed_record(lambda r:r.update(uid='landsd/201560:0'))
 def test_wrong_csuid(self):self.changed_record(lambda r:r.update(csuid='unrelated'))
 def test_wrong_objectid(self):self.changed_record(lambda r:r.update(objectId=201560))
 def test_duplicate_actor(self):
  with self.assertRaises(AssertionError):self.check(actors=[self.actor,self.actor])
 def test_missing_actor(self):
  with self.assertRaises(AssertionError):self.check(actors=[])
 def test_wrong_current_actor_csuid(self):self.changed_actor(lambda a:a.update(buildingCSUID='wrong'))
 def test_wrong_hashkind(self):self.changed_record(lambda r:r['sourceEvidence'].update(hashKind='raw-file-sha'))
 def test_wrong_candidate_hashkind(self):self.changed_record(lambda r:r['candidate'].update(hashKind='raw-file-sha'))
 def test_wrong_kind(self):self.changed_record(lambda r:r['sourceEvidence'].update(kind='gzip'))
 def test_wrong_path(self):self.changed_record(lambda r:r['sourceEvidence'].update(path='3d-viewer/city/data/tiles/0_0.json'))
 def test_wrong_sha(self):self.changed_record(lambda r:r['sourceEvidence'].update(sha256='0'*64))
 def test_wrong_bytes(self):self.changed_record(lambda r:r['sourceEvidence'].update(bytes=1))
 def test_wrong_modelid(self):self.changed_record(lambda r:r['sourceEvidence'].update(modelId='other'))
 def test_wrong_source_hashes(self):self.changed_record(lambda r:r.update(sourceHashes={}))
 def test_geometry_vertex_mutation(self):self.changed_actor(lambda a:a['modelGeometry']['position'].__setitem__(0,a['modelGeometry']['position'][0]+.125))
 def test_geometry_normal_mutation(self):self.changed_actor(lambda a:a['modelGeometry']['normal'].__setitem__(0,a['modelGeometry']['normal'][0]+.125))
 def test_missing_geometry_field(self):self.changed_actor(lambda a:a['modelGeometry'].pop('colour'))
 def test_extra_geometry_field(self):self.changed_actor(lambda a:a['modelGeometry'].update(unbound=1))
 def test_reference_mismatch(self):
  ref=deepcopy(self.record['sourceEvidence']);ref['modelId']='other'
  with self.assertRaises(AssertionError):self.check(reference=ref)
 def test_capture_raw_mutation(self):
  with self.assertRaises(AssertionError):m.BoundResolver(self.capture+b' ',self.tile_raw)
 def test_tile_raw_mutation(self):
  with self.assertRaises(AssertionError):m.BoundResolver(self.capture,self.tile_raw+b' ')
if __name__=='__main__':unittest.main()
