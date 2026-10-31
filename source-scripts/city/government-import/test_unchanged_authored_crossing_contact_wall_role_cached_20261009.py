"""Cache reuse must never reuse current actor acceptance."""
import unittest
from unittest.mock import patch
from test_unchanged_authored_crossing_contact_wall_role_20261009 import packet
from exact_original_wall_contact_paths_20261009 import contact_paths
from unchanged_authored_crossing_contact_wall_role_cached_20261009 import verify_wall_role

def check(p):
    args=p[3]
    graph=contact_paths(p[0],p[2],args['expected_role']['wallFaces'],
                        expected_source_binding=args['expected_binding'],current_source_binding=args['current_binding'])
    with patch('unchanged_authored_crossing_contact_wall_role_cached_20261009.load_and_replay', return_value=graph) as load:
        r=verify_wall_role(*p[:3],**args,verified_source_graph_result='fenced-receipt')
        load.assert_called_once()
        return r

class CachedForeignTests(unittest.TestCase):
    def test_current_disjoint_scope_passes_without_cached_acceptance(self):
        r=check(packet());self.assertTrue(r['verifiedWallRole']);self.assertFalse(r['installationApproved'])
    def test_current_foreign_intersection_still_rejects(self):
        r=check(packet(foreign=[[[1,1,-1],[1,1,1],[1,3,0]]]));self.assertFalse(r['verifiedWallRole']);self.assertTrue(r['foreignIntersections'])
    def test_current_actor_omission_still_rejects(self):
        p=packet();p[3]['foreign_scope']['actors']=[]
        with self.assertRaisesRegex(AssertionError,'Omitted'):check(p)
    def test_current_scope_binding_change_still_rejects(self):
        p=packet();p[3]['foreign_scope']['currentGroupBoundaryBinding']['manifestSHA256']='changed'
        with self.assertRaises(AssertionError):check(p)

if __name__=='__main__':unittest.main()
