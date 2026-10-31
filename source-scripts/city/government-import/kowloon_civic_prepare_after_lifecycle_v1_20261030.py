"""Continue CPU-only review binding and real publisher dry run after the live worker."""
import os
import subprocess
import sys
import time
from run import ROOT, HERE, read, digest
from china_ferry_current_foundations_v1_20261020 import authenticate

BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-kowloon-city-civic-five-after-fuying-'
LIFECYCLE = P + 'atomic-lifecycle-v1-20261030'
CONFIG = BASE / (P + 'install-config-v1-20261030.json')
STEPS = [('source-review', HERE / 'kowloon_civic_source_review_v1_20261030.py', []),
         ('qualified-stage', HERE / 'kowloon_civic_qualified_stage_v1_20261030.py', []),
         ('installer-preflight', HERE / 'kowloon_civic_live_install_v1_20261030.py', ['--prepare-only'])]


def main():
    files = [CONFIG, *[p for _, p, _ in STEPS],
             HERE / 'kowloon_civic_guarded_publish_v1_20261030.py',
             HERE / 'kowloon_civic_live_atomic_lifecycle_v1_20261030.mjs']
    pins = {p: digest(p.read_bytes()) for p in files}
    deadline = time.monotonic() + 2400
    print('Waiting for six-case private lifecycle; no duplicate worker or production writes.', flush=True)
    while not (BASE / LIFECYCLE / 'result.json').exists():
        assert time.monotonic() < deadline
        probe = subprocess.run(['pgrep', '-f', '[k]owloon_civic_browser_followthrough_v1_20261030.py'], capture_output=True)
        assert probe.returncode == 0, 'Follow-through stopped without a lifecycle receipt; inspect its exact failure.'
        time.sleep(5)
    receipt, _ = authenticate(BASE / LIFECYCLE)
    assert receipt['cases'] == 6 and receipt['installationApproved'] is False
    env = {**os.environ, 'ORIGINAL_INSTALL_CONFIG': str(CONFIG.relative_to(ROOT))}
    for name, script, args in STEPS:
        for path, sha in pins.items():
            assert digest(path.read_bytes()) == sha
        print('Starting ' + name, flush=True)
        with open('/tmp/astra-kowloon-civic-' + name + '-v1-20261030.log', 'w') as log:
            subprocess.run([sys.executable, str(script), *args], cwd=ROOT, env=env,
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        print('Completed ' + name, flush=True)
    print('Prepared real publisher and installer preflight. No model installed or public files written.', flush=True)


if __name__ == '__main__':
    main()
