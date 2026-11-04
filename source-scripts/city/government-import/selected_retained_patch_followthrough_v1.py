"""Continue a retained original terrain candidate through complete current scene gates."""
import argparse
import os
import subprocess
import sys
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'patch', 'capture', 'inventory', 'uid']:
        ap.add_argument('--' + k, required=True)
    a = ap.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / a.batch
    assert not doc.exists()
    patch, pins = authenticate(base / a.patch)
    assert patch['status'] == 'private-terrain-validator-passed' and patch['uids'] == [a.uid]
    candidate = ROOT / patch['candidate']['path']
    assert digest(candidate.read_bytes()) == patch['candidate']['sha256'] == pins[str(candidate.relative_to(ROOT))]
    doc.mkdir()
    names = {k: a.batch + '-' + k for k in ['runtime', 'identity', 'scope', 'neighbours']}
    commands = [
        ('runtime', 'selected_original_patch_runtime_v2.py', ['--patch', a.patch, '--capture', a.capture]),
        ('identity', 'selected_original_identity_v3.py', ['--capture', names['runtime']]),
        ('scope', 'selected_original_patch_scope_v1.py', ['--inventory', a.inventory, '--patch', a.patch]),
        ('neighbours', 'selected_bounded_native_neighbours_v1.py', ['--scope', names['scope'], '--inventory', a.inventory, '--patch', a.patch]),
    ]
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'OPENBLAS_NUM_THREADS': '1'}
    refs = [Path(__file__), base / a.patch / 'result.json', candidate]
    result = dict(uids=[a.uid], batches=names, patch=a.patch, installationApproved=False, publication=False)
    for phase, script, tail in commands:
        with (doc / (phase + '.log')).open('w') as log:
            proc = subprocess.run([sys.executable, str(HERE / script), '--batch', names[phase], *tail], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        if proc.returncode:
            result.update(status='script-investigation', failedPhase=phase, exitCode=proc.returncode)
            break
        receipt, _ = authenticate(base / names[phase])
        refs.append(base / names[phase] / 'result.json')
        print(dict(phase=phase, jobId=receipt['jobId']), flush=True)
        if phase == 'runtime' and any(r['status'] != 'captured' for r in receipt['rows']):
            result.update(status='runtime-investigation', failedPhase=phase)
            break
    else:
        identity = read(base / names['identity'] / a.uid.split('/')[1] / 'identity.json')
        metrics = read(base / names['runtime'] / 'metrics.json')
        metric = next(r for r in metrics['rows'] if r['uid'] == a.uid)
        policy = module('existing_patch_policy', HERE / 'acceptance-policy.py')
        reasons = policy.reasons(dict(state='runtime-validated-awaiting-acceptance', sourceSHA256=metric['sourceSHA256'], identityProof=identity['proof']), metric, metrics['profiles']['mobile'])
        foundation = read(base / names['runtime'] / 'summary.json')['rows'][0]
        scope = read(base / names['scope'] / 'scope.json')
        forms = read(base / names['neighbours'] / 'summary.json')
        clean = not reasons and identity['passed'] and foundation['completeTerrainTriangles'] == foundation['triangles'] and foundation['fullyBuriedTriangles'] == foundation['fullyBuriedUpwardTriangles'] == 0 and not forms['basicFlags'] and set(forms['nativeResolved']) == set(forms['requiredNativeUids']) and all(r['passed'] for r in forms['nativeRows'])
        result.update(status='ready-for-all-mode-and-browser-checks' if clean else 'current-placement-investigation', rawPolicyReasons=reasons, identityReasons=identity['reasons'], foundation=foundation, basicFlags=forms['basicFlags'], nativeResolved=forms['nativeResolved'], nativeRows=forms['nativeRows'], touchingNativeUids=scope['touchingNativeUids'], terrainContacts=scope['terrainContacts'])
    checked = {}
    for name in names.values():
        if not (base / name / 'result.json').exists():
            continue
        _, bound = authenticate(base / name)
        for path, sha in bound.items():
            assert path not in checked or checked[path] == sha
            if path not in checked:
                assert digest((ROOT / path).read_bytes()) == sha
                checked[path] = sha
    result['distinctPhaseReferencesRehashed'] = len(checked)
    save(doc / 'summary.json', result)
    module('existing_patch_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'selected-existing-private-patch-current-followthrough', refs, result)


if __name__ == '__main__':
    main()
