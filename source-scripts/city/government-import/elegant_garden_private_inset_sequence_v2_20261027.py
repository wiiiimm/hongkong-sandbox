"""After the live root-terrain owner ends, run existing private inset checks.

Strictly diagnostic: no original model edits, public writes or guard changes.
"""
import argparse
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import process_identity

PREFIX = 'government-xl-elegant-garden-'
BATCH = PREFIX + 'private-inset-sequence-v2-20261027'
PLAN = PREFIX + 'inset-scope-v1-20261027'
CAPTURE = PREFIX + 'existing-ground-runtime-v2-20261027'
GROUND = PREFIX + 'podium-original-terrain-binding-v1-20261027'
INVENTORY = 'government-xl-after-ocean-four-current-inventory-v1-20261027'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--after-pid', type=int, required=True)
    a = p.parse_args()
    identity = process_identity(a.after_pid)
    assert identity and b'north_pair_remaining_mobile_v1_20261027.py' in identity[1]
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / BATCH, HERE / 'local' / BATCH
    assert not doc.exists() and not local.exists()
    _, pins = authenticate(base / PLAN)
    path = base / PLAN / 'summary.json'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    plan = read(path)
    assert plan['standaloneInsetEligible'] and not plan['coordinatedMembers']
    assert plan['coverNative'] == ['city/data/government-native-kwong-fung-original-v1-20261025.json']
    assert plan['touchingNativeUids'] == ['landsd/229834:0', 'landsd/337316:0', 'landsd/337318:0']
    local.mkdir(parents=True)
    save(local / 'predecessor.json', dict(pid=a.after_pid, startTicks=identity[0]))
    print('Waiting for exact mobile controller to finish; no root/model lease claimed.', flush=True)
    while process_identity(a.after_pid) == identity:
        time.sleep(30)
    terrain, scope, runtime, forms = [PREFIX + s + '-v1-20261027' for s in
                                     ['private-inset', 'private-inset-scope', 'private-inset-runtime', 'private-inset-forms']]
    steps = [
        (terrain, 'selected_original_local_inset_v9_20261024.py',
         ['--capture', CAPTURE, '--terrain-check', GROUND, '--uid', 'landsd/236170:0',
          '--companion', 'landsd/173532:0', '--companion', 'landsd/173768:0',
          '--cover-native', plan['coverNative'][0]]),
        (scope, 'selected_original_retained_patch_scope_v3_20261026.py', ['--inventory', INVENTORY, '--patch', terrain]),
        (runtime, 'selected_original_patch_runtime_v6_20261024.py', ['--patch', terrain, '--capture', CAPTURE]),
        (forms, 'selected_original_retained_patch_form_checks_v1_20261027.py', ['--scope', scope, '--inventory', INVENTORY, '--patch', terrain]),
    ]
    completed = []
    doc.mkdir()
    save(doc / 'commands.json', dict(steps=[dict(batch=b, script=s, args=t) for b, s, t in steps], resources=plan['resources']))
    for batch, script, tail in steps:
        # The exact complete prepared scene must still exist; no approval crosses
        # a changed manifest, source, terrain member or retained-model revision.
        for path, sha in pins.items():
            assert digest((ROOT / path).read_bytes()) == sha
        assert not (base / batch).exists()
        claim = reservations.claim('elegant-inset-phase-' + str(uuid.uuid4()),
                                   plan['resources'], batch=batch, ttl=3600)
        assert claim['ok'], 'Scope reserved by another owner; no takeover permitted'
        lease = claim['reservation']
        lease_path = local / (batch + '-lease.json')
        save(lease_path, json.loads(json.dumps(lease, default=str)))
        print('Starting ' + batch, flush=True)
        try:
            with (local / (batch + '.log')).open('w') as log:
                proc = subprocess.run([sys.executable, str(HERE / 'observed_reserved_runner_v1_20261027.py'),
                                       str(lease_path), sys.executable, str(HERE / script), '--batch', batch, *tail],
                                      cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        finally:
            if reservations.owns(lease):
                assert reservations.release(lease)['ok']
        status = dict(uids=plan['uids'], completed=completed, phase=batch,
                      exitCode=proc.returncode, installationApproved=False, publication=False)
        save(doc / 'progress.json', status)
        assert proc.returncode == 0, 'Keep failed output and inspect; never restart completed phases'
        receipt, _ = authenticate(base / batch)
        completed.append(batch)
        if batch == terrain:
            assert receipt['status'] == 'private-terrain-validator-passed', 'Private candidate held; no guard waiver'
            actual = read(base / terrain / 'scope.json')
            assert actual['cells'] == plan['cells'] and actual['bounds'] == plan['bounds']
        if batch == scope:
            actual = read(base / scope / 'scope.json')
            assert sorted(actual['touchingNativeUids']) == plan['touchingNativeUids'], 'Scope changed: reserve before more processing'
        print('Completed ' + batch, flush=True)
    summary = dict(uids=plan['uids'], completed=completed, sourceGeometryChanges=0,
                   installationApproved=False, physicalAcceptance=False, publication=False,
                   qualification='Existing bounded original-terrain inset, complete retained scope, runtime '
                   'and base-form diagnostics only. All raw failures remain; no source/physical/browser/publication approval.')
    save(doc / 'summary.json', summary)
    module('elegant_private_inset_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'private-original-terrain-inset-current-diagnostics',
        [Path(__file__), base / PLAN / 'result.json', *[base / b / 'result.json' for b in completed]], summary)


if __name__ == '__main__':
    main()
