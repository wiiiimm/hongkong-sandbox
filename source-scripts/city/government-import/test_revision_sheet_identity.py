import unittest
from revision_sheet_identity import source_sheet


class RevisionSheetIdentity(unittest.TestCase):
    def fixture(self):
        model={'sourceEntry':'BUILDING/a.gltf','sourceHashes':{'BUILDING/a.gltf':'a','BUILDING/a.bin':'b'}}
        revision={'sheet':'11-SW-9A','download':'cache/receipt.json','archiveSHA256':'archive','directorySHA256':'directory'}
        receipt={'sheet':revision['sheet'],'sha256':'archive','directorySHA256':'directory','entries':[{'name':n,'sha256':h} for n,h in model['sourceHashes'].items()]}
        return model,revision,receipt

    def test_cache_path_need_not_contain_sheet(self):
        model,revision,receipt=self.fixture()
        self.assertEqual(source_sheet(model,[revision],reader=lambda _:receipt),'11-SW-9A')

    def test_one_changed_dependency_rejects(self):
        model,revision,receipt=self.fixture();receipt['entries'][1]['sha256']='changed'
        with self.assertRaises(AssertionError):source_sheet(model,[revision],reader=lambda _:receipt)

    def test_ambiguous_sheet_receipts_reject(self):
        model,revision,receipt=self.fixture()
        with self.assertRaises(AssertionError):source_sheet(model,[revision,revision],reader=lambda _:receipt)

    def test_archive_revision_mismatch_rejects(self):
        model,revision,receipt=self.fixture();receipt['directorySHA256']='changed'
        with self.assertRaises(AssertionError):source_sheet(model,[revision],reader=lambda _:receipt)


if __name__=='__main__':unittest.main()
