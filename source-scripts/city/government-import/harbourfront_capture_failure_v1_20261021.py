"""Retain the terminal duplicate-screenshot timeout and recorded recovery."""
from pathlib import Path
from run import ROOT,HERE,read,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-harbourfront-tower-original-installed-v4-20261021';BATCH='government-xl-harbourfront-capture-failure-v1-20261021'
assert not reservations.owns(read(HERE/'local'/OLD.name/'reservation.json'))
r=read(OLD/'1280/live-browser.json');assert any('page.screenshot: Timeout 60000ms'in e for e in r['errors']);assert read(OLD/'supervisor-recovery.json')['allPublicDestinationsRestored']
refs=[Path(__file__),HERE/'harbourfront_tower_live_install_v4_20261021.py',HERE/'harbourfront_live_browser_v3_20261021.mjs',*[p for p in OLD.rglob('*')if p.is_file()]]
module('capture_failure',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'duplicate-full-page-capture-timeout-after-canvas-export',refs,dict(uids=['landsd/118230:0'],failure='duplicate-page-screenshot-timeout',newlyInstalled=0,installationApproved=False,modelCorruption=False,recoveryRecorded=True,qualification='Desktop reached original and emitted both canvas PNGs, but duplicate page screenshot prevented final report. No complete desktop approval. Prior recovery receipt retained; subsequent publication state is separate. Next capture writes direct canvas PNG and keeps all acceptance assertions.'))
