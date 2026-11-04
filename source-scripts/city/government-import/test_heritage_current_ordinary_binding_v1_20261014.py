import unittest,copy
import heritage165054_current_ordinary_physical_v1_20261014 as a
class Binding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.row,cls.identity,cls.context,cls.forms,cls.tiles,*_=a.inputs()
    def test_actual_positive_identity_and_exact_current_source_forms(self):self.assertTrue(a.bind_saved_identity(self.row,self.identity,self.context,self.forms,self.tiles)['identityPassed'])
    def test_rejected_or_partial_identity_not_transferred(self):
        for key,value in [('passed',False),('completeOriginalFaceCount',15139)]:
            d=copy.deepcopy(self.identity);d[key]=value
            with self.assertRaises(AssertionError):a.bind_saved_identity(self.row,d,self.context,self.forms,self.tiles)
    def test_new_local_actor_or_tile_hash_rejects(self):
        with self.assertRaises(AssertionError):a.bind_saved_identity(self.row,self.identity,self.context,self.forms[:-1],self.tiles)
        tiles=dict(self.tiles);tiles[next(iter(tiles))]='0'*64
        with self.assertRaises(AssertionError):a.bind_saved_identity(self.row,self.identity,self.context,self.forms,tiles)
    def test_no_runtime_or_foreign_exemption_transplant(self):
        d=copy.deepcopy(self.identity);d['runtimeExemption']=True
        with self.assertRaises(AssertionError):a.bind_saved_identity(self.row,d,self.context,self.forms,self.tiles)
if __name__=='__main__':unittest.main()
