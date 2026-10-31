"""Commit only the installed exact Pak Shing pair and its actual verification code."""
import argparse
import importlib.util
from pathlib import Path
from run import ROOT, HERE, read
from pak_shing_compound_identity import UIDS

probe=argparse.ArgumentParser(add_help=False)
probe.add_argument('--source',required=True)
args,_=probe.parse_known_args()
source=ROOT/args.source
assert source.parent==ROOT/'docs/astra-city/government-import'
result=read(source/'result.json')
assert set(result['installedUids'])==UIDS and result['publication'] and result['passed']
spec=importlib.util.spec_from_file_location('pak_actual_install_commit',HERE/'xl-commit-installed.py')
coordinator=importlib.util.module_from_spec(spec);spec.loader.exec_module(coordinator)
original_call=coordinator.call
extra=[HERE/name for name in ['pak_shing_compound_identity.py','test_pak_shing_compound_identity.py',
    'xl-pak-shing-compound-support-recheck.py','xl-pak-shing-compound-support-install.py',
    'xl-commit-pak-shing-compound-installed.py']]
extra += [ROOT/'docs/astra-city/government-import'/name for name in [
    'government-xl-pak-shing-original-neighbour-20261007',
    'government-xl-pak-shing-neighbour-current-inputs-20261007',
    'government-xl-pak-shing-original-tower-support-20261007',
    'government-xl-pak-shing-podium-complete-current-recheck-20261007']]
assert all(p.exists() for p in extra)
def scoped_call(command):
    if command[:3]==['git','add','--']:
        command=command+[str(p.relative_to(ROOT)) for p in extra]
    return original_call(command)
coordinator.call=scoped_call
coordinator.main()
