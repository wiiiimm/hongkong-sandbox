"""Future adapter authentication counterfixtures; synthetic JSON only."""
import copy
import gzip
import hashlib
import json
import unittest
from saved_ground_selection_receipt_adapter_design_v1_20261013 import AuthenticatedSelectionReceipt


def fixture(change=None):
    files={}
    def put(path,obj):
        raw=json.dumps(obj,sort_keys=True).encode()
        if path.endswith('.gz'):raw=gzip.compress(raw,mtime=0)
        files[path]=raw
        return dict(path=path,sha256=hashlib.sha256(raw).hexdigest())
    scope={'selectedFaceIDs':[1,3],'allOtherFacesStrictlyOutside':True}
    rows=[dict(face=i,currentBaselineVerbatim={'sourceFaceSHA256':'face'+str(i),'ordinaryBoundProved':True},
        completeNewGroundSelection={'completeGroundSHA256':'ground','selectedOriginalGroundFaces':[8,9]},
        completeRelevantGroundSHA256='tuple'+str(i),findings={'ordinaryBoundProved':False,'projectionCovered':False,'crossings':[23]})for i in [1,3]]
    chunk=dict(uid='actor',mode='oldModePreserved',wholeWorldSHA256='world',completeNewGroundSHA256='ground',rows=rows)
    world=dict(mode='literal',wholeWorldSHA256='world',completeFaces=4,completeScope=scope,findings={'chunks':None,'completeProcessedFaces':2})
    if change:change(chunk,world)
    cr=put('chunks/a.json.gz',chunk);world['findings']['chunks']=[cr]
    actor=dict(uid='actor',role='held-foreign',sourceSHA256='source',worlds=[world])
    basic=dict(uid='basic',completeFaces=4,completeScope=scope,findings={'worlds':[world]})
    sr=put('summary.json.gz',dict(newGroundSHA256='ground',physicalAccepted=False,installationApproved=False,actors=[actor],completeBasicRows=[basic]))
    ir=put('world-input.json',{'sourceIndexAndPositionBinding':'immutable'})
    receipt={'jobId':'job','evidenceRefs':[sr,cr,ir]};rr=put('result.json',receipt)
    args=dict(uid='actor',mode='literal',actor_kind='source-actor',role='held-foreign',live_source_sha='source',live_world_sha='world',complete_face_count=4,complete_scope=scope,old_ground_sha='ground',independently_bound_input_refs=[ir])
    return files,rr,receipt,sr,args


class Tests(unittest.TestCase):
    def bind(self,change=None):
        f,r,receipt,s,args=fixture(change)
        a=AuthenticatedSelectionReceipt(r,'job',('complete',receipt),f.__getitem__)
        return a,a.bind_world(s,**args),f,r,receipt,s,args

    def test_complete_rows_negative_context_and_original_mode_labels_preserved(self):
        a,w,*_=self.bind();token=w.face(3,'face3')
        self.assertFalse(token['priorCandidateRowVerbatim']['findings']['ordinaryBoundProved'])
        self.assertEqual(token['priorCandidateRowVerbatim']['findings']['crossings'],[23]);a.verify_end()

    def test_wrong_neon_status_result_job_or_file_digest_rejected(self):
        f,r,receipt,s,args=fixture()
        for row,job in [(('running',receipt),'job'),(('complete',{}),'job'),(('complete',receipt),'other')]:
            with self.assertRaises(AssertionError):AuthenticatedSelectionReceipt(r,job,row,f.__getitem__)
        f['world-input.json']+=b' '
        with self.assertRaises(AssertionError):AuthenticatedSelectionReceipt(r,'job',('complete',receipt),f.__getitem__)

    def test_missing_duplicate_extra_or_wrong_ground_rows_rejected(self):
        changes=[lambda c,w:c['rows'].pop(),lambda c,w:c['rows'].append(c['rows'][0]),lambda c,w:c['rows'].append({**c['rows'][0],'face':2}),lambda c,w:c.update(completeNewGroundSHA256='stale')]
        for change in changes:
            with self.assertRaises(AssertionError):self.bind(change)

    def test_wrong_scope_world_source_role_or_count_rejected(self):
        f,r,receipt,s,args=fixture();a=AuthenticatedSelectionReceipt(r,'job',('complete',receipt),f.__getitem__)
        for k,v in [('complete_scope',{'selectedFaceIDs':[1]}),('live_world_sha','wrong'),('live_source_sha','wrong'),('role','owned'),('complete_face_count',5),('old_ground_sha','wrong')]:
            with self.assertRaises(AssertionError):a.bind_world(s,**{**args,k:v})

    def test_missing_receipt_membership_cannot_be_supplied_as_input(self):
        f,r,receipt,s,args=fixture();a=AuthenticatedSelectionReceipt(r,'job',('complete',receipt),f.__getitem__)
        with self.assertRaises(AssertionError):a.bind_world(s,**{**args,'independently_bound_input_refs':[{'path':'unknown.json','sha256':'unknown'}]})

    def test_wrong_source_face_and_unselected_face_rejected(self):
        a,w,*_=self.bind()
        with self.assertRaises(AssertionError):w.face(1,'different-face')
        with self.assertRaises(KeyError):w.face(2,'face2')

    def test_snapshot_token_mutation_does_not_alter_authenticated_row(self):
        a,w,*_=self.bind();t=w.face(1,'face1');t['priorCandidateRowVerbatim']['findings']['ordinaryBoundProved']=True
        t['priorWorldVerbatim']['mode']='relabelled';t['completedReceipt']['sha256']='changed'
        self.assertFalse(w.face(1,'face1')['priorCandidateRowVerbatim']['findings']['ordinaryBoundProved'])
        self.assertEqual(w.face(1,'face1')['priorWorldVerbatim']['mode'],'literal')
        self.assertNotEqual(w.face(1,'face1')['completedReceipt']['sha256'],'changed')

    def test_all_receipt_pins_rechecked_at_end(self):
        a,w,f,*_=self.bind();f['world-input.json']+=b' '
        with self.assertRaises(AssertionError):a.verify_end()

    def test_borrowed_chunk_uid_cannot_credit_basic_actor(self):
        f,r,receipt,s,args=fixture();a=AuthenticatedSelectionReceipt(r,'job',('complete',receipt),f.__getitem__)
        with self.assertRaises(AssertionError):a.bind_world(s,**{**args,'uid':'basic','actor_kind':'affected-BASIC','role':'complete-affected-BASIC-regression'})

if __name__=='__main__':unittest.main()
