import unittest,hashlib
import numpy as np
from copy import deepcopy
from test_authored_wall_roof_paths_20261009 import fixture
from test_original_face_ground_crossing_20261009 import flat
from test_unchanged_open_exterior_paths_20261009 import binding
from original_face_ground_crossing_v2_20261009 import face_ground_context
from unchanged_closed_column_role_v2_20261009 import canonical_sha
from unchanged_authored_crossing_wall_role_20261009 import verify_wall_role

def packet(tri=None,foreign=None):
 tri=fixture() if tri is None else tri;ground=flat()
 contexts=[dict(face_ground_context(t,ground),sourceFace=i) for i,t in enumerate(tri)]
 walls=[i for i,c in enumerate(contexts) if c['minimum']['minimumGapM']<-.5]
 role={'role':'original-provider-exterior-ground-crossing-walls','sourceSHA256':'source','originalFaceCount':len(tri),'wallFaces':walls,'uid':'candidate','providerExteriorProvenanceBinding':{'sourceInfo':'provider-exterior-source-description'}}
 mesh=np.asarray([[[10,0,10],[11,0,10],[10,1,11]]] if foreign is None else foreign,float)
 actor={'uid':'other','worldTriangles':mesh.tolist(),'currentSourceBinding':{'tileSHA':'tile','formSHA':'form'}}
 record={'uid':'other','worldTrianglesSHA256':hashlib.sha256(mesh.tobytes()).hexdigest(),'currentSourceBinding':actor['currentSourceBinding']}
 scope={'completeCurrentActorScope':True,'actors':[actor],'expectedActorManifest':[record],'currentGroupBoundaryBinding':{'candidateUID':'candidate','ownedUIDs':['candidate'],'currentScopeUIDs':['candidate','other'],'manifestSHA256':'current','currentFormInputHashes':{'tile':'sha'},'nativeCatalogueInputHashes':{'catalogue':'sha'}}}
 b=binding(tri);b.update(sourceSHA256='source',drawnGroundSHA256=hashlib.sha256(ground.tobytes()).hexdigest(),continuousFaceContextsSHA256=canonical_sha(contexts),reviewedOriginalWallRoleSHA256=canonical_sha(role),currentForeignScopeSHA256=canonical_sha({k:scope[k] for k in ['completeCurrentActorScope','expectedActorManifest','currentGroupBoundaryBinding']}))
 return tri,ground,contexts,{'expected_binding':b,'current_binding':deepcopy(b),'expected_role':role,'foreign_scope':scope}
def check(p):return verify_wall_role(*p[:3],**p[3])
class WallRoleTests(unittest.TestCase):
 def test_complete_role_only(self):
  r=check(packet());self.assertTrue(r['verifiedWallRole']);self.assertEqual(r['rawClearanceFailingFacesRetained'],[2,3]);self.assertFalse(r['installationApproved']);self.assertFalse(r['closedSolidCertified'])
 def test_detached_wall(self):
  t=fixture();t[2:,:,0]+=4;self.assertFalse(check(packet(t))['verifiedWallRole'])
 def test_buried_upward(self):
  t=fixture();t[:2,:,1]=-1;self.assertFalse(check(packet(t))['verifiedWallRole'])
 def test_missing_ground(self):
  p=packet();p[2][0]['groundProjectionCovered']=False;p[3]['current_binding']['continuousFaceContextsSHA256']=canonical_sha(p[2]);p[3]['expected_binding']=deepcopy(p[3]['current_binding'])
  with self.assertRaisesRegex(AssertionError,'Missing whole-face'):check(p)
 def test_changed_source(self):
  p=packet();p[3]['current_binding']['sourceSHA256']='changed'
  with self.assertRaises(AssertionError):check(p)
 def test_changed_context(self):
  p=packet();p[2][0]['minimum']['minimumGapM']=.3
  with self.assertRaises(AssertionError):check(p)
 def test_omitted_face(self):
  p=packet();p[2].pop()
  with self.assertRaises(AssertionError):check(p)
 def test_foreign_intersection(self):
  r=check(packet(foreign=[[[1,1,-1],[1,1,1],[1,3,0]]]));self.assertFalse(r['verifiedWallRole']);self.assertTrue(r['foreignIntersections'])
 def test_omitted_actor(self):
  p=packet();p[3]['foreign_scope']['actors']=[]
  with self.assertRaisesRegex(AssertionError,'Omitted'):check(p)
 def test_no_scope(self):
  p=packet();p[3]['foreign_scope']={}
  with self.assertRaisesRegex(AssertionError,'Missing complete'):check(p)
 def test_basic_overlap(self):
  p=packet();a=p[3]['foreign_scope']['actors'][0];a.update(proofType='current-basic-full-footprint',originalCurrentRings=[[[-1,-1],[3,-1],[3,3],[-1,3],[-1,-1]]])
  with self.assertRaisesRegex(AssertionError,'intersects credited wall'):check(p)
if __name__=='__main__':unittest.main()
