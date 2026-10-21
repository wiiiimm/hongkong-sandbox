"""Preserve the instrumented cold-mobile UI timeout without source-failure credit."""
from pathlib import Path
from run import ROOT,HERE,read
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';n='government-xl-illumination-mobile-diagnostic-v1-20261021';folder=BASE/n
assert read(folder/'command-390.json')['exitCode']==1
report=read(folder/'390/staged-browser.json');assert not report.get('passed') and any('locator.click' in e for e in report['errors'])
refs=[Path(__file__),HERE/'illumination_mobile_diagnostic_v1_20261021.py',HERE/'illumination_mobile_diagnostic_v1_20261021.mjs']
refs.extend(p for d in [folder,HERE/'local'/n]for p in d.rglob('*')if p.is_file()and p.name!='reservation.json')
module('illumination_mobile_failure_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze('government-xl-illumination-mobile-failure-record-v1-20261021','cold-map-retry-ui-timeout',refs,dict(uids=['landsd/255531:0','landsd/258737:0'],installationApproved=False,sourceCorrupt=False,coldMobileRecoveryPassed=False,reason='Retry button locator resolved but click timed out30seconds. Logged timer delays during base-map travel/loading; no source-corruption conclusion. Subsequent base-ready run must retain cold-load failure and cannot claim improved cold performance.'))
