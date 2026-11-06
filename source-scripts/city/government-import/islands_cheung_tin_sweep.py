"""Continue a fresh numbered Cheung source-TIN diagnostic range, without installs.

Earlier waves remain immutable and excluded by the existing nominee selector.
Every negative is checkpointed to Neon. Manifest changes stop the continuation.
"""
import argparse
from pathlib import Path
import subprocess
import sys
from islands_direct_stage import ROOT, HERE, read, save, sha, rel
from islands_peng_tin_sweep import checkpoint


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bounds', type=Path, required=True)
    p.add_argument('--first', type=int, required=True)
    p.add_argument('--last', type=int, required=True)
    a = p.parse_args()
    assert 2 <= a.first <= a.last <= 16 and a.last-a.first < 15
    bounds = a.bounds.resolve(); assert bounds.is_relative_to(ROOT)
    expected = read(bounds)['currentManifest']['sha256']
    base = ROOT / 'docs/astra-city/government-import'
    control = base / f'government-islands-cheung-chau-sweep-{a.first:03d}-{a.last:03d}-control-20261106-v1'
    assert not control.exists()
    completed, seen = [], set()
    for number in range(a.first, a.last+1):
        batch = f'government-islands-cheung-chau-sweep-{number:03d}-20261106-v1'
        doc = base / batch
        assert not doc.exists()
        def call(phase, command):
            assert sha(ROOT / '3d-viewer/city/data/manifest.json') == expected
            log = control / (batch+'-'+phase+'.log'); assert not log.exists()
            save(control / 'state.json', {'state':phase,'batch':batch,'completed':completed,'sourceGeometryChanges':0,'publication':False})
            with log.open('x') as stream:
                code = subprocess.run([str(x) for x in command],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT).returncode
            if code:
                save(control / 'state.json', {'state':'script-error','batch':batch,'phase':phase,'exitCode':code,'log':rel(log),'completed':completed,'publication':False})
                raise RuntimeError('Inspect retained failure; no automatic recovery or approval')
        call('nominate', [sys.executable,HERE/'islands_cheung_tin_sweep_nominate.py','--batch',batch])
        uids = set(read(doc / 'nomination.json')['uids'])
        assert not uids.intersection(seen); seen.update(uids)
        if not uids:
            save(control / 'state.json', {'state':'current-disjoint-nominations-exhausted','completed':completed,'sourcesExamined':len(seen),'newlyInstalled':0,'publication':False})
            return
        call('terrain', [sys.executable,HERE/'islands_stage_owned.py','--batch',batch,'--script','islands_cheung_tin_sweep_stage.py','--pass-batch','--wait'])
        identity = doc / 'identity-evidence.json.gz'
        if read(doc / 'terrain-stage.json')['stagedSourceCandidates']:
            call('scope', [sys.executable,HERE/'islands_tin_current_scope.py','--batch',batch,'--bounds',bounds,'--identity',identity])
            call('runtime', [sys.executable,HERE/'islands_tin_runtime.py','--source-batch',batch,'--batch',batch+'-runtime','--wait'])
            if read(doc / 'runtime-current/summary.json')['clearScriptCandidates']:
                call('clear', [sys.executable,HERE/'islands_tin_clear_subset.py','--source-batch',batch,'--batch',batch+'-clear','--identity',identity])
        completed.append({'batch':batch,**checkpoint(doc,batch)})
        print({k:v for k,v in completed[-1].items() if k != 'inputHashes'},flush=True)
    save(control / 'state.json', {'state':'explicit-wave-limit-complete','completed':completed,'sourcesExamined':len(seen),'newlyInstalled':0,'publication':False})


if __name__ == '__main__':
    main()
