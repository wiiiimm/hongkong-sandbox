"""Finish current terrain scope/neighbour diagnostics while retaining identity holds.

Explicit immediate compute only. No installation, new queues or acceptance credit.
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
    parser.add_argument('--batch', required=True)
    parser.add_argument('--inventory', required=True)
    parser.add_argument('--candidate', action='append', required=True, help='uid,patchBatch,runtimeBatch,identityBatch')
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    candidates = [s.split(',') for s in args.candidate]
    assert all(len(r) == 4 and r[0].startswith('landsd/') and all(n.startswith('government-xl-') and '/' not in n for n in r[1:]) for r in candidates)
    assert len({r[0] for r in candidates}) == len(candidates)
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / args.batch
    assert not doc.exists()
    refs = [Path(__file__)]
    for uid, patch, runtime, identity in candidates:
        for name in [patch, runtime, identity]:
            receipt, pins = authenticate(base / name)
            assert uid in receipt['uids']
            for filename, sha in pins.items():
                assert digest((ROOT / filename).read_bytes()) == sha
            refs.append(base / name / 'result.json')
        assert read(base / patch / 'result.json')['status'] == 'private-terrain-validator-passed'
    doc.mkdir(parents=True)
    save(doc / 'selection.json', dict(candidates=candidates, inventory=args.inventory))
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'OPENBLAS_NUM_THREADS': '1'}

    def process(candidate):
        uid, patch, runtime, identity = candidate
        suffix = uid.split('/')[1].replace(':', '-')
        names = {step: args.batch + '-' + suffix + '-' + step for step in ['scope', 'forms']}
        result = dict(uid=uid, identityReasons=read(base / identity / 'summary.json')['rows'][0]['reasons'], installationApproved=False, newlyInstalled=0, completedJobs=[])
        for step, tool, tail in [
            ('scope', 'selected_original_patch_scope_v1.py', ['--inventory', args.inventory, '--patch', patch]),
            ('forms', 'selected_original_patch_form_checks_v1.py', ['--scope', names['scope'], '--inventory', args.inventory, '--patch', patch]),
        ]:
            with (doc / (suffix + '-' + step + '.log')).open('w') as log:
                proc = subprocess.run([sys.executable, str(HERE / tool), '--batch', names[step], *tail], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
            if proc.returncode:
                result.update(status='script-adapter-investigation', stoppedAt=step, exitCode=proc.returncode)
                break
            receipt = read(base / names[step] / 'result.json')
            result['completedJobs'].append(dict(batch=names[step], jobId=receipt['jobId']))
            if step == 'scope' and receipt['positiveAreaTerrainOverlaps']:
                result.update(status='terrain-retention-required', touchingNativeUids=receipt['touchingNativeUids'], terrainContacts=receipt['terrainContacts'])
                break
        else:
            scope = read(base / names['scope'] / 'scope.json')
            forms = read(base / names['forms'] / 'summary.json')
            result.update(status='neighbour-diagnostics-complete', flaggedForms=forms['flagged'], touchingNativeUids=scope['touchingNativeUids'])
        save(doc / (suffix + '.json'), result)
        print(dict(uid=uid, status=result['status']), flush=True)
        return result

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(process, candidates))
    for result in results:
        for job in result['completedJobs']:
            receipt, pins = authenticate(base / job['batch'])
            assert receipt['jobId'] == job['jobId']
            for filename, sha in pins.items():
                assert digest((ROOT / filename).read_bytes()) == sha
            refs.append(base / job['batch'] / 'result.json')
    summary = dict(uids=[r[0] for r in candidates], rows=results, installationApproved=False, newlyInstalled=0, publication=False, sourceGeometryChanges=0, scriptExternalAICalls=0, qualification='Remaining scope and neighbour diagnostics only; all identity and other acceptance failures remain unresolved.')
    save(doc / 'summary.json', summary)
    module('scope_followthrough_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'selected-original-scope-followthrough', refs, summary)


if __name__ == '__main__':
    main()
