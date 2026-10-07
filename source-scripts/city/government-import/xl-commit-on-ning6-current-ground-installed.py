"""Commit exact On Ning Block 6 unchanged-ground installation and its complete checks."""
import argparse
import importlib.util
from run import ROOT, HERE, read

probe = argparse.ArgumentParser(add_help=False)
probe.add_argument('--source', required=True)
args, _ = probe.parse_known_args()
source = ROOT / args.source
assert source.parent == ROOT / 'docs/astra-city/government-import'
result = read(source / 'result.json')
assert len(result['installedUids']) == 1 and set(result['installedUids']) == {'landsd/34249:0'}
assert result['publication'] and result['passed']
spec = importlib.util.spec_from_file_location('on_ning_verified_commit', HERE / 'xl-commit-installed.py')
coordinator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(coordinator)
original_call = coordinator.call
extra = [HERE / name for name in ['xl-on-ning6-current-ground-preflight.py',
    'xl-on-ning6-current-ground-result.py', 'xl-on-ning6-current-ground-install.py',
    'xl-commit-on-ning6-current-ground-installed.py']]
assert all(p.exists() for p in extra)


def scoped_call(command):
    if command[:3] == ['git', 'add', '--']:
        command = command + [str(p.relative_to(ROOT)) for p in extra]
    return original_call(command)


coordinator.call = scoped_call
coordinator.main()
