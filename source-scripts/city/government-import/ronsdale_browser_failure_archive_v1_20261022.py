"""Preserve terminal browser/test and image-review failures without acceptance credit."""
from pathlib import Path
from run import ROOT,HERE,read,save,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ronsdale-browser-failure-archive-v1-20261022';DOC=BASE/BATCH
OLD='government-xl-ronsdale-three-staged-browser-v1-20261022'
def main():
 assert not DOC.exists();old=BASE/OLD;local=HERE/'local'/OLD;assert not(old/'result.json').exists();assert not reservations.owns(read(local/'reservation.json'))
 desktop=read(old/'1280/staged-browser.json');mobile=read(old/'390/staged-browser.json');assert desktop['passed']and not desktop['errors'] and mobile['errors'];assert read(old/'command-390.json')['exitCode']!=0
 rejected=HERE/'local/government-xl-ronsdale-root-image-inspection-20261022/desktop-v1-rejected.json';review=read(rejected);assert review['visualAcceptance']is False and len(review['imagesActuallyViewed'])==6
 refs=[Path(__file__),HERE/'ronsdale_three_staged_browser_v1_20261022.py',HERE/'ronsdale_three_staged_browser_v1_20261022.mjs',rejected]
 refs.extend(p for p in old.rglob('*')if p.is_file());refs.extend(p for p in local.rglob('*')if p.is_file()and p.name!='reservation.json')
 result=dict(uids=['landsd/256898:0','landsd/256702:0','landsd/233771:0'],producerExitCode=1,desktopNumericChecksPassed=True,mobileChecksPassed=False,visualAcceptance=False,sourceGeometryChanges=0,newInstallations=0,installationApproved=False,reason='Desktop exports obscured by foreground ordinary towers; mobile retry tested dependent tower before recovering deliberately blocked source podium.',correctedProducer='source-scripts/city/government-import/ronsdale_three_staged_browser_v2_20261022.py',correction='Unobstructed south-side camera directions and topological dependency-first failure/retry iteration; all source, frame, visibility, pick/collision, recovery and timing assertions retained.')
 save(DOC/'failure.json',result);module('ronsdale_failed_browser_archive',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'terminal-browser-and-image-failure-evidence-archive',refs,result)
if __name__=='__main__':main()
