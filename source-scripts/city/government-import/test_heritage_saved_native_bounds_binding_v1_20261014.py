"""Metadata authentication and exact closed-boundary counterfixtures only."""
import copy,unittest
from heritage_saved_native_bounds_binding_v1_20261014 import bind_record,closed_disjoint
class CachedBounds(unittest.TestCase):
    def fixture(self):
        e=dict(uid='landsd/1:0',sha256='a'*64,triangles=1,verticalPlacementOffsetHKPD=0.0)
        d=dict(uid=e['uid'],rawCurrentEntry=copy.deepcopy(e),source=dict(sha256=e['sha256']))
        box=[[2.,0.,2.],[3.,1.,3.]]
        p=dict(sourceSHA256=e['sha256'],allOriginalPositionVerticesAccounted=True,completeOriginalTriangles=1,completeOriginalPositionVertices=3,originalWholeSourceBounds=box)
        r=dict(uid=e['uid'],sourceSHA256=e['sha256'],completeFaces=1,completePositionVertices=3,completeOriginalPOSITIONProof=p,actualRenderMeshes=[dict(wholePositionVerticesIncludingUnused=True,completePositionVertices=3,completeIndexedFaces=1)],wholeUnusedPositionVerticesIncluded=True,sourceFacesOmitted=0,completeLiteralBounds=box,completeLeftAssociatedF32Bounds=box,completeBalancedF32Bounds=box)
        return e,d,r
    def test_exact_all_four_modes_closed_relation_holds_on_touch(self):
        e,d,r=self.fixture();b=bind_record(e,d,r);self.assertTrue(closed_disjoint(b,[0,0,1,1]))
        r['completeBalancedF32Bounds']=[[1.,0.,0.],[2.,1.,1.]];self.assertFalse(closed_disjoint(bind_record(e,d,r),[0,0,1,1]))
    def test_changed_source_or_entry_signed_zero_or_missing_unused_fails_closed(self):
        for mutate in [lambda e,d,r:e.update(sha256='b'*64),lambda e,d,r:e.update(verticalPlacementOffsetHKPD=-0.0),lambda e,d,r:r.update(wholeUnusedPositionVerticesIncluded=False)]:
            e,d,r=self.fixture();mutate(e,d,r)
            with self.assertRaises(AssertionError):bind_record(e,d,r)
    def test_missing_source_faces_or_bad_bounds_are_not_outside_credit(self):
        for mutate in [lambda r:r.update(sourceFacesOmitted=1),lambda r:r.update(completePositionVertices=4),lambda r:r.update(completeLeftAssociatedF32Bounds=[[float('nan'),0.,0.],[3.,1.,3.]])]:
            e,d,r=self.fixture();mutate(r)
            with self.assertRaises(AssertionError):bind_record(e,d,r)
    def test_actual_packet_declaration_rows_are6649_plus1_plus3_with_unique6653_UIDs(self):
        import heritage165054_saved_current_native_bounds_reconciliation_v1_20261014 as a
        seen=set()
        for expected,(folder,_,file,key)in zip([6649,1,3],a.PACKETS):
            d=a.BASE/folder;declared=a.read(d/'input.json.gz')[key];rows=a.read(d/file)['rows']
            self.assertEqual(len(declared),expected);self.assertEqual(len(rows),expected)
            uids={r['uid']for r in declared};self.assertEqual(uids,{r['uid']for r in rows});self.assertFalse(seen.intersection(uids));seen.update(uids)
        self.assertEqual(len(seen),6653)
if __name__=='__main__':unittest.main()
