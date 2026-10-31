"""Retain a terminal lease-renewal browser failure without model-failure credit."""
from pathlib import Path
from run import ROOT,HERE,read,save,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-harbourfront-browser-failure-v1-20261021';DOC=BASE/BATCH;old=BASE/'government-xl-harbourfront-tower-staged-browser-v1-20261021';local=HERE/'local'/old.name
assert not DOC.exists();log=Path('/tmp/harbourfront-staged-browser-v1-20261021.log').read_text();assert 'lease-lost-or-renewal-failed'in log and '"released": true'in log;assert not reservations.owns(read(local/'reservation.json'))
DOC.mkdir(parents=True);(DOC/'terminal-worker.log').write_text(log)
refs=[Path(__file__),HERE/'harbourfront_tower_staged_browser_v1_20261021.py',HERE/'tko_grandiose_synchronised_browser_v2_20261021.mjs'];refs.extend(p for d in [old,local] for p in d.rglob('*')if p.is_file()and p.name!='reservation.json')
summary=dict(uids=['landsd/118230:0'],failure='lease-lost-or-renewal-failed',terminalExitCode=2,oldLeaseOwned=False,desktopPassed=False,mobilePassed=False,installationApproved=False,modelCorruption=False,qualification='Owned browser supervisor stopped on lease renewal failure; no visual acceptance. Old owned processes were confirmed absent. Retry must use the new hotel-preserving terrain, with a fresh lease.')
save(DOC/'summary.json',summary);r=module('harbourfront_failed_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'terminal-browser-lease-renewal-failure',refs,summary);print(r['jobId'],flush=True)
