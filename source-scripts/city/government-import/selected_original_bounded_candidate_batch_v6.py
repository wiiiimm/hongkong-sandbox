"""Process explicit XL sources through bounded terrain and current-world checks.

This executes work immediately; it creates no production import/optimisation queue.
Passing diagnostics remain unpublished until the normal source/browser/install flow.
"""
import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'capture', 'inventory']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--candidate', action='append', required=True, help='uid,terrainCheckBatch')
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--terrain-strategy', choices=['lower-inset', 'original-replacement'], default='lower-inset')
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    assert 1 <= args.workers <= 2
    pairs = [entry.split(',') for entry in args.candidate]
    assert all(len(pair) == 2 and pair[0].startswith('landsd/') and pair[1].startswith('government-xl-') for pair in pairs)
    assert len({pair[0] for pair in pairs}) == len(pairs)
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / args.batch
    assert not doc.exists()
    doc.mkdir(parents=True)
    # Require real actual-renderer geometry before starting expensive terrain work.
    capture_receipt, capture_pins = authenticate(base / args.capture)
    geometrypath = HERE / 'local' / args.capture / 'runtime-geometry.json.gz'
    assert digest(geometrypath.read_bytes()) == capture_pins[str(geometrypath.relative_to(ROOT))]
    captured = {r['uid'] for r in read(geometrypath)['rows']}
    assert {p[0] for p in pairs} <= captured, 'Missing actual renderer geometry; repair capture first'
    save(doc / 'selection.json', dict(candidates=pairs, capture=args.capture, inventory=args.inventory, workers=args.workers, terrainStrategy=args.terrain_strategy, publication=False))
    environment = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'OPENBLAS_NUM_THREADS': '1'}

    def process(pair):
        uid, ground = pair
        suffix = uid.split('/')[1].replace(':', '-')
        prefix = args.batch + '-' + suffix
        names = {step: prefix + '-' + step for step in ['terrain', 'runtime', 'identity', 'scope', 'forms']}
        result = dict(uid=uid, batches=names, installationApproved=False, newlyInstalled=0)
        commands = [
            ('terrain', ('selected_original_local_replacement_v1.py' if args.terrain_strategy == 'original-replacement' else 'selected_original_local_inset_v7.py'), ['--terrain-check', ground, '--capture', args.capture, '--uid', uid]),
            ('runtime', 'selected_original_patch_runtime_v2.py', ['--patch', names['terrain'], '--capture', args.capture]),
            ('identity', 'selected_original_identity_v3.py', ['--capture', names['runtime']]),
            ('scope', 'selected_original_patch_scope_v1.py', ['--inventory', args.inventory, '--patch', names['terrain']]),
            ('forms', 'selected_original_patch_form_checks_v1.py', ['--scope', names['scope'], '--inventory', args.inventory, '--patch', names['terrain']]),
        ]
        for step, script, tail in commands:
            command = [sys.executable, str(HERE / script), '--batch', names[step], *tail]
            logfile = doc / (suffix + '-' + step + '.log')
            with logfile.open('w') as log:
                proc = subprocess.run(command, cwd=ROOT, env=environment, stdout=log, stderr=subprocess.STDOUT)
            if proc.returncode:
                result.update(status='script-adapter-investigation', stoppedAt=step, exitCode=proc.returncode, log=str(logfile.relative_to(ROOT)))
                break
            receipt = read(base / names[step] / 'result.json')
            result.setdefault('completedJobs', []).append(dict(batch=names[step], jobId=receipt['jobId']))
            if step == 'terrain' and receipt['status'] != 'private-terrain-validator-passed':
                reason = receipt.get('reason') or receipt.get('errorType') or receipt['status']
                result.update(status='terrain-investigation', stoppedAt=step, reasons=[reason])
                failure = base / names[step] / 'failure.json'
                if failure.exists():
                    detail = read(failure)
                    result['failureEvidence'] = dict(path=str(failure.relative_to(ROOT)), sha256=digest(failure.read_bytes()))
                    result['failureTracebackTail'] = detail.get('traceback', '').splitlines()[-8:]
                break
            if step == 'runtime' and any(r['status'] != 'captured' for r in receipt['rows']):
                result.update(status='runtime-investigation', stoppedAt=step, runtimeRows=receipt['rows'])
                break
            if step == 'identity':
                result['identityReasons'] = [reason for r in receipt['rows'] for reason in r['reasons']]
            if step == 'scope' and receipt['positiveAreaTerrainOverlaps']:
                result.update(status='overlapping-terrain-investigation', stoppedAt=step, reasons=receipt['terrainContacts'])
                break
        else:
            metrics = read(base / names['runtime'] / 'metrics.json')
            identity = read(base / names['identity'] / uid.split('/')[1] / 'identity.json')
            metric = next(r for r in metrics['rows'] if r['uid'] == uid)
            policy = module('batch_source_acceptance_' + suffix, HERE / 'acceptance-policy.py')
            reasons = policy.reasons(dict(state='runtime-validated-awaiting-acceptance', sourceSHA256=metric['sourceSHA256'], identityProof=identity['proof']), metric, metrics['profiles']['mobile'])
            foundation = read(base / names['runtime'] / 'summary.json')['rows'][0]
            forms = read(base / names['forms'] / 'summary.json')
            scope = read(base / names['scope'] / 'scope.json')
            clean = not result['identityReasons'] and not reasons and foundation.get('completeTerrainTriangles') == foundation.get('triangles') and foundation.get('fullyBuriedTriangles') == 0 and not forms['flagged'] and not scope['touchingNativeUids']
            result.update(status='ready-for-source-browser-acceptance' if clean else 'current-placement-investigation', rawPolicyReasons=reasons, foundation=foundation, flaggedForms=forms['flagged'], touchingNativeUids=scope['touchingNativeUids'])
        save(doc / (suffix + '.json'), result)
        print(dict(uid=uid, status=result['status'], stoppedAt=result.get('stoppedAt')), flush=True)
        return result

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(process, pairs))
    refs = [Path(__file__), HERE / 'acceptance-policy.py']
    for result in results:
        for completed in result.get('completedJobs', []):
            folder = base / completed['batch']
            receipt, pins = authenticate(folder)
            assert receipt['jobId'] == completed['jobId']
            refs.append(folder / 'result.json')
            # Verify each consumed checkpoint's exact bytes before summarising it.
            for name, sha in pins.items():
                assert digest((ROOT / name).read_bytes()) == sha
    summary = dict(uids=[pair[0] for pair in pairs], rows=results, newlyInstalled=0, installationApproved=False, publication=False, sourceGeometryChanges=0, scriptExternalAICalls=0, terrainStrategy=args.terrain_strategy, qualification='Existing explicit sources processed through current-world script stages. Investigation statuses are technical follow-ups, not AI/human requirements or permanent rejection.')
    save(doc / 'summary.json', summary)
    module('selected_batch_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'selected-existing-xl-current-candidate-batch', refs, summary)


if __name__ == '__main__':
    main()
