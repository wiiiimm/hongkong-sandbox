"""Archive bounded source interpretation without geometry or installation approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-china-merchants-basement-layout-evidence-v1-20261015';DOC=BASE/BATCH
if __name__=='__main__':
 assert not(DOC/'result.json').exists()
 for r in read(DOC/'freeguider-retrieval.json'):assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 r=read(DOC/'retrieval.json');assert digest((DOC/'shun-tak-directory-20130904.jpg').read_bytes())==r['sha256']
 review=dict(uid='landsd/264206:0',sourceSHA256='0ff5adae4dae90e856af6fb6f40112a24198668ca9dfc66e9570b058739b50fb',imagesActuallyViewed=['basement-plan.jpg','ground-escalator.jpg','shun-tak-directory-20130904.jpg'],finding='Basement directory visibly labels basement units, three escalator symbols and loading/unloading area. Ground escalator photograph shows paired escalators with curved handrail ends. Original bodies6/8/9/10 are consistent in shape with escalator handrails, but the photo is G/F and cannot establish these exact source-body elevations or positions. Group4 ramp-like and group5 low wall/floor correspondence remains unproved.',sourceRoleApproved=False,placementApproved=False,permanentRejection=False,needsHumanDecision=False,remainingReason='Exact affected source-face roles and visible/collision impact of below-ground geometry unresolved',nextAction='Match original component plan positions and elevations to basement/entrance context; do not replay completed 1199-native/5312-form regression checks unless their pinned inputs change.',noBuildingGeometryEdits=True,noOptimisation=True)
 save(DOC/'review.json',review)
 paths=[Path(__file__),BASE/'government-xl-china-merchants-current-target-foundation-v1-20261015/result.json',BASE/'government-xl-china-merchants-unchanged-four-and-basic-v1-20261015/result.json',BASE/'government-xl-china-merchants-complete-body-context-v1-20261015/summary.json',BASE/'government-xl-china-merchants-complete-body-context-v1-20261015/failure-context-azimuth-35.png',BASE/'government-xl-china-merchants-buried-context-v1-20261015/failure-context-azimuth-215.png']
 module('china_basement_layout_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-basement-layout-source-interpretation-v1',paths,dict(uids=[review['uid']],review=review,fullAcceptance=False))
