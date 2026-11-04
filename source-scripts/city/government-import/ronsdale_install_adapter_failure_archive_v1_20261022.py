"""Archive the first installer adapter failure, which stopped before live mutation."""
from pathlib import Path
from run import ROOT,HERE,read,save,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ronsdale-install-adapter-failure-v1-20261022';DOC=BASE/BATCH
OLD='government-xl-ronsdale-original-installed-v1-20261022'
def main():
 assert not DOC.exists();old=BASE/OLD;local=HERE/'local'/OLD;assert not(old/'result.json').exists()and not reservations.owns(read(local/'reservation.json'));command=read(old/'command-000.json');assert command['exitCode']==0 and '--apply'not in command['command'];pub=ROOT/'docs/astra-city/model-integration-20260909'/OLD/'publication-plan.json';assert read(pub)['published']is False
 assert not(old/'installed-acceptance.json').exists();models=read(HERE/'accepted/government-xl-ronsdale-qualified-stage-v1-20261022/catalogue.json')['models'];assert any('label'not in m for m in models)
 result=dict(uids=[m['uid']for m in models],producerExitCode=1,failure='Optional catalogue label accessed as required field before source inventory seed or publisher apply',publicationApplied=False,preRetryLiveStateUnchangedVerified=True,leaseReleased=True,installationApproved=False,newInstallations=0,correctedProducer='source-scripts/city/government-import/ronsdale_original_live_install_v2_20261022.py',correction='Shared inventory_part adapter uses optional label, existing source name or UID fallback; the same adapter is exercised in --prepare-only and installation.')
 save(DOC/'failure.json',result);refs=[Path(__file__),HERE/'ronsdale_original_live_install_v1_20261022.py',HERE/'ronsdale_guarded_publish_v1_20261022.py',pub];refs.extend(p for p in old.rglob('*')if p.is_file());module('ronsdale_installer_failure_archive',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'pre-publication-installer-adapter-failure-archive',refs,result)
if __name__=='__main__':main()
