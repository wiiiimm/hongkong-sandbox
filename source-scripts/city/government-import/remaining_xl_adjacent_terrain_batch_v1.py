"""Sequential source-only adjoining terrain recovery; no live scene acceptance."""
import argparse
import os
import subprocess
import sys
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
TERRAIN = 'government-xl-all-200-original-terrain-batch-v2-20261022'
BULK = 'government-xl-remaining-195-current-scene-batch-v1-20261022'
KNOWN = {'landsd/137130:0', 'landsd/339808:0'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--batch', required=True)
    ap.add_argument('--installed', required=True)
    a = ap.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    doc = BASE / a.batch
    assert not doc.exists()
    refs = [Path(__file__), HERE / 'selected_adjacent_source_terrain_v3.py']
    def pinned(name, filename):
        _, pins = authenticate(BASE / name)
        p = BASE / name / filename
        assert digest(p.read_bytes()) == pins[str(p.relative_to(ROOT))]
        refs.extend([BASE / name / 'result.json', p])
        return read(p)
    terrain = pinned(TERRAIN, 'summary.json')
    installed = pinned(a.installed, 'full-xl-current-count.json')
    bulk = pinned(BULK, 'selection.json')
    pending = {r['uid']: r for r in installed['rows'] if r['uid'] and not r['installedVerified']}
    captures = {uid: BULK + '-chunk-' + str(i).zfill(2) + '-runtime'
                for i, chunk in enumerate(bulk['chunks'], 1) for uid in chunk}
    candidates = []
    for r in terrain['rows']:
        f = r.get('originalTerrainFoundation', {})
        incomplete = r['status'] == 'source-terrain-recovery-required' or f.get('completeTerrainTriangles', 0) < f.get('triangles', 0)
        if incomplete and r['uid'] in pending and r['uid'] not in KNOWN:
            assert r['sourceSHA256'] == pending[r['uid']]['indexedSourceSHA256']
            assert r['uid'] in captures
            candidates.append(dict(uid=r['uid'], sourceSHA256=r['sourceSHA256'], capture=captures[r['uid']]))
    assert len({r['uid'] for r in candidates}) == len(candidates)
    doc.mkdir()
    save(doc / 'selection.json', dict(rows=candidates, excludedKnownRecovery=sorted(KNOWN),
        geometryBasis='Historical actual renderer source coordinates only; no current ground/neighbour approval transferred.',
        installationApproved=False, publication=False))
    outcomes = []
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'OPENBLAS_NUM_THREADS': '1'}
    for n, r in enumerate(candidates, 1):
        child = a.batch + '-' + r['uid'].split('/')[1].replace(':', '-')
        log = doc / (str(n).zfill(3) + '.log')
        command = [sys.executable, str(HERE / 'selected_adjacent_source_terrain_v3.py'),
                   '--batch', child, '--capture', r['capture'], '--uid', r['uid'], '--allow-new-terrain-revision']
        with log.open('w') as stream:
            proc = subprocess.run(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
        outcome = {**r, 'batch': child, 'exitCode': proc.returncode, 'installationApproved': False, 'permanentRejection': False}
        if proc.returncode == 0:
            receipt, pins = authenticate(BASE / child)
            summary = BASE / child / 'summary.json'
            assert digest(summary.read_bytes()) == pins[str(summary.relative_to(ROOT))]
            result = read(summary)['rows'][0]
            assert result['uid'] == r['uid'] and result['sourceSHA256'] == r['sourceSHA256']
            outcome.update(jobId=receipt['jobId'], foundation=result['originalTerrainFoundation'], status='source-terrain-recovered')
            refs.append(BASE / child / 'result.json')
        else:
            outcome.update(status='source-terrain-investigation', log=str(log.relative_to(ROOT)))
        outcomes.append(outcome)
        save(doc / 'progress.json', dict(completed=len(outcomes), selected=len(candidates), rows=outcomes, installationApproved=False))
        print(dict(completed=len(outcomes), total=len(candidates), uid=r['uid'], status=outcome['status']), flush=True)
    result = dict(uids=[r['uid'] for r in candidates], rows=outcomes, selected=len(candidates),
        activeWorkers=0, installationApproved=False, publication=False,
        qualification='Source terrain acquisition/coverage diagnostics only. Failed children remain investigations, never corruption or permanent rejection. Fresh complete placement, identity, neighbours and browser gates remain mandatory.')
    save(doc / 'summary.json', result)
    module('adjacent_batch_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'remaining-xl-adjacent-original-terrain-diagnostics', refs, result)


if __name__ == '__main__':
    main()
