"""Archive failed mobile observation and successful desktop evidence, without approval."""
from pathlib import Path
from run import ROOT,HERE,read
from primrose_compound_foundation_v2_20261015 import module
from china_ferry_current_foundations_v1_20261020 import authenticate
BASE=ROOT/'docs/astra-city/government-import';n='government-xl-illumination-staged-browser-v1-20261021';folder=BASE/n
assert read(folder/'command-1280.json')['exitCode']==0 and read(folder/'command-390.json')['exitCode']==1
assert read(folder/'1280/staged-browser.json')['passed'] and not read(folder/'390/staged-browser.json').get('passed')
refs=[Path(__file__),HERE/'illumination_staged_browser_v1_20261021.py',HERE/'parkview_retained_atomic_capture_v2_20261021.mjs']
for name in ['government-xl-illumination-inset-runtime-v2-20261021','government-xl-illumination-local-inset-v2-20261021']:
 _,pins=authenticate(BASE/name);refs.extend([BASE/name/'result.json',*[ROOT/p for p in pins]])
refs.extend(p for d in [folder,HERE/'local'/n]for p in d.rglob('*')if p.is_file()and p.name!='reservation.json')
module('illumination_browser_failure_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze('government-xl-illumination-browser-failure-record-v1-20261021','desktop-pass-mobile-retry-activation-timeout',list(dict.fromkeys(refs)),dict(uids=['landsd/255531:0','landsd/258737:0'],desktopPassed=True,mobilePassed=False,sourceCorrupt=False,installationApproved=False,reason='Mobile podium retry fetched bytes; remained pending and not active at unchanged60second deadline. Cause unresolved. Full failure and desktop results retained.'))
