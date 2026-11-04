"""Current original-pair ground capture and complete four-stream low-face checks."""
import sys
import uuid
import subprocess
from pathlib import Path
from run import ROOT, HERE, read, save, reservations
from observed_reserved_runner_v4_20261103 import execute_reserved

BATCH = 'government-xl-silvercord-lippo-complete-floor-low-faces-v1-20261103'
LOCAL = HERE / 'local' / BATCH
BASE = ROOT / 'docs/astra-city/government-import'
UIDS = ['landsd/233997:0', 'landsd/231645:0']
SELECTION = BATCH + '-selection'
RUNTIME = 'government-xl-silvercord-lippo-complete-floor-runtime-v2-20261103'
ATTRIBUTES = 'government-xl-silvercord-lippo-original-attributes-v1-20261101'


def owned():
    lease = read(LOCAL / 'reservation.json'); assert reservations.owns(lease)
    prior = BASE / 'government-xl-silvercord-lippo-reviewed-identity-replay-recovered-v1-20261103/result.json'
    assert read(prior)['bothCurrentIdentitiesReplayed'] and not read(prior)['installationApproved']
    commands = []
    for uid in UIDS:
        commands.append([sys.executable, str(HERE/'selected_original_four_world_low_face_context_v3_20261031.py'),
                         '--batch', BATCH+'-'+uid.split('/')[1].replace(':','-'),
                         '--runtime', RUNTIME, '--attributes', ATTRIBUTES, '--uid', uid])
    outcomes = []
    for index, command in enumerate(commands):
        assert reservations.owns(lease)
        path = LOCAL / ('phase-' + str(index) + '.log')
        with path.open('w') as log:
            result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=7200)
        outcomes.append(dict(command=command, exitCode=result.returncode, log=str(path.relative_to(ROOT))))
        save(LOCAL / 'progress.json', dict(uids=UIDS, rows=outcomes, installationApproved=False))
        assert result.returncode == 0, 'Preserve exact failed phase; no source-corruption inference'
        assert reservations.owns(lease)
        print(dict(phase=index, passed=True), flush=True)
    save(LOCAL / 'completed.json', dict(uids=UIDS, rows=outcomes, installationApproved=False,
                                       next='Preserve every raw buried wall/downward-face measurement and established policy result; current source-role, exact native support migration, terrain admission, browser and publication remain separate.'))


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists()
        claim = reservations.claim('silvercord-lippo-current-floor-' + str(uuid.uuid4()),
                                   ['building:' + u for u in UIDS] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok']
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
