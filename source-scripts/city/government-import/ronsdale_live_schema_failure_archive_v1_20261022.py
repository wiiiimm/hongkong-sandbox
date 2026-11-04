"""Archive the fully rolled-back live source-form adapter failure."""
from pathlib import Path
from run import ROOT,HERE,read,save,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ronsdale-live-schema-failure-v1-20261022';DOC=BASE/BATCH
OLD='government-xl-ronsdale-original-installed-v2-20261022'
def main():
 assert not DOC.exists();old=BASE/OLD;local=HERE/'local'/OLD;recovery=read(old/'failure-recovery.json');assert recovery['allPublicDestinationsRestored']and not recovery['rollbackErrors']and not recovery['derivedInstalledReviewHistoryRetained'];assert 'forms.find is not a function'in recovery['error'];assert not reservations.owns(read(local/'reservation.json'))
 pub=ROOT/'docs/astra-city/model-integration-20260909'/OLD;assert read(pub/'publication.json')['published'];assert not(old/'installed-acceptance.json').exists()and not(old/'result.json').exists()
 result=dict(uids=['landsd/233771:0','landsd/256898:0','landsd/256702:0'],producerExitCode=1,publicationAppliedThenRolledBack=True,allPublicDestinationsRestored=True,currentPointerRestored=True,newInstalledReviewHistory=False,installationApproved=False,newInstallations=0,failure='Browser helper expected array while qualified stage supplied the validator source-form dictionary.',correctedProducer='source-scripts/city/government-import/ronsdale_original_live_install_v3_20261022.py',correction='Normalise both existing source-form schemas. --prepare-only invokes the actual browser form adapter and proves the normalized prepared forms exactly equal staged browser-tested buildings before apply.')
 save(DOC/'failure.json',result);refs=[Path(__file__),HERE/'ronsdale_original_live_install_v2_20261022.py',HERE/'ronsdale_guarded_publish_v2_20261022.py',HERE/'ronsdale_three_staged_browser_v2_20261022.mjs'];refs.extend(p for folder in [old,pub]for p in folder.rglob('*')if p.is_file());module('ronsdale_live_schema_failure',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'rolled-back-live-source-form-adapter-failure-archive',refs,result)
if __name__=='__main__':main()
