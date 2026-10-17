"""Replay and fence mandatory-original assembly identity, no physical credit."""
import json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from man_hei_current_bound_mandatory_platform_identity_v2_20261010 import DOC as INPUT,UID,PLATFORM,verify_files,module
BATCH='government-xl-man-hei-current-bound-mandatory-platform-promotion-v3-20261010';DOC=INPUT.parent/BATCH;LOCAL=HERE/'local'/BATCH

def main():
    assert not DOC.exists()
    claim=reservations.claim('manhei-mandatory-platform-promotion-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation']
    try:
        before=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes();assert digest(before)==read(INPUT/'current-inputs.json.gz')['manifestSHA256']
        rows=read(INPUT/'selection.json.gz')['rows'];contexts=read(INPUT/'context.json.gz')['rows'];proofs=[]
        for row in rows:
            proof=verify_files(row,next(c for c in contexts if c['uid']==row['uid']),LOCAL/row['uid'].split('/')[1])
            assert proof['passed'] and proof['reasons']==[] and proof['physicalAccepted'] is False and proof['installationApproved'] is False
            assert proof['mandatoryOriginalRuntimeUIDs']==[UID,PLATFORM] and proof['standaloneOriginalImportAccepted'] is False
            assert proof['currentBinding']['manifestSHA256']==digest(before) and proof['currentBinding']['bothNativeRunMembershipsVerified'] is True
            proofs.append(proof)
        assert len(proofs)==2 and {p['uid'] for p in proofs}=={UID,PLATFORM}
        save(DOC/'identities.json.gz',{'rows':proofs});save(DOC/'selection.json.gz',{'rows':rows});save(DOC/'context.json.gz',{'rows':contexts})
        tests=[sys.executable,'-m','unittest','test_man_hei_named_mandatory_original_platform_identity_20261010','test_man_hei_current_bound_mandatory_platform_identity_v2_20261010','-v']
        test=subprocess.run(tests,cwd=HERE,text=True,capture_output=True)
        save(DOC/'actual-counterexample-tests.json',dict(command=tests,exitCode=test.returncode,stdout=test.stdout,stderr=test.stderr,productionUnmockedOriginalContacts=True));assert test.returncode==0
        assert (ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==before and reservations.owns(lease)
        refs=[Path(__file__),HERE/'man_hei_named_mandatory_original_platform_identity_20261010.py',HERE/'test_man_hei_named_mandatory_original_platform_identity_20261010.py',HERE/'man_hei_current_bound_mandatory_platform_identity_v2_20261010.py',HERE/'test_man_hei_current_bound_mandatory_platform_identity_v2_20261010.py',HERE/'man_hei_dependent_platform_current_identity_20261010.py',HERE/'man_fuk_current_bound_envelope_identity_v3_20261010.py',INPUT/'result.json',INPUT.parent/'government-xl-man-hei-dependent-platform-current-proof-v2-20261010/result.json']+[p for p in LOCAL.rglob('*') if p.is_file()]
        upper=next(p for p in proofs if p['uid']==UID)
        result=module('manhei_current_identity_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-current-mandatory-man-hei-original-platform-identity-v1',refs,dict(uids=[UID,PLATFORM],identityAccepted=True,currentIdentityAccepted=True,physicalAccepted=False,manifestSHA256=digest(before),sourceIdentityPolicy=upper['policy'],mandatoryOriginalRuntimeUIDs=[UID,PLATFORM],standaloneOriginalImportAccepted=False,completeMissingFloorClaim=False,completeOriginalFaceCounts=upper['completeOriginalFaceCounts'],completeOriginalPartCounts=upper['completeOriginalPartCounts'],rawStandaloneCoverageReasonsRetained=upper['rawStandaloneUpperCoverageReasonsRetained'],sourceEvidenceInterpretationUsedAI=True,nextStep='Root complete coupled unchanged-original terrain/support/foreign/foundation/runtime checks. Preserve all99originalparts and actual retainedManOi. Both originals required at any eventual stage/install; no standalone identity import.',qualification='Current source-only mandatory assembly identity accepted, no physical/import/installation credit. True partial floor gaps remain, ordinary95%/10m numeric gates unchanged; independent platform namedManOi relation freshly recomputed, all current foreign actors retained.'))
        print(json.dumps({'jobId':result['jobId'],'identityPassed':True,'physicalAccepted':False,'manifestSHA256':digest(before)}),flush=True)
    finally:assert reservations.release(lease)['ok']

if __name__=='__main__':main()
