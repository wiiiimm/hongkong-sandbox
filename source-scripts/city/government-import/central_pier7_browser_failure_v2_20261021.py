"""Archive completed desktop evidence and failed mobile travel wait without approval."""
from pathlib import Path
from run import ROOT,HERE,read,save
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-pier7-browser-failure-v2-20261021';DOC=BASE/BATCH;old=BASE/'government-xl-central-pier7-staged-browser-v2-20261021';local=HERE/'local'/old.name
assert not DOC.exists();assert read(old/'command-390.json')['exitCode']==1
assert 'Timeout 120000ms exceeded' in (old/'browser-390.log').read_text()
refs=[Path(__file__),HERE/'central_pier7_staged_browser_v2_20261021.py',HERE/'tko_grandiose_synchronised_browser_v2_20261021.mjs'];refs.extend(p for d in [old,local] for p in d.rglob('*') if p.is_file() and p.name!='reservation.json')
summary=dict(uids=['landsd/285475:0'],desktopRun=False,mobilePassed=False,failure='Mobile map initialisation exceeded 120000ms before model selection. Host memory contention observed separately; no model rejection.',installationApproved=False,sourceGeometryChanges=0,qualification='Failed browser orchestration retained; not a corruption or permanent model hold. Retry exited1 with lease release reported; no further retry while full native baseline is using memory.')
save(DOC/'summary.json',summary);r=module('pier7_browser_failure_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'staged-browser-mobile-travel-timeout',refs,summary);print(r['jobId'],flush=True)
