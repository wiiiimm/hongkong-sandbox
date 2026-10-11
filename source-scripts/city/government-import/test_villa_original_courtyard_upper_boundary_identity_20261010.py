"""Actual complete Villa source fixtures; no synthetic geometry acceptance."""
import copy
import unittest
from run import ROOT, read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from villa_original_courtyard_upper_boundary_identity_20261010 import named_proof, UID, FOREIGN

BASE = ROOT/'docs/astra-city/government-import'
RAW = BASE/'government-xl-villa-premiere-complete-record-projection-identity-20261010'
CONTEXT = read(BASE/'government-xl-villa-premiere-original-overlap-primary-context-20261010/diagnostic.json.gz')
ROW = read(RAW/'selection.json.gz')['rows'][0]
PREVIOUS = read(RAW/'identity.json')
OWN = decode_original_world_triangles((ROOT/ROW['candidate']['path']).read_bytes())
MISSING = read(BASE/'government-xl-villa-premiere-two-original-recovery-20261010/selection.json.gz')['missing'][0]


def fixture():
    return [copy.deepcopy(PREVIOUS), copy.deepcopy(ROW), OWN.copy(),
            copy.deepcopy(CONTEXT['currentForms']), copy.deepcopy(CONTEXT['exactPrimary']), copy.deepcopy(MISSING)]


def foreign(args):
    return next(b for b in args[3] if b['uid'] == FOREIGN)


class OriginalTests(unittest.TestCase):
    def rejected(self, mutate):
        args = fixture()
        mutate(args)
        with self.assertRaises((AssertionError, KeyError, ValueError)):
            named_proof(*args)

    def test_actual_source_proposed_identity_only(self):
        p = named_proof(*fixture())
        self.assertTrue(p['passed'])
        self.assertFalse(p['physicalAccepted'])
        self.assertFalse(p['installationApproved'])
        self.assertFalse(p['surveyedCanopySeparationClaim'])
        self.assertFalse(p['wholeOwnMainBodyOverheadClaim'])
        self.assertFalse(p['foreignCollisionExemption'])
        self.assertFalse(p['foreignTerrainExemption'])
        self.assertEqual(len(p['allRawNamedOverlapFaceIds']), 16)
        self.assertEqual(len(p['completeOriginalMainBodyFaceIds']), 11783)
        self.assertEqual(p['completeOriginalParts'], 58)
        self.assertEqual(len(p['rawUnrelatedOverlapReasonsRetained']), 2)
        self.assertGreater(p['independentFullSourceSpatialChecks']['primary']['rawNamedForeignExcessM2'], 1)

    def test_other_independent_failure_preserved(self):
        args = fixture(); args[0]['reasons'].append('independent-current-failure')
        p = named_proof(*args)
        self.assertFalse(p['passed']); self.assertIn('independent-current-failure', p['reasons'])

    def test_uid_mutation(self): self.rejected(lambda a: a[1].__setitem__('uid', FOREIGN))
    def test_source_sha_mutation(self): self.rejected(lambda a: a[1].__setitem__('sourceSHA256', '0'*64))
    def test_model_id_mutation(self): self.rejected(lambda a: a[1].__setitem__('modelId', 'B216223338401063C0'))
    def test_prior_sha_mutation(self): self.rejected(lambda a: a[0].__setitem__('sourceSHA256', '0'*64))
    def test_unowned_source(self): self.rejected(lambda a: a[0]['originalOwnership'].__setitem__('sourceGraphVerified', False))
    def test_wrong_original_root(self): self.rejected(lambda a: a[0]['originalOwnership'].__setitem__('originalRootName', 'B_other'))
    def test_x_mutation(self): self.rejected(lambda a: a[2].__setitem__((0, 0, 0), a[2][0, 0, 0]+.00001))
    def test_y_only_mutation(self): self.rejected(lambda a: a[2].__setitem__((6727, 0, 1), a[2][6727, 0, 1]+.00001))
    def test_nonfinite(self): self.rejected(lambda a: a[2].__setitem__((0, 0, 1), float('nan')))
    def test_missing_face(self): self.rejected(lambda a: a.__setitem__(2, a[2][:-1]))
    def test_reversed_authored_face(self): self.rejected(lambda a: a[2].__setitem__(6727, a[2][6727][::-1]))
    def test_duplicate_current_actor(self): self.rejected(lambda a: a[3].append(copy.deepcopy(a[3][0])))
    def test_foreign_actor_missing(self): self.rejected(lambda a: a.__setitem__(3, [b for b in a[3] if b['uid'] != FOREIGN]))
    def test_own_actor_missing(self): self.rejected(lambda a: a.__setitem__(3, [b for b in a[3] if b['uid'] != UID]))
    def test_duplicate_primary(self): self.rejected(lambda a: a[4].append(copy.deepcopy(a[4][0])))
    def test_inactive_primary(self): self.rejected(lambda a: a[4][0]['attributes'].__setitem__('Status', 'Retired'))
    def test_wrong_primary_type(self): self.rejected(lambda a: a[4][0]['attributes'].__setitem__('BuildingBlockType', 'Tower'))
    def test_wrong_primary_id(self): self.rejected(lambda a: a[4][0]['attributes'].__setitem__('BuildingID', 1))
    def test_wrong_primary_date(self): self.rejected(lambda a: a[4][0]['attributes'].__setitem__('DateCreate', 0))
    def test_wrong_primary_georef(self): self.rejected(lambda a: a[4][0]['attributes'].__setitem__('GeoRefNo', '2162233384'))
    def test_current_canopy_now_surveyed(self):
        def mutate(a):
            foreign(a)['topHeightHKPD'] = 14
            a[4][1]['attributes']['TopHeight'] = 14
            a[5]['currentSource']['building']['topHeightHKPD'] = 14
        self.rejected(mutate)
    def test_false_foreign_ground_metadata(self):
        def mutate(a):
            foreign(a)['baseSource'] = 'landsd'
            a[5]['currentSource']['building']['baseSource'] = 'landsd'
        self.rejected(mutate)
    def test_false_foreign_height_metadata(self):
        def mutate(a):
            foreign(a)['heightSource'] = 'landsd'
            a[5]['currentSource']['building']['heightSource'] = 'landsd'
        self.rejected(mutate)
    def test_actual_current_canopy_reaches_roof(self):
        def mutate(a):
            foreign(a)['height'] = 8
            a[5]['currentSource']['building']['height'] = 8
        self.rejected(mutate)
    def test_foreign_native_now_available(self): self.rejected(lambda a: a[5].__setitem__('exactNativeMatches', 1))
    def test_ambiguous_foreign_native_profile(self): self.rejected(lambda a: a[5].__setitem__('profiles', [{'cacheKey': 'new'}]))
    def test_wrong_missing_foreign_uid(self): self.rejected(lambda a: a[5].__setitem__('uid', UID))
    def test_missing_foreign_snapshot_changed(self): self.rejected(lambda a: a[5]['currentSource']['building'].__setitem__('base', 20))
    def test_current_canopy_shared_boundary_destroyed(self):
        def mutate(a):
            b=foreign(a); b['rings']=[[[x+20, z] for x, z in ring] for ring in b['rings']]
            a[5]['currentSource']['building']=copy.deepcopy(b)
        self.rejected(mutate)
    def test_primary_canopy_overlaps_podium_interior(self):
        def mutate(a):
            p=a[4][1];p['geometry']['rings']=[[[x+20,y] for x,y in ring] for ring in p['geometry']['rings']]
        self.rejected(mutate)


if __name__ == '__main__': unittest.main()
