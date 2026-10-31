"""Process explicit XL sources through bounded terrain and current-world checks.

This executes work immediately; it creates no production import/optimisation queue.
Passing diagnostics remain unpublished until the normal source/browser/install flow.
"""
import argparse
import os
import subprocess
import sys
import math
import threading
import numpy as np
import shapely
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
    geometry = {r['uid']: r for r in read(geometrypath)['rows']}
    captured = set(geometry)
    assert {p[0] for p in pairs} <= captured, 'Missing actual renderer geometry; repair capture first'
    save(doc / 'selection.json', dict(candidates=pairs, capture=args.capture, inventory=args.inventory, workers=args.workers, publication=False))
    environment = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'OPENBLAS_NUM_THREADS': '1'}

    # Build one immutable terrain atlas for this exact captured manifest. Include
    # every packed vertex and Float32 world position, even unused vertices.
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    rootpath = ROOT / '3d-viewer/city/data/terrain.json'
    manifestsha = digest(manifestpath.read_bytes())
    assert manifestsha == capture_pins[str(manifestpath.relative_to(ROOT))]
    parent = read(rootpath)
    builder = module('batch_retained_extent', HERE / 'resolve-pass-indexed-parent-clipping.py')
    atlas, atlasrefs = [], [manifestpath, rootpath]
    for entry in read(manifestpath)['terrainPatches']:
        path = ROOT / '3d-viewer' / entry['url']
        node = read(path)
        shapes = [shapely.box(*builder.extent(node['coarseCells'], parent))]
        def visit(value):
            if value.get('nativeMesh'):
                vertices = np.asarray(value['nativeMesh']['position']).reshape(-1, 3)
                vertices = np.concatenate([vertices, vertices.astype('float32').astype('float64')])
                low, high = vertices.min(0), vertices.max(0)
                shapes.append(shapely.box(low[0], low[2], high[0], high[2]))
            for child in value.get('patches', []):
                visit(child)
        visit(node)
        atlas.append(dict(url=entry['url'], sha256=digest(path.read_bytes()), shapes=shapes,
                          flatNative=bool(node.get('nativeMesh')) and not node.get('patches') and not node.get('hydro')))
        atlasrefs.append(path)
    atlaspins = {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in atlasrefs}
    save(doc / 'terrain-atlas.json', dict(inputHashes=atlaspins, patches=[{k: v for k,v in r.items() if k != 'shapes'} for r in atlas]))
    native_lock = threading.Lock()

    def contacts(uid):
        g = geometry[uid]
        tri = np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
        projection = shapely.union_all([shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in tri])
        outer = projection.buffer(1, join_style='mitre').buffer(3, join_style='mitre')
        a,b,c,d = outer.bounds
        georef,size = parent['meta']['georef'],parent['cell']
        cells=[math.floor((a-.001+834500-georef['bE'])/size),math.floor((b-.001-816500+georef['bN'])/size),math.ceil((c+.001+834500-georef['bE'])/size),math.ceil((d+.001-816500+georef['bN'])/size)]
        domain=shapely.box(*builder.extent(cells,parent))
        return [r for r in atlas if any(domain.intersection(shape).area > 0 for shape in r['shapes'])]

    def process(pair):
        uid, ground = pair
        suffix = uid.split('/')[1].replace(':', '-')
        prefix = args.batch + '-' + suffix
        names = {step: prefix + '-' + step for step in ['terrain', 'runtime', 'identity', 'scope', 'forms']}
        result = dict(uid=uid, batches=names, installationApproved=False, newlyInstalled=0)
        touching = contacts(uid)
        result['initialTerrainContacts'] = [{k:v for k,v in r.items() if k != 'shapes'} for r in touching]
        if len(touching) > 1 or (touching and not touching[0]['flatNative']):
            result.update(status='explicit-multiple-or-nested-terrain-retention-required', stoppedAt='terrain-routing', permanentRejection=False, nextAction='Construct exact retained terrain domain and run full current neighbour checks; no AI geometry required.')
            save(doc / (suffix + '.json'), result)
            print(dict(uid=uid,status=result['status']),flush=True)
            return result
        terrain_tool = 'selected_original_retained_replacement_v2.py' if touching else 'selected_original_local_replacement_v2.py'
        retention = ['--retain-patch', touching[0]['url']] if touching else []
        commands = [
            ('terrain', terrain_tool, ['--terrain-check', ground, '--capture', args.capture, '--uid', uid, *retention]),
            ('runtime', 'selected_original_patch_runtime_v2.py', ['--patch', names['terrain'], '--capture', args.capture]),
            ('identity', 'selected_original_identity_v3.py', ['--capture', names['runtime']]),
            ('scope', 'selected_original_patch_scope_v1.py', ['--inventory', args.inventory, '--patch', names['terrain']]),
            ('forms', 'selected_bounded_native_neighbours_v1.py', ['--scope', names['scope'], '--inventory', args.inventory, '--patch', names['terrain']]),
        ]
        for step, script, tail in commands:
            command = [sys.executable, str(HERE / script), '--batch', names[step], *tail]
            logfile = doc / (suffix + '-' + step + '.log')
            def execute():
                with logfile.open('w') as log:
                    return subprocess.run(command, cwd=ROOT, env=environment, stdout=log, stderr=subprocess.STDOUT)
            if step == 'forms':
                # These checks claim the same real root-terrain lease.
                with native_lock:
                    proc = execute()
            else:
                proc = execute()
            if proc.returncode:
                result.update(status='script-adapter-investigation', stoppedAt=step, exitCode=proc.returncode, log=str(logfile.relative_to(ROOT)))
                break
            receipt = read(base / names[step] / 'result.json')
            result.setdefault('completedJobs', []).append(dict(batch=names[step], jobId=receipt['jobId']))
            if step == 'terrain' and receipt['status'] != 'private-terrain-validator-passed':
                result.update(status='terrain-investigation', stoppedAt=step, reasons=[receipt.get('reason', receipt['status'])])
                break
            if step == 'runtime' and any(r['status'] != 'captured' for r in receipt['rows']):
                result.update(status='runtime-investigation', stoppedAt=step, runtimeRows=receipt['rows'])
                break
            if step == 'identity':
                result['identityReasons'] = [reason for r in receipt['rows'] for reason in r['reasons']]
        else:
            metrics = read(base / names['runtime'] / 'metrics.json')
            identity = read(base / names['identity'] / uid.split('/')[1] / 'identity.json')
            metric = next(r for r in metrics['rows'] if r['uid'] == uid)
            policy = module('batch_source_acceptance_' + suffix, HERE / 'acceptance-policy.py')
            reasons = policy.reasons(dict(state='runtime-validated-awaiting-acceptance', sourceSHA256=metric['sourceSHA256'], identityProof=identity['proof']), metric, metrics['profiles']['mobile'])
            foundation = read(base / names['runtime'] / 'summary.json')['rows'][0]
            forms = read(base / names['forms'] / 'summary.json')
            scope = read(base / names['scope'] / 'scope.json')
            clean = not result['identityReasons'] and not reasons and foundation.get('completeTerrainTriangles') == foundation.get('triangles') and foundation.get('fullyBuriedTriangles') == foundation.get('fullyBuriedUpwardTriangles') == 0 and not forms['basicFlags'] and set(forms['nativeResolved']) == set(forms['requiredNativeUids']) and all(r['passed'] for r in forms['nativeRows'])
            result.update(status='ready-for-source-browser-acceptance' if clean else 'current-placement-investigation', rawPolicyReasons=reasons, foundation=foundation, basicFlags=forms['basicFlags'], nativeResolved=forms['nativeResolved'], nativeRows=forms['nativeRows'], touchingNativeUids=scope['touchingNativeUids'], terrainContacts=scope['terrainContacts'])
        save(doc / (suffix + '.json'), result)
        print(dict(uid=uid, status=result['status'], stoppedAt=result.get('stoppedAt')), flush=True)
        return result

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(process, pairs))
    refs = [Path(__file__), HERE / 'acceptance-policy.py', doc / 'terrain-atlas.json', *atlasrefs, base / args.capture / 'result.json', base / args.inventory / 'result.json']
    for path, sha in atlaspins.items():
        assert digest((ROOT/path).read_bytes()) == sha
    verified = {}
    for result in results:
        for completed in result.get('completedJobs', []):
            folder = base / completed['batch']
            receipt, pins = authenticate(folder)
            assert receipt['jobId'] == completed['jobId']
            refs.append(folder / 'result.json')
            # Verify each consumed checkpoint's exact bytes before summarising it.
            for name, sha in pins.items():
                assert name not in verified or verified[name] == sha
                if name not in verified:
                    assert digest((ROOT / name).read_bytes()) == sha
                    verified[name] = sha
    summary = dict(uids=[pair[0] for pair in pairs], rows=results, newlyInstalled=0, installationApproved=False, publication=False, sourceGeometryChanges=0, scriptExternalAICalls=0, qualification='Existing explicit sources processed through current-world script stages. Investigation statuses are technical follow-ups, not AI/human requirements or permanent rejection.')
    save(doc / 'summary.json', summary)
    module('selected_batch_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'selected-existing-xl-current-candidate-batch', refs, summary)


if __name__ == '__main__':
    main()
