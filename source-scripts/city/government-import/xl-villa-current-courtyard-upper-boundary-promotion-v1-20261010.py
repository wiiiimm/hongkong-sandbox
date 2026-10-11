"""Fence the exact named current identity; never approve physical installation."""
import json
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from villa_current_bound_courtyard_upper_boundary_identity_20261010 import DOC as INPUT,verify_files,module
from villa_original_courtyard_upper_boundary_identity_20261010 import UID,FOREIGN

BATCH='government-xl-villa-current-courtyard-upper-boundary-promotion-v1-20261010'
DOC=INPUT.parent/BATCH
LOCAL=HERE/'local'/BATCH


def main():
    assert not DOC.exists()
    claim=reservations.claim('villa-courtyard-current-promotion-'+str(uuid.uuid4()),
        ['building:'+UID,'building:'+FOREIGN],batch=BATCH,ttl=3600)
    assert claim['ok'],claim
    try:
        before=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()
        assert digest(before)==read(INPUT/'current-inputs.json.gz')['manifestSHA256']
        row=read(INPUT/'selection.json.gz')['rows'][0]
        context=read(INPUT/'context.json.gz')['rows'][0]
        proof=verify_files(row,context,LOCAL)
        assert proof['passed'] and proof['reasons']==[]
        assert not proof['physicalAccepted'] and not proof['installationApproved']
        assert not proof['surveyedCanopySeparationClaim'] and not proof['foreignCollisionExemption']
        save(DOC/'identity.json',proof)
        save(DOC/'selection.json.gz',dict(rows=[row]))
        save(DOC/'context.json.gz',dict(rows=[context]))
        command=[sys.executable,'-m','unittest','test_villa_original_courtyard_upper_boundary_identity_20261010',
            'test_villa_current_bound_courtyard_upper_boundary_identity_20261010','-v']
        test=subprocess.run(command,cwd=HERE,text=True,capture_output=True)
        save(DOC/'actual-counterexample-tests.json',dict(command=command,exitCode=test.returncode,
            stdout=test.stdout,stderr=test.stderr,unmockedProductionCurrentNativeAndNeonReplay=True))
        assert test.returncode==0
        assert (ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==before
        refs=[Path(__file__),INPUT/'result.json',HERE/'villa_original_courtyard_upper_boundary_identity_20261010.py',
            HERE/'villa_current_bound_courtyard_upper_boundary_identity_20261010.py',
            HERE/'villa_current_native_inventory_20261010.py',
            HERE/'test_villa_original_courtyard_upper_boundary_identity_20261010.py',
            HERE/'test_villa_current_bound_courtyard_upper_boundary_identity_20261010.py',
            HERE/'routed_original_cell_identity.py',HERE/'exact_original_georef_cell_identity_20261009.py']
        result=module('villa_named_current_promotion_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            BATCH,'named-complete-original-villa-courtyard-boundary-current-identity-v1',refs,
            dict(uids=[UID,FOREIGN],identityAccepted=True,currentIdentityAccepted=True,physicalAccepted=False,
                manifestSHA256=digest(before),sourceIdentityPolicy=proof['policy'],completeOriginalFaces=16669,
                completeOriginalParts=58,namedOriginalUpperBoundaryFaces=16,foreignOriginalUnavailable=True,
                foreignSurveyedHeightUnknown=True,foreignPhysicalExemptions=0,sourceGeometryChanges=0,
                sourceEvidenceInterpretationUsedAI=True,
                currentHeldReason='independent-complete-source-terrain-support-foreign-runtime-checks-required',
                nextStep='Run full unchanged-original physical/current foreign foundations/support/terrain/runtime checks. The distinct unknown-survey-height canopy remains an actual estimated basic actor; no source suppression or physics waiver.',
                qualification='Reviewed exact named source/current/provider identity-only route. Both raw overlap reasons/real strips retained. No surveyed canopy clearance, common ownership, function, support, foreign omission or tolerance claim. Zero installation credit.'))
        print(json.dumps(dict(jobId=result['jobId'],identityPassed=True,physicalAccepted=False,manifestSHA256=digest(before))),flush=True)
    finally:
        assert reservations.release(claim['reservation'])['ok']


if __name__=='__main__':main()
