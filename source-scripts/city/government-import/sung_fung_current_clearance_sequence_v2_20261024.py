"""Complete bounded current ground diagnostics for the three original sources."""
from pathlib import Path
import subprocess
import sys
from run import ROOT, HERE, save
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base = ROOT / 'docs/astra-city/government-import'
    batch = 'government-xl-next-repairs-sung-fung-current-clearance-sequence-v2-20261024'
    out = base / batch
    assert not out.exists()
    runtime = 'government-xl-next-repairs-sung-fung-three-two-insets-runtime-v1-20261024'
    attributes = 'government-xl-next-repairs-sung-fung-three-original-attributes-v1-20261024'
    for name in [runtime, attributes]:
        authenticate(base / name)
    out.mkdir()
    refs = [Path(__file__), base / runtime / 'result.json', base / attributes / 'result.json']
    completed = []
    steps = []
    for uid in ['landsd/79098:0', 'landsd/45779:0', 'landsd/47160:0']:
        token = uid.split('/')[1].split(':')[0]
        low = 'government-xl-next-repairs-sung-family-' + token + '-current-low-faces-v2-20261024'
        cap = 'government-xl-next-repairs-sung-family-' + token + '-current-cap-paths-v2-20261024'
        common = ['--runtime', runtime, '--attributes', attributes, '--uid', uid]
        steps.append((low, 'selected_original_four_world_low_face_context_v1_20261024.py', common))
        steps.append((cap, 'selected_original_complete_ground_cap_paths_v2_20261024.py', common + ['--low-faces', low]))
    failed = None
    for name, script, args in steps:
        assert not (base / name).exists()
        logpath = out / (name + '.log')
        with logpath.open('w') as log:
            code = subprocess.run([sys.executable, str(HERE / script), '--batch', name, *args], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT).returncode
        refs.extend([HERE / script, logpath])
        if code:
            failed = dict(batch=name, exitCode=code)
            break
        receipt, _ = authenticate(base / name)
        refs.append(base / name / 'result.json')
        completed.append(dict(batch=name, jobId=receipt['jobId']))
        print(completed[-1], flush=True)
    result = dict(uids=['landsd/79098:0', 'landsd/45779:0', 'landsd/47160:0'], completed=completed, failed=failed, status='complete' if failed is None else 'script-investigation', installationApproved=False, publication=False, sourceGeometryChanges=0, aiGeometryModelling=False, qualification='Exact complete current drawn-ground and original cap-path diagnostics only. Raw burial/support negatives retained. No current terrain validation, source-role or publication approval transferred.')
    save(out / 'summary.json', result)
    module('sung_current_clearance_sequence_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch, 'three-original-current-ground-clearance-sequence', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
