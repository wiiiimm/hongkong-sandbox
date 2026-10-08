"""Complete physical checks for fresh exact routed originals; no approval credit."""
import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from shapely.geometry import box


def route(row):
    spec = importlib.util.spec_from_file_location('routed_rectangles', HERE / 'resolve-pass.py')
    geometry = importlib.util.module_from_spec(spec); spec.loader.exec_module(geometry)
    parent = read(ROOT / '3d-viewer/city/data/terrain.json')
    bounds = geometry.extent(geometry.rectangle_for(row['native']['model']['worldBounds'], parent), parent)
    overlaps = []
    for entry in read(ROOT / '3d-viewer/city/data/manifest.json')['terrainPatches']:
        patch = read(ROOT / '3d-viewer' / entry['url']); g = patch['meta']['georef']
        other = [g['bE']-834500, 816500-g['bN'], g['bE']-834500+(patch['w']-1)*g['aE'], 816500-g['bN']-(patch['h']-1)*g['aN']]
        if box(*bounds).intersection(box(*other)).area > 1e-8:
            overlaps.append((entry['url'], patch))
    if len(overlaps) == 1:
        url, patch = overlaps[0]
        if patch.get('patches') and not patch.get('nativeMesh'):
            return 'xl-routed-cell-nested-terrain-followthrough.py', ['--parent', url]
        if patch.get('nativeMesh') and not patch.get('patches'):
            return 'xl-routed-cell-retained-terrain-followthrough.py', ['--retained', url, '--allow-basic-targets']
    # Complex overlaps stay under the unchanged explicit construction guard.
    return 'xl-routed-cell-indexed-terrain-continuation.py', []


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--inputs', required=True); p.add_argument('--batch', required=True); a = p.parse_args()
    assert Path(a.batch).name == a.batch and a.batch.startswith('government-xl-')
    inputs = (ROOT / a.inputs).resolve(); assert inputs.is_relative_to(ROOT)
    frozen = read(inputs)
    for ref in frozen['evidenceRefs']: assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
    doc = ROOT / 'docs/astra-city/government-import' / a.batch; local = HERE / 'local' / a.batch
    assert not doc.exists(), 'Fresh immutable sequence only'
    local.mkdir(parents=True, exist_ok=True); outcomes = []
    for index, selected in enumerate(frozen['rows'], 1):
        row = next(r for r in read(ROOT / selected['base'] / 'check-selection.json.gz')['rows'] if r['uid'] == selected['uid'])
        assert row['sourceSHA256'] == selected['sourceSHA256']
        token = row['uid'].split('/')[1].replace(':', '-'); batch = a.batch + '-' + token
        runner, flags = route(row)
        command = [sys.executable, str(HERE / runner), '--uid', row['uid'], '--base', selected['base'], '--batch', batch, *flags]
        current = {'uid': row['uid'], 'name': selected['name'], 'sourceSHA256': row['sourceSHA256'], 'batch': batch, 'command': command}
        save(doc / 'working-commands.json', {'finished': outcomes, 'running': current, 'queued': len(frozen['rows'])-index})
        print(json.dumps({'starting': row['uid'], 'position': index, 'total': len(frozen['rows']), 'runner': runner}), flush=True)
        log = local / (token + '.log')
        with log.open('w') as out:
            process = subprocess.run(command, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT)
        path = ROOT / 'docs/astra-city/government-import' / batch
        result = read(path / 'result.json') if (path / 'result.json').exists() else None
        current.update(returncode=process.returncode, result=result, log=str(log.relative_to(ROOT)), newlyInstalled=0,
                       nextStep='Complete guarded staged/live installation immediately.' if result and result['scriptChecksPassed'] else 'Resolve only the exact newly recorded original-source/terrain blockers.')
        outcomes.append(current)
        save(doc / 'working-commands.json', {'finished': outcomes, 'running': None, 'queued': len(frozen['rows'])-index})
        print(json.dumps({'finished': row['uid'], 'passed': bool(result and result['scriptChecksPassed']), 'reasons': result['reasons'] if result else ['command-failure-see-log']}), flush=True)
    save(doc / 'commands.json', {'batch': a.batch, 'rows': outcomes, 'inputs': str(inputs.relative_to(ROOT)), 'inputsSHA256': digest(inputs.read_bytes()),
        'newlyInstalled': 0, 'activeWorkers': 0, 'queuedFollowups': 0, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0,
        'qualification': 'Complete per-source physical phase only. Passing sources still require guarded staged/live browser installation; no diagnostic installation credit. Full327 goal continues.'})

if __name__ == '__main__': main()
