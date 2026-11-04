"""Run unapproved original scene checks sequentially; never install or optimise.

Each stage saves its existing Neon evidence independently. The local state file
names the live child PID; observation timeouts are not permission to restart it.
"""
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import re
import subprocess
import sys
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module



def needs_native_finite_contacts(scope):
    """Closed complete bounds touching at any axis require the exact scanner."""
    assert scope['rows']
    for row in scope['rows']:
        lo, hi = np.asarray(row['completeSourceFourWorldBounds'], dtype=float)
        assert lo.shape == hi.shape == (3,) and np.isfinite([lo, hi]).all() and np.all(lo <= hi)
        for native in row['nearbyNativeActors']:
            points = np.asarray(native['completeFourWorldBounds'], dtype=float).reshape(-1, 3)
            assert len(points) >= 2 and np.isfinite(points).all()
            gaps = np.maximum(points.min(0) - hi, lo - points.max(0))
            if not np.any(gaps > 0):
                return True
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['prefix', 'date', 'selection', 'inventory']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--uid', action='append', required=True)
    args = parser.parse_args()
    assert re.fullmatch(r'government-xl-[a-z0-9-]+', args.prefix)
    assert re.fullmatch(r'[0-9]{8}', args.date)
    assert 0 < len(args.uid) == len(set(args.uid)) <= 40
    base = ROOT / 'docs/astra-city/government-import'
    receipt, selection_pins = authenticate(base / args.selection)
    selection_path = base / args.selection / 'selection.json.gz'
    assert digest(selection_path.read_bytes()) == selection_pins[str(selection_path.relative_to(ROOT))]
    selection = read(selection_path)
    assert {r['uid'] for r in selection['rows']} == set(args.uid)
    assert all(not r['candidate']['entry'].get(key) for r in selection['rows'] for key in ['publicationApproved', 'placementReviewed', 'identityReviewApproved', 'sourceIdentityReviewed'])
    _, inventory_pins = authenticate(base / args.inventory)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_sha = digest(manifest.read_bytes())
    assert manifest_sha == selection['manifestSHA256'] == inventory_pins[str(manifest.relative_to(ROOT))]
    batch = lambda stage: args.prefix + '-' + stage + '-v1-' + args.date
    names = {stage: batch(stage) for stage in ['ground', 'attributes', 'identity', 'scope', 'native-contacts', 'foreign']}
    sequence = batch('scene-check-sequence')
    local = HERE / 'local' / sequence
    assert not local.exists() and not (base / sequence).exists()
    assert all(not (base / name).exists() for name in names.values()), 'Inspect existing workers/receipts; never restart a partial sequence blindly'
    uid_args = [value for uid in args.uid for value in ['--uid', uid]]
    steps = [
        ('ground', 'selected_original_current_capture_v3.py', ['--capture', args.selection, *uid_args]),
        ('attributes', 'selected_original_render_attributes_v1.py', ['--capture', names['ground']]),
        ('identity', 'selected_original_identity_v3.py', ['--capture', names['ground']]),
        ('scope', 'selected_original_model_only_scope_v1_20261023.py', ['--runtime', names['ground'], '--attributes', names['attributes'], '--inventory', args.inventory]),
        ('native-contacts', 'selected_original_overlapping_native_contacts_v3_20261024.py', ['--scope', names['scope'], '--runtime', names['ground'], '--attributes', names['attributes'], '--inventory', args.inventory]),
        ('foreign', 'selected_original_model_only_foreign_contacts_v3_20261024.py', ['--scope', names['scope'], '--runtime', names['ground'], '--attributes', names['attributes'], '--native-contacts', names['native-contacts']]),
    ]
    local.mkdir(parents=True)
    state_path = local / 'state.json'
    state = dict(parentPID=os.getpid(), status='running', currentStage=None, childPID=None, completed=[], skipped=[], uids=args.uid, manifestSHA256=manifest_sha)
    refs = [Path(__file__), base / args.selection / 'result.json', selection_path, base / args.inventory / 'result.json', manifest]
    for stage, producer, extra in steps:
        assert digest(manifest.read_bytes()) == manifest_sha
        if stage == 'native-contacts':
            scope_receipt, scope_pins = authenticate(base / names['scope'])
            scope_path = base / names['scope'] / 'summary.json'
            assert digest(scope_path.read_bytes()) == scope_pins[str(scope_path.relative_to(ROOT))]
            scope = read(scope_path)
            assert scope['currentManifestSHA256'] == manifest_sha and set(scope['uids']) == set(args.uid)
            assert scope['terrainEdits'] is False and scope['installationApproved'] is False
            if not needs_native_finite_contacts(scope):
                state['skipped'].append(dict(stage=stage, reason='All complete nominated native bounds strictly disjoint, or no native nominations', scopeJobId=scope_receipt['jobId'], scopeSHA256=digest(scope_path.read_bytes())))
                state.update(currentStage=None, childPID=None)
                save(state_path, state)
                refs.append(scope_path)
                print(state['skipped'][-1], flush=True)
                continue
        if stage == 'foreign' and state['skipped']:
            assert extra[-2:] == ['--native-contacts', names['native-contacts']]
            extra = extra[:-2]

        command = [sys.executable, str(HERE / producer), '--batch', names[stage], *extra]
        with (local / (stage + '.log')).open('w') as log:
            child = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            state.update(currentStage=stage, childPID=child.pid, observedUTC=datetime.now(timezone.utc).isoformat(), command=command)
            save(state_path, state)
            print(dict(stage=stage, childPID=child.pid), flush=True)
            code = child.wait()
        state.update(childPID=None, exitCode=code)
        if code:
            state['status'] = 'failed'
            save(state_path, state)
            raise RuntimeError(f'{stage} exited {code}; inspect its log and any completed evidence before resuming')
        result, _ = authenticate(base / names[stage])
        state['completed'].append(dict(stage=stage, batch=names[stage], jobId=result['jobId']))
        save(state_path, state)
        refs.extend([HERE / producer, base / names[stage] / 'result.json'])
        print(dict(stage=stage, complete=True, jobId=result['jobId']), flush=True)
    assert digest(manifest.read_bytes()) == manifest_sha
    state.update(status='complete', currentStage=None)
    save(state_path, state)
    result = dict(uids=args.uid, completed=state['completed'], skipped=state['skipped'], currentManifestSHA256=manifest_sha, currentMapStartEndVerified=True, sourceGeometryChanges=0, sourcePoseChanges=0, installationApproved=False, publication=False, optimisationPerformed=False, qualification='Existing unapproved original-source checks only. Every executed phase has an authenticated completed receipt, including raw failed identity/physical diagnostics. Native finite scans are omitted only when the completed current scope proves no touching native bounds; the existing foreign checker independently preserves strict-bound separation and all BASIC checks. Completion of this driver is not source acceptance or installation credit. No migration, inventory reset, optimisation work or model editing is performed.')
    save(base / sequence / 'summary.json', result)
    refs.append(state_path)
    module('original_scene_sequence_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(sequence, 'unapproved-original-scene-check-sequence', refs, result)


if __name__ == '__main__':
    main()
