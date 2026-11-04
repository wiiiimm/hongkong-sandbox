import copy,gzip,json,unittest
from pathlib import Path
from peninsula_private_group_roof_contract_v1_20261029 import apply,OWNER,ROOF,TOWER
ROOT=Path(__file__).resolve().parents[3]
class PrivateRoofExperimentGuards(unittest.TestCase):
    def setUp(self):
        b=ROOT/'docs/astra-city/government-import'
        self.review=json.loads((b/'government-xl-peninsula-private-group-roof-review-v1-20261029/ROOT-PRIVATE-EXPERIMENT-REVIEW.json').read_text())
        self.models=json.loads((ROOT/'source-scripts/city/government-import/local/government-xl-peninsula-pair-retained-roof-private-browser-v1-20261029/catalogue.json').read_text())['models']
        rows=json.loads(gzip.decompress((b/'government-xl-peninsula-pair-current-v1-20261029-model-scope/270876:0-forms.json.gz').read_bytes()));self.forms={r['building']['uid']:r['building']for r in rows}
    def test_only_exact_group_and_owner_roof_metadata_change(self):
        before=copy.deepcopy(self.models);out=apply(self.models,self.forms,self.review)
        self.assertEqual(self.models,before)
        for old,new in zip(before,out):
            actual=copy.deepcopy(new);self.assertEqual(actual.pop('activationGroup'),sorted([OWNER,TOWER]))
            if old['uid']==OWNER:self.assertEqual(actual.pop('suppressesBuildingUids'),[ROOF])
            self.assertEqual(actual,old)
    def test_changed_source_is_rejected(self):
        self.models[0]['sha256']='0'*64
        with self.assertRaises(AssertionError):apply(self.models,self.forms,self.review)
    def test_changed_current_roof_is_rejected(self):
        self.forms[ROOF]['height']=4
        with self.assertRaises(AssertionError):apply(self.models,self.forms,self.review)
    def test_changed_source_form_is_rejected(self):
        self.forms[OWNER]['base']+=1
        with self.assertRaises(AssertionError):apply(self.models,self.forms,self.review)
    def test_existing_approval_cannot_be_carried_into_private_test(self):
        self.models[0]['publicationApproved']=True
        with self.assertRaises(AssertionError):apply(self.models,self.forms,self.review)
    def test_non_roof_or_unreviewed_revision_cannot_be_suppressed(self):
        for key,value in [('version','5'),('tags',{'building':'yes'})]:
            review=copy.deepcopy(self.review);review['primaryOSMWay'][key]=value
            with self.assertRaises(AssertionError):apply(self.models,self.forms,review)
    def test_publication_and_retargeting_are_rejected(self):
        for key,value in [('publication',True),('installationApproved',True),('roofUid','way/other:0'),('activationGroup',[OWNER])]:
            review=copy.deepcopy(self.review);review[key]=value
            with self.assertRaises(AssertionError):apply(self.models,self.forms,review)
if __name__=='__main__':unittest.main()
