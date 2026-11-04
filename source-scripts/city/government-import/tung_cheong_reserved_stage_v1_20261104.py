"""Run only Tung Cheong's exact reviewed original-model dry run under its lease."""
import os
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved

BASE=ROOT/'docs/astra-city/government-import'
PLAN=BASE/'government-xl-tung-cheong-two-original-installation-plan-v1-20261104'
REVIEW='government-xl-tung-cheong-atomic-source-review-v1-20261104'
BATCH='government-xl-tung-cheong-two-original-atomic-retained-qualified-stage-v1-20261104'
TOOL=HERE/'tung_cheong_atomic_retained_qualified_stage_v1_20261104.py'

def main():
    assert not(BASE/BATCH).exists()
    receipt,pins=authenticate(BASE/REVIEW);p=BASE/REVIEW/'ROOT-SOURCE-REVIEW.json'
    assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
    review=read(p);assert review['compoundIdentityAccepted']and review['visualAcceptance']and review['installationApproved']is False
    resources=sorted(set(review['leaseResources'])|{'immutable-source-proof:'+BATCH})
    lp=HERE/'local'/(BATCH+'-control')/'reservation.json'
    if '--owned'not in sys.argv:
        assert not lp.parent.exists()
        c=reservations.claim('tung-cheong-qualified-stage-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600)
        assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    command=[sys.executable,str(TOOL)];before=digest(TOOL.read_bytes())
    save(PLAN/'stage-command.json',dict(command=command,config=str((PLAN/'config.json').relative_to(ROOT)),producerSHA256=before,reviewJobId=receipt['jobId'],resources=resources,publication=False))
    subprocess.run(command,cwd=ROOT,check=True,env={**os.environ,'ORIGINAL_INSTALL_CONFIG':str((PLAN/'config.json').relative_to(ROOT))})
    assert digest(TOOL.read_bytes())==before and reservations.owns(lease)
    completed,_=authenticate(BASE/BATCH);assert completed['qualifiedForLiveVerification']and completed['publication']is False

if __name__=='__main__':main()
