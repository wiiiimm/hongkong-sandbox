"""Commit only the installed Forum original and its exact verification code."""
import argparse
import importlib.util
from pathlib import Path
from run import ROOT, HERE, read
UIDS={'landsd/319459:0'}

probe=argparse.ArgumentParser(add_help=False)
probe.add_argument('--source',required=True)
args,_=probe.parse_known_args()
source=ROOT/args.source
assert source.parent==ROOT/'docs/astra-city/government-import'
result=read(source/'result.json')
assert set(result['installedUids'])==UIDS and result['publication'] and result['passed']
spec=importlib.util.spec_from_file_location('forum_actual_install_commit',HERE/'xl-commit-installed.py')
coordinator=importlib.util.module_from_spec(spec);spec.loader.exec_module(coordinator)
original_call=coordinator.call
extra=[HERE/name for name in ['xl-forum-current-support-preflight.py',
    'xl-forum-current-support-result.py','xl-forum-current-support-install.py',
    'xl-commit-forum-installed.py']]
extra += [ROOT/'docs/astra-city/government-import'/name for name in [
    'government-xl-forum-compound-current-inputs-20261007',
    'government-xl-forum-source-support-20261006',
    'government-xl-forum-unobstructed-live-check-20261007']]
assert all(p.exists() for p in extra)
def scoped_call(command):
    if command[:3]==['git','add','--']:
        command=command+[str(p.relative_to(ROOT)) for p in extra]
    return original_call(command)
coordinator.call=scoped_call
coordinator.main()
