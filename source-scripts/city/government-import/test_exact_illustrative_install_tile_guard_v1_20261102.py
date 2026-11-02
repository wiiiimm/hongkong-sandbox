import copy,hashlib,json,unittest
from exact_illustrative_install_tile_guard_v1_20261102 import verify
class ExactPublishedTileTests(unittest.TestCase):
    def setUp(self):
        self.old={'buildings':[{'uid':'canopy','base':8},{'uid':'unrelated','base':10}]}
        self.raw=json.dumps(self.old).encode();self.new=copy.deepcopy(self.old);self.new['buildings'][0].update(foundationBase=5,foundationPolicy='terrain-derived-illustrative-posts')
        self.updates=[dict(uid='canopy',tile='tile.json',tileSHA256=hashlib.sha256(self.raw).hexdigest(),before=self.old['buildings'][0],foundationBase=5)]
    def call(self,new=None,extra=False,bad_manifest=False):
        raw=json.dumps(self.new if new is None else new).encode();tiles=[dict(url='tile.json',bytes=len(self.raw),bounds=[0,0,1,1]),dict(url='unrelated.json',bytes=20)]
        after=copy.deepcopy(tiles);after[0]['bytes']=len(raw)
        if bad_manifest:after[1]['bytes']=21
        old={'tile.json':self.raw};newbytes={'tile.json':raw}
        if extra:old['unrelated.json']=b'{}';newbytes['unrelated.json']=b'{}'
        return verify(tiles,after,old,newbytes,self.updates)
    def test_exact_transaction(self):self.assertTrue(self.call())
    def test_reject_unrelated_building_edit(self):
        bad=copy.deepcopy(self.new);bad['buildings'][1]['base']=11
        with self.assertRaises(AssertionError):self.call(bad)
    def test_reject_missing_policy(self):
        bad=copy.deepcopy(self.new);del bad['buildings'][0]['foundationPolicy']
        with self.assertRaises(AssertionError):self.call(bad)
    def test_reject_unrelated_manifest_change(self):
        with self.assertRaises(AssertionError):self.call(bad_manifest=True)
    def test_reject_unplanned_tile(self):
        with self.assertRaises(AssertionError):self.call(extra=True)
    def test_reject_stale_before_hash(self):
        self.updates[0]['tileSHA256']='0'*64
        with self.assertRaises(AssertionError):self.call()
if __name__=='__main__':unittest.main()
