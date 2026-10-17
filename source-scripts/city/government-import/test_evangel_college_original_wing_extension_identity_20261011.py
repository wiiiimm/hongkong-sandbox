"""Hermetic actual13960-source counterexamples; production replay is separate."""
import unittest
from copy import deepcopy
import numpy as np
from run import ROOT,read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import evangel_college_original_wing_extension_identity_20261011 as k
B=ROOT/'docs/astra-city/government-import';RAW=B/'government-xl-evangel-college-91306-current-complete-identity-diagnostic-v1-20261011'
class ActualSource(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.row=read(RAW/'selection.json.gz')['rows'][0];cls.previous=read(RAW/'identity.json');cls.world=decode_original_world_triangles((ROOT/cls.row['candidate']['path']).read_bytes());cls.forms=read(RAW/'complete-current-forms.json.gz')['rows'];cls.provider=read(B/'government-xl-evangel-college-91306-primary-relations-v1-20261011/exact-current-one-primary.json');cls.context=read(B/'government-xl-evangel-college-91306-western-original-patches-context-v1-20261011/diagnostic.json.gz')
 def args(self):return [deepcopy(self.previous),deepcopy(self.row),self.world.copy(),deepcopy(self.forms),deepcopy(self.provider),deepcopy(self.context)]
 def reject(self,mutation):
  a=self.args();mutation(a)
  with self.assertRaises(AssertionError):k.proposal(*a)
 def test_actual_complete_source(self):
  p=k.proposal(*self.args());self.assertTrue(p['proposalSpatialGuardsSatisfied']);self.assertEqual((p['completeSourceFaces'],len(p['namedOriginalWingExtensionFaceIDs']),p['ordinaryExtentFaceCount']),(13960,136,13824));self.assertFalse(p['physicalSupportExemption']);self.assertFalse(p['identityAccepted']);self.assertEqual(p['rawExtentReasonsRetained'],k.RAW_REASONS)
 def test_unknown_reason(self):self.reject(lambda a:a[0]['reasons'].append('unreviewed-other-reason'))
 def test_raw_pass_not_reinterpreted(self):self.reject(lambda a:a[0].update(passed=True))
 def test_source_sha_changed(self):self.reject(lambda a:a[1].update(sourceSHA256='0'*64))
 def test_world_next_double(self):self.reject(lambda a:a[2].__setitem__((0,0,0),np.nextafter(a[2][0,0,0],np.inf)))
 def test_world_y_changed(self):self.reject(lambda a:a[2].__setitem__((500,1,1),a[2][500,1,1]+.001))
 def test_world_face_omitted(self):self.reject(lambda a:a.__setitem__(2,a[2][:-1]))
 def test_wrong_model(self):self.reject(lambda a:a[1].update(modelId='unrelated-original'))
 def test_wrong_uid(self):self.reject(lambda a:a[1].update(uid='landsd/91307:0'))
 def test_missing_whole_cell(self):self.reject(lambda a:a[0]['exactWholeCellCoverage'].update(covered=False))
 def test_source_root_changed(self):self.reject(lambda a:a[0]['originalOwnership'].update(originalRootName='wrong'))
 def test_context_faces_omitted(self):self.reject(lambda a:a[5]['nominatedCompleteFaceIDs'].pop())
 def test_context_contact_removed(self):self.reject(lambda a:a[5]['completeDetachedOriginalContexts'][0]['completeFiniteContacts']['contacts'].pop())
 def test_context_geometry_changed(self):self.reject(lambda a:a[5]['nominatedSourceDefinedPatches'][0]['completeOriginalTriangles'][0][0].__setitem__(0,0))
 def test_context_part_changed(self):self.reject(lambda a:a[5]['completeDetachedOriginalContexts'][0].update(component=21))
 def test_context_zero_promoted(self):self.reject(lambda a:a[5].update(structuralRootOrBridgeCredit=True))
 def test_duplicate_current_actor(self):self.reject(lambda a:a[3].append(deepcopy(a[3][0])))
 def test_current_csuid_changed(self):self.reject(lambda a:next(f for f in a[3]if f['uid']==k.UID).update(buildingCSUID='unrelated'))
 def test_primary_inactive(self):self.reject(lambda a:a[4]['features'][0]['attributes'].update(Status='Demolished'))
 def test_primary_id_changed(self):self.reject(lambda a:a[4]['features'][0]['attributes'].update(BuildingID=1))
 def test_primary_duplicate(self):self.reject(lambda a:a[4]['features'].append(deepcopy(a[4]['features'][0])))
 def test_full_source_foreign_guard(self):
  a=self.args();a[3].append(dict(uid='foreign-no-shared-role',rings=[[[10547,-1913],[10561,-1913],[10561,-1895],[10547,-1895],[10547,-1913]]]))
  p=k.proposal(*a);self.assertFalse(p['proposalSpatialGuardsSatisfied']);self.assertGreater(p['fullSourceSpatialChecks']['current']['completeSourceForeignExcessM2'],1);self.assertIn('foreign-no-shared-role',p['allOtherForeignUIDs'])
if __name__=='__main__':unittest.main()
