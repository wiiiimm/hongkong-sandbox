"""Actual complete source fixtures and distinct mounting-policy counterexamples."""
import copy,unittest
import numpy as np
from run import ROOT,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import elements24_named_original_mounted_visual_surface_proposal_v1_20261011 as k

def actual_fixture():
 base=ROOT/'docs/astra-city/government-import'
 names={
  'graph':'xl-terrain-recovery-20261011-elements-complete-owned-original-contact-graph-v1',
  'bands':'xl-terrain-recovery-20261011-elements132-four-stream-qualified-host-association-v1',
  'finite':'xl-terrain-recovery-20261011-elements-owned-four-stream-complete-finite-v1',
  'attrs':'xl-terrain-recovery-20261011-elements-sun-star-two-current-render-attribute-capture-v1'}
 docs={}
 for label,name in names.items():
  folder=base/name;r=read(folder/'result.json');p=folder/('actual-render-attributes.json.gz'if label=='attrs'else'diagnostic.json.gz')
  assert dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))in r['evidenceRefs'];docs[label]=read(p)
 worlds={};original=[]
 for s in docs['graph']['binding']['completeSourceInputs'][:2]:
  p=ROOT/s['asset']['path'];raw=p.read_bytes();assert digest(raw)==s['sourceSHA256'];original.append(decode_original_world_triangles(raw))
 worlds['providerOriginal']=np.concatenate(original)
 for mode,field in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftFloat32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedFloat32','completeExplicitBalancedFloat32WorldPosition')]:
  worlds[mode]=np.concatenate([np.asarray(a[field],float).reshape(-1,3)[np.asarray(a['completeOriginalIndex'],int).reshape(-1,3)]for a in docs['attrs']['rows']])
 assert all(w.shape==(23809,3,3)for w in worlds.values())
 packages={}
 for part,faces in k.NAMED_SOURCE_PART_FACES.items():
  uid='landsd/204145:0'if max(faces)<12129 else 'landsd/204143:0';offset=0 if uid=='landsd/204145:0'else 12129;contexts={};hosts={}
  for mode in k.MODES:
   row=next(r for r in docs['bands']['rows']if r['mode']==mode);a=next(a for a in row['all132OriginalBodyAssociations']if a['originalBody']==part)
   finite=next(r for r in docs['finite']['rows']if r['mode']==mode and r['uid']==uid)
   assert k.world_sha(worlds[mode])==row['completeWorldSHA256']
   assert k.world_sha(worlds[mode][:12129]if offset==0 else worlds[mode][12129:])==finite['completeWorldSHA256']
   contexts[mode]=dict(completeOwnedWorldSHA256=row['completeWorldSHA256'],association=a,allCompletePartFiniteFaces=[finite['allFaces'][f-offset]for f in faces])
   hosts[mode]=a['completeHostSelection']['completeQualifiedSameActorHostFaces']
  packages[part]=dict(part=part,uid=uid,source_sha=k.SOURCE_SHA[uid],worlds=worlds,contexts=contexts,qualified_hosts=hosts,expected_binding=k.binding(part,uid,k.SOURCE_SHA[uid],worlds,contexts,hosts))
 return docs,packages

class ActualNamedVisualSurfaceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.docs,cls.packages=actual_fixture()
 def run_part(self,part,**change):
  p=self.packages[part].copy();p.update(change);return k.verify(**p)
 def test_all24_complete_actual_fourstream_fixtures(self):
  for i in k.NAMED_SOURCE_PART_FACES:
   with self.subTest(part=i):
    r=self.run_part(i);self.assertTrue(r['conditionalSourceVisualRoleProposal']);self.assertFalse(r['structuralRootCredit']);self.assertFalse(r['structuralBridgeCredit']);self.assertFalse(r['currentAcceptance']);self.assertEqual(len(r['allFourStreamProofs']),4)
 def test_three_U_edges_preserve_actual_free_interior_negative(self):
  r=self.run_part(500);self.assertEqual(r['allFourStreamProofs'][0]['completeNamedMountEdgeCount'],3);self.assertFalse(r['allFourStreamProofs'][0]['wholeInteriorBandPositive'])
 def test_folded_source_lower_and_both_terminal_chains(self):
  r=self.run_part(509);self.assertEqual(r['allFourStreamProofs'][0]['completeNamedMountEdgeCount'],4);self.assertEqual(len(r['allFourStreamProofs'][0]['unqualifiedFreeEdgeFindings']),2)
 def test934_preserves_free_source_end_and_upper_edges(self):
  r=self.run_part(934);self.assertEqual(r['allFourStreamProofs'][0]['completeNamedMountEdgeCount'],3);self.assertEqual(len(r['allFourStreamProofs'][0]['unqualifiedFreeEdgeFindings']),5)
 def test_changed_pose_rejects_original_frozen_binding(self):
  worlds=self.packages[500]['worlds'].copy();worlds['actualLiteral']=worlds['actualLiteral'].copy();worlds['actualLiteral'][9080,0,0]+=.2
  with self.assertRaises(AssertionError):self.run_part(500,worlds=worlds)
 def test_removed_actual_mount_edge_proof_rejects(self):
  contexts=copy.deepcopy(self.packages[500]['contexts']);contexts['actualLiteral']['association']['allActualIncidenceOneBoundaryEdgeProofs'].pop()
  with self.assertRaises(AssertionError):self.run_part(500,contexts=contexts)
 def test_forged_complete_free_edge_cannot_replace_named_mount(self):
  p=self.packages[500];contexts=copy.deepcopy(p['contexts']);a=contexts['actualLiteral']['association'];a['allActualIncidenceOneBoundaryEdgeProofs'][0]['wholeEdgeWithinExistingFiniteHostBand']=False
  with self.assertRaises(AssertionError):self.run_part(500,contexts=contexts)
 def test_partial_lower_chain_cannot_be_called_complete(self):
  contexts=copy.deepcopy(self.packages[509]['contexts']);contexts['providerOriginal']['association']['allActualIncidenceOneBoundaryEdgeProofs'].pop()
  with self.assertRaises(AssertionError):self.run_part(509,contexts=contexts)
 def test_host_detachment_or_visual_bootstrap_rejects(self):
  hosts=self.packages[500]['qualified_hosts'].copy();hosts['actualLiteral']=[]
  with self.assertRaises(AssertionError):self.run_part(500,qualified_hosts=hosts)
 def test_foreign_actor_host_rejects(self):
  contexts=copy.deepcopy(self.packages[500]['contexts']);contexts['actualLiteral']['association']['completeHostSelection']['selectedGlobalHostFaces']=[12129]
  with self.assertRaises(AssertionError):self.run_part(500,contexts=contexts)
 def test_changed_ground_or_wholefacet_failure_rejects(self):
  contexts=copy.deepcopy(self.packages[509]['contexts']);contexts['actualLiteral']['allCompletePartFiniteFaces'][0]['strictlyExposedWholeFacet']=False
  with self.assertRaises(AssertionError):self.run_part(509,contexts=contexts)
 def test_extra_or_missing_source_facet_rejects(self):
  contexts=copy.deepcopy(self.packages[500]['contexts']);contexts['providerOriginal']['association']['completeOriginalFaceIds']=[9080]
  with self.assertRaises(AssertionError):self.run_part(500,contexts=contexts)
 def test_wrong_provider_source_or_actor_rejects(self):
  with self.assertRaises(AssertionError):self.run_part(500,source_sha='0'*64)
  with self.assertRaises(AssertionError):self.run_part(500,uid='landsd/204143:0')
 def test_missing_render_arithmetic_stream_rejects(self):
  worlds=self.packages[500]['worlds'].copy();worlds.pop('explicitBalancedFloat32')
  with self.assertRaises(AssertionError):self.run_part(500,worlds=worlds)
 def test_unqualified_curved_roof_not_added_to_policy(self):
  with self.assertRaises(AssertionError):k.verify(902,'landsd/204143:0',k.SOURCE_SHA['landsd/204143:0'],self.packages[500]['worlds'],{}, {},expected_binding={})
 def test_detached_topology_cannot_define_lower_chain(self):
  w=self.packages[509]['worlds']['providerOriginal'].copy();w[11367,0]+=np.array([1.,0.,0.])
  with self.assertRaises(AssertionError):k.original_mount(509,w,k.NAMED_SOURCE_PART_FACES[509])
if __name__=='__main__':unittest.main()
