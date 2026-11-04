"""Unexecuted actual saved-candidate and adverse representation fixtures."""
import copy,gzip,json,unittest
from pathlib import Path
import polyu_sports_saved_candidate_actual_edge_incidents_draft_v1_20261013 as m
R=Path(__file__).resolve().parents[3];D=R/'docs/astra-city/government-import/government-xl-polyu-sports305582-authentic-local-private-terrain-v2-20261013'
class Actual(unittest.TestCase):
 def setUp(self):
  q=json.loads(gzip.decompress((D/'full-computed-private-candidate-and-account.json.gz').read_bytes()));self.a=q['account'];self.p=json.loads((R/q['candidatePath']).read_bytes())
 def test_complete_actual_candidate_all_incidents(self):
  q=m.actual_complete_edge_incidents(self.p,self.a);self.assertEqual(q['completeIncidentCount'],9642);self.assertTrue(q['everyOriginalFacetLocalEdgeAccounted']);self.assertEqual({x['outputFacet']for e in q['completeActualPackedEdgeInventory']for x in e['allIncidentRecords']},set(range(3214)))
 def test_changed_packed_point_rejected(self):
  self.p['nativeMesh']['position'][0]+=1
  with self.assertRaises(AssertionError):m.actual_complete_edge_incidents(self.p,self.a)
 def test_missing_incident_facet_rejected(self):
  self.a['completeOutputFacetLineage'].pop()
  with self.assertRaises(AssertionError):m.actual_complete_edge_incidents(self.p,self.a)
 def test_duplicate_source_facet_id_rejected(self):
  self.a['completeOutputFacetLineage'][1]['outputFacet']=0
  with self.assertRaises(AssertionError):m.actual_complete_edge_incidents(self.p,self.a)
 def test_synthetic_exclusion_kind_rejected(self):
  self.a['completeOutputFacetLineage'][0]['classification']='unchanged-v4-exterior'
  with self.assertRaises(AssertionError):m.actual_complete_edge_incidents(self.p,self.a)
 def test_reordered_actual_indices_rejected(self):
  self.p['nativeMesh']['index'][0],self.p['nativeMesh']['index'][1]=self.p['nativeMesh']['index'][1],self.p['nativeMesh']['index'][0]
  with self.assertRaises(AssertionError):m.actual_complete_edge_incidents(self.p,self.a)
 def test_missing_actual_classification_rejected(self):
  del self.a['completeOutputFacetLineage'][0]['classification']
  with self.assertRaises(KeyError):m.actual_complete_edge_incidents(self.p,self.a)
 def test_source_layer_retention_claim_changed_rejected(self):
  self.a['completeOutputFacetLineage'][0]['noHeightLayerDeleted']=False
  with self.assertRaises(AssertionError):m.actual_complete_edge_incidents(self.p,self.a)
if __name__=='__main__':unittest.main(verbosity=2)
