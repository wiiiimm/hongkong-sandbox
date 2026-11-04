"""Continue private checks after the already-running preview; never restart it."""
import os
import subprocess
import sys
import time
from pathlib import Path
from run import ROOT, HERE, digest, read
from china_ferry_current_foundations_v1_20261020 import authenticate

BASE = ROOT / 'docs/astra-city/government-import'
PREFIX = 'government-xl-kowloon-city-civic-five-after-fuying-'
PRIOR = PREFIX + 'unapproved-atomic-private-browser-v1-20261030'
NEXT = PREFIX + 'unapproved-atomic-private-browser-v2-20261030'
CONFIG = BASE / (PREFIX + 'private-browser-config-v2-20261030.json')
PREVIEW = HERE / 'kowloon_civic_unapproved_atomic_browser_v2_20261030.py'
LIFECYCLE = HERE / 'kowloon_civic_atomic_lifecycle_v1_20261030.py'
PINNED = [CONFIG, PREVIEW, LIFECYCLE, HERE / 'kowloon_civic_atomic_lifecycle_browser_v1_20261030.mjs']


def main():
    pins = {p: digest(p.read_bytes()) for p in PINNED}
    deadline = time.monotonic() + 900
    print('Waiting for existing V1 receipt; no restart or source edits.', flush=True)
    while not (BASE / PRIOR / 'result.json').exists():
        assert time.monotonic() < deadline, 'Existing preview did not complete; inspect its original worker.'
        os.kill(199008, 0)  # Exact already-observed parent; a failed predecessor stops this sequence.
        time.sleep(5)
    receipt, _ = authenticate(BASE / PRIOR)
    assert receipt['previewOnly'] and not receipt['installationApproved']
    # Completion is written before the predecessor closes its leased server.
    while Path('/proc/199008/cmdline').exists() and 'kowloon_civic_unapproved_atomic_browser_v1_20261030.py' in Path('/proc/199008/cmdline').read_text():
        assert time.monotonic() < deadline
        time.sleep(1)
    for path, sha in pins.items():
        assert digest(path.read_bytes()) == sha
    assert not (BASE / NEXT).exists()
    env = {**os.environ, 'ORIGINAL_PREVIEW_CONFIG': str(CONFIG.relative_to(ROOT))}
    with open('/tmp/astra-kowloon-civic-private-browser-v2-20261030.log', 'w') as log:
        subprocess.run([sys.executable, str(PREVIEW)], cwd=ROOT, env=env,
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    print('Opposite-side wider private views complete; starting exact atomic lifecycle.', flush=True)
    for path, sha in pins.items():
        assert digest(path.read_bytes()) == sha
    with open('/tmp/astra-kowloon-civic-atomic-lifecycle-v1-20261030.log', 'w') as log:
        subprocess.run([sys.executable, str(LIFECYCLE)], cwd=ROOT,
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    print('Private views and six lifecycle cases complete. No installation/publication.', flush=True)


if __name__ == '__main__':
    main()
