"""Process an explicit frozen owned-source cohort through full existing gates.

Sequential publication prevents stale manifest races. Each subprocess owns its
sources and writes a fenced Neon result. Failed sources remain explicit while
independent sources continue. Installation signals prompt coordinator inspection
and exact commits; this runner never stages Git files or performs model AI work.
"""
import argparse
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

from shapely.geometry import box
from run import ROOT, HERE, read, save, digest


def module(filename):
    spec = importlib.util.spec_from_file_location('owned_sequence_routing', HERE / filename)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


def retained_route(row):
    manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
    parent = read(ROOT / '3d-viewer/city/data/terrain.json')
    geometry = module('resolve-pass.py')
    bounds = geometry.extent(geometry.rectangle_for(row['native']['model']['worldBounds'], parent), parent)
    overlapping = []
    for entry in manifest['terrainPatches']:
        patch = read(ROOT / '3d-viewer' / entry['url']); g = patch['meta']['georef']
        other = [g['bE']-834500, 816500-g['bN'],
                 g['bE']-834500+(patch['w']-1)*g['aE'],
                 816500-g['bN']-(patch['h']-1)*g['aN']]
        if box(*bounds).intersection(box(*other)).area > 1e-8:
            overlapping.append((entry['url'], bool(patch.get('nativeMesh') and not patch.get('patches'))))
    # More complex surfaces still go through the root preparer's explicit guard;
    # routing cannot turn an overlap diagnostic into a passing terrain candidate.
    return overlapping[0][0] if len(overlapping) == 1 and overlapping[0][1] else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', required=True)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--after', required=True, help='Completed explicit sequence commands.json to await; publication remains sequential')
    args = parser.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    inputs = (ROOT / args.inputs).resolve(); assert inputs.is_relative_to(ROOT)
    after=(ROOT/args.after).resolve(); assert after.is_relative_to(ROOT/'docs/astra-city/government-import')
    while not after.exists():
        print(json.dumps({'waitingForCompletedSequence':args.after,'externalAICalls':0}),flush=True)
        time.sleep(30)
    prior=read(after); assert prior['activeWorkers']==0 and prior['queuedFollowups']==0
    frozen = read(inputs); assert frozen['rows'] and frozen['scriptExternalAICalls'] == 0
    for ref in frozen['evidenceRefs']:
        assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    local = HERE / 'local' / args.batch
    assert not doc.exists(), 'Fresh explicit sequence only; do not overwrite completed phases'
    local.mkdir(parents=True, exist_ok=True)
    outcomes = []
    for index, selected in enumerate(frozen['rows'], 1):
        base = ROOT / selected['base']
        row = next(r for r in read(base / 'check-selection.json.gz')['rows'] if r['uid'] == selected['uid'])
        assert row['sourceSHA256'] == selected['sourceSHA256']
        token = row['uid'].split('/')[1].replace(':', '-')
        batch = args.batch + '-' + token
        retained = retained_route(row)
        prepare = 'xl-cell-retained-terrain-followthrough.py' if retained else 'xl-cell-indexed-terrain-continuation.py'
        command = [sys.executable, str(HERE / prepare), '--uid', row['uid'], '--batch', batch,
                   '--base', selected['base']]
        if retained: command += ['--retained', retained, '--allow-basic-targets']
        print(json.dumps({'starting': row['uid'], 'name': selected['name'], 'position': index,
                          'total': len(frozen['rows']), 'retainedTerrain': retained}), flush=True)
        outcome = {'uid': row['uid'], 'name': selected['name'], 'sourceSHA256': row['sourceSHA256'],
                   'base': selected['base'], 'batch': batch, 'steps': []}
        save(doc / 'working-commands.json', {'batch': args.batch, 'finished': outcomes,
             'running': outcome, 'queued': len(frozen['rows']) - index, 'scriptExternalAICalls': 0})
        for phase, operation in [('prepare', command)]:
            log = local / (token + '-' + phase + '.log')
            with log.open('w') as out:
                process = subprocess.run(operation, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT)
            path = ROOT / 'docs/astra-city/government-import' / batch
            result = read(path / 'result.json') if (path / 'result.json').exists() else None
            outcome['steps'].append({'phase': phase, 'command': operation, 'returncode': process.returncode,
                 'result': result, 'log': str(log.relative_to(ROOT))})
        if process.returncode == 0 and result and result['scriptChecksPassed']:
            installed = batch + '-installed'
            installer = 'xl-explicit-cell-retained-install.py' if retained else 'xl-explicit-cell-root-install.py'
            command = [sys.executable, str(HERE / installer), '--uid', row['uid'], '--batch', installed,
                 '--source', str(path.relative_to(ROOT)), '--base', selected['base']]
            log = local / (token + '-installed.log')
            print(json.dumps({'installing': row['uid'], 'phase': installed}), flush=True)
            with log.open('w') as out:
                process = subprocess.run(command, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT)
            path = ROOT / 'docs/astra-city/government-import' / installed
            installation = read(path / 'result.json') if (path / 'result.json').exists() else None
            outcome['steps'].append({'phase': 'installed', 'command': command,
                 'returncode': process.returncode, 'result': installation, 'log': str(log.relative_to(ROOT))})
            if installation and installation.get('installedUids') == [row['uid']]:
                save(doc / ('commit-required-' + token + '.json'), {'uid': row['uid'], 'installation': installed})
        final = outcome['steps'][-1]['result']
        outcome['installed'] = bool(final and final.get('installedUids') == [row['uid']])
        outcome['nextStep'] = ('Inspect exported browser evidence and commit/push exact installation assets.'
             if outcome['installed'] else 'Continue exact recorded technical reasons under a fresh phase; no AI/human requirement inferred.')
        outcomes.append(outcome)
        save(doc / 'working-commands.json', {'batch': args.batch, 'finished': outcomes,
             'running': None, 'queued': len(frozen['rows']) - index, 'scriptExternalAICalls': 0})
        print(json.dumps({'finished': row['uid'], 'installed': outcome['installed'], 'position': index,
                          'reasons': final.get('reasons') if final else ['command-failure-see-log']}), flush=True)
    save(doc / 'commands.json', {'batch': args.batch, 'rows': outcomes, 'inputs': args.inputs,
        'inputsSHA256': digest(inputs.read_bytes()), 'newlyInstalled': sum(r['installed'] for r in outcomes),
        'scriptExternalAICalls': 0, 'modelGeometryChanges': 0, 'activeWorkers': 0, 'queuedFollowups': 0,
        'qualification': 'Explicit bounded cohort. Exact per-phase Neon results and installed-verified acceptance determine credit. This sequence does not complete the wider 100-install target.'})


if __name__ == '__main__': main()
