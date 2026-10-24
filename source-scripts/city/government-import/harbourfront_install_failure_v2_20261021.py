"""Preserve recovered startup timeout without source rejection."""
from pathlib import Path
from run import ROOT,HERE,read,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-harbourfront-tower-original-installed-v2-20261021';BATCH='government-xl-harbourfront-install-failure-v2-20261021'
assert not reservations.owns(read(HERE/'local'/OLD.name/'reservation.json'))
h=read(OLD/'historical-input-context.json')
for q in h['mutableCurrentByteSnapshots']:assert digest((ROOT/q['originalPath']).read_bytes())==q['originalSHA256']
assert read(OLD/'supervisor-recovery.json')['allPublicDestinationsRestored'];report=read(OLD/'390/live-browser.json');assert report['errors']==['page.waitForFunction: Timeout 120000ms exceeded.'];assert not report['views']
refs=[Path(__file__),HERE/'harbourfront_tower_live_install_v2_20261021.py',HERE/'recover_interrupted_publication_20261021.py',*[p for p in OLD.rglob('*')if p.is_file()]]
module('hf_failure',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'recovered-live-browser-startup-timeout',refs,dict(uids=['landsd/118230:0'],failure='mobile-map-startup-timeout-before-model-selection',timeoutMs=120000,newlyInstalled=0,installationApproved=False,modelCorruption=False,allPublicDestinationsRestored=True,currentSnapshot=h['preInstallSnapshot'],qualification='Map startup observation timed out on memory-pressured host. No source check failed; no source rejection or installed credit. Retry may allow more startup time while retaining acceptance checks.'))
