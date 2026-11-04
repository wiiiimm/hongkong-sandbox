import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from illustrative_foundations import stage_illustrative_foundations
class FoundationTests(unittest.TestCase):
 def run_case(self,change=None):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);tile='city/data/tiles/test.json';p=root/'3d-viewer'/tile;p.parent.mkdir(parents=True)
   b=dict(uid='roof',kind='roof',structureType='Open-sided Structure',baseSource='terrain-estimated',heightSource='estimated',base=7,height=3,rings=[[[0,0],[1,0],[1,1]]])
   data=dict(buildings=[b,dict(uid='unrelated',base=9)]);enc=lambda d:json.dumps(d).encode();p.write_bytes(enc(data));load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
   evidence=root/'review.json';evidence.write_bytes(enc(dict(uid='roof',fullPostFootprintsMeetGround=True,wholeRoofClear=True)))
   proposal=root/'proposal.json';proposal.write_bytes(enc(dict(uid='roof',foundationBase=5,originalBase=7)))
   update=dict(uid='roof',tile=tile,tileSHA256=sha(p),before=copy.deepcopy(b),foundationBase=5,evidence=dict(path='review.json',sha256=sha(evidence)),proposal=dict(path='proposal.json',sha256=sha(proposal)))
   manifest=dict(tiles=[dict(url=tile,bytes=len(p.read_bytes()))]);edits={};report={}
   if change:change(update,p,b,enc)
   before=p.read_bytes();stage_illustrative_foundations(root,dict(illustrativeFoundations=[update]),manifest,edits,report,load,sha,enc)
   self.assertEqual(p.read_bytes(),before);after=json.loads(edits[p]);self.assertEqual(after['buildings'][1],data['buildings'][1]);self.assertEqual(after['buildings'][0],{**b,'foundationBase':5,'foundationPolicy':'terrain-derived-illustrative-posts'});self.assertEqual(manifest['tiles'][0]['bytes'],len(edits[p]))
 def test_stage_only_preserves_fields(self):self.run_case()
 def test_wrong_value_rejected(self):
  with self.assertRaises(AssertionError):self.run_case(lambda u,*_:u.update(foundationBase=4))
 def test_changed_tile_rejected(self):
  with self.assertRaises(AssertionError):self.run_case(lambda u,p,b,e:p.write_bytes(e(dict(buildings=[{**b,'height':20}]))))
 def test_changed_form_rejected(self):
  with self.assertRaises(AssertionError):self.run_case(lambda u,*_:u['before'].update(base=8))
 def test_bad_evidence_rejected(self):
  with self.assertRaises(AssertionError):self.run_case(lambda u,*_:u['evidence'].update(sha256='bad'))
 def test_nonfinite_rejected(self):
  with self.assertRaises(AssertionError):self.run_case(lambda u,*_:u.update(foundationBase=float('nan')))
if __name__=='__main__':unittest.main()
