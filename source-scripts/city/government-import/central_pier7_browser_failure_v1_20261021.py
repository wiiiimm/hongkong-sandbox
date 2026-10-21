"""Archive completed desktop evidence and failed mobile travel wait without approval."""
from pathlib import Path
from run import ROOT,HERE,read,save
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-pier7-browser-failure-v1-20261021';DOC=BASE/BATCH;old=BASE/'government-xl-central-pier7-staged-browser-v1-20261021';local=HERE/'local'/old.name
assert not DOC.exists();assert read(old/'command-1280.json')['exitCode']==0;assert read(old/'command-390.json')['exitCode']==1
assert read(old/'1280/staged-browser.json')['passed'];assert 'Timeout 90000ms exceeded' in (old/'browser-390.log').read_text()
refs=[Path(__file__),HERE/'central_pier7_staged_browser_v1_20261021.py',HERE/'tko_grandiose_synchronised_browser_v2_20261021.mjs'];refs.extend(p for d in [old,local] for p in d.rglob('*') if p.is_file() and p.name!='reservation.json')
summary=dict(uids=['landsd/285475:0'],desktopPassed=True,mobilePassed=False,failure='Mobile map-travel wait exceeded 90000ms before model active/render validation.',installationApproved=False,sourceGeometryChanges=0,qualification='Failed browser orchestration retained; not a corruption or permanent model hold. Old owned worker confirmed terminal and lease explicitly released before new mobile-only retry.')
save(DOC/'summary.json',summary);r=module('pier7_browser_failure_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'staged-browser-mobile-travel-timeout',refs,summary);print(r['jobId'],flush=True)
