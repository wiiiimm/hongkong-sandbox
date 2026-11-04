import unittest,json,gzip,copy
from pathlib import Path
from heritage_saved_interface_schema_v1_20261014 import validate_saved_contacts
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'docs/astra-city/government-import'
def packet(p):return json.loads(gzip.decompress((BASE/p).read_bytes()))
class SavedSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.basic=packet('government-xl-heritage165054-starmart57455-current-finite-collision-draft-v3-20261014/collision-output-v3/diagnostic.json.gz')
        cls.original=packet('government-xl-heritage-starmart-original91-acquisition-contact-draft-v2-20261014/original-source-contact-output-v2/diagnostic.json.gz')
    def test_real_saved_fourViews_schema(self):self.assertEqual(validate_saved_contacts(self.basic,self.original)['savedCurrentBASICCrossingsPerView'],14)
    def test_no_chosen_contact_shortcut(self):
        b=copy.deepcopy(self.basic);b['fourViews'][0]['fullFiniteSurfaceContacts']['contacts'].pop()
        with self.assertRaises(AssertionError):validate_saved_contacts(b,self.original)
    def test_missing_arithmetic(self):
        o=copy.deepcopy(self.original);o['allFourViews'].pop()
        with self.assertRaises(AssertionError):validate_saved_contacts(self.basic,o)
    def test_no_foreign_ownership_exception(self):
        b=copy.deepcopy(self.basic);b['noOwnershipException']=False
        with self.assertRaises(AssertionError):validate_saved_contacts(b,self.original)
    def test_no_volumetric_credit_from_crossing(self):
        o=copy.deepcopy(self.original);o['allFourViews'][0]['pairs']['Museum-vs-originalStar']['contacts']['contacts'][0]['crossingDiagnostic']['volumetricCollisionProved']=True
        with self.assertRaises(AssertionError):validate_saved_contacts(self.basic,o)
if __name__=='__main__':unittest.main()
