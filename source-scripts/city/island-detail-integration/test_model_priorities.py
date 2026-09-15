import hashlib,json,tempfile,unittest
from pathlib import Path
from model_priorities import stage_priorities
class PriorityGate(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.model={'uid':'landsd/1:0','sha256':'source','modelId':'native','buildingCSUID':'csuid','priority':'detail','supportDependencies':[],'recordedBaseHeight':2}
  self.cat=self.put('3d-viewer/city/cat.json',{'models':[self.model]})
  self.evidence=self.ref('evidence.json',{'views':['desktop','mobile']})
  self.review={'catalogues':[{'url':'city/cat.json','source':'3d-viewer/city/cat.json','oldSHA256':self.sha(self.cat),'models':['landsd/1:0']}],'changes':[{'uid':'landsd/1:0','catalogue':'3d-viewer/city/cat.json','modelSHA256':'source','modelId':'native','buildingCSUID':'csuid','oldPriority':'detail','priority':'landmark'}],'evidence':self.evidence}
  self.approval=self.ref('approval.json',{'status':'approved-for-integration'})
 def tearDown(self):self.tmp.cleanup()
 def sha(self,p):return hashlib.sha256(p.read_bytes()).hexdigest()
 def put(self,name,value):
  p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value));return p
 def ref(self,name,value):
  p=self.put(name,value);return {'path':name,'sha256':self.sha(p)}
 def run_gate(self,edits=None):
  edits={} if edits is None else edits;report={};entry={**self.ref('review.json',self.review),'visualApproval':self.approval}
  stage_priorities(self.root,{'priorityReviews':[entry]},{'officialModelCatalogues':['city/cat.json']},edits,report);return edits,report
 def test_changes_only_priority_and_preserves_other_staged_metadata(self):
  staged={**self.model,'supportDependencies':['podium']};before=self.cat.read_bytes();edits,report=self.run_gate({self.cat:json.dumps({'models':[staged]}).encode()})
  self.assertEqual(json.loads(edits[self.cat])['models'][0],{**staged,'priority':'landmark'});self.assertEqual(self.cat.read_bytes(),before);self.assertEqual(len(report['priorityUpdates']),1)
 def test_stale_catalogue_or_identity_rejected(self):
  self.review['changes'][0]['modelSHA256']='wrong'
  with self.assertRaisesRegex(AssertionError,'identity'):self.run_gate()
  self.review['changes'][0]['modelSHA256']='source';self.cat.write_text(self.cat.read_text()+' ')
  with self.assertRaisesRegex(AssertionError,'catalogue changed'):self.run_gate()
 def test_unreviewed_evidence_and_unknown_priority_rejected(self):
  self.review['changes'][0]['priority']='unbounded'
  with self.assertRaisesRegex(AssertionError,'Unsupported'):self.run_gate()
  self.review['changes'][0]['priority']='landmark';self.put('evidence.json',{'changed':True})
  with self.assertRaisesRegex(AssertionError,'review changed'):self.run_gate()
if __name__=='__main__':unittest.main()
