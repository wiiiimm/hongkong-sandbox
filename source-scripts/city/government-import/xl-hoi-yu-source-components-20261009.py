"""Complete original component census and source capture; diagnostic only."""
import importlib.util
import json
import os
import shutil
import subprocess
import uuid
from collections import defaultdict
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from original_shell_diagnostic_20261009 import shell_context

BATCH = 'government-xl-hoi-yu-source-components-20261009'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
LOCAL = HERE / 'local' / BATCH
OLD = ROOT / 'docs/astra-city/government-import/government-xl-hoi-yu-original-pair-v2-20261009'


def main():
    assert not DOC.exists() and not LOCAL.exists()
    claim = reservations.claim('codex-hoi-yu-components-' + str(uuid.uuid4()),
                               ['building:landsd/177604:0', 'building:landsd/177605:0'], batch=BATCH)
    assert claim['ok'], claim
    lease = claim['reservation']
    save(LOCAL / 'reservation.json', json.loads(json.dumps(lease, default=str)))
    try:
        rows = read(OLD / 'selection.json.gz')['rows']
        tower = next(r for r in rows if r['uid'] == 'landsd/177605:0')
        spec = importlib.util.spec_from_file_location('hoi_yu_components_decoder', HERE / 'xl-second-pass.py')
        decoder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(decoder)
        decoder.LOCAL = LOCAL
        (LOCAL / 'assets').mkdir()
        raw = (ROOT / tower['candidate']['path']).read_bytes()
        assert digest(raw) == tower['sourceSHA256']
        (LOCAL / 'assets' / (tower['sourceSHA256'] + '.glb.gz')).write_bytes(raw)
        triangles = decoder.glb_triangles({**tower, 'triangles': tower['native']['model']['triangles']})
        parents = list(range(len(triangles)))
        def find(i):
            while parents[i] != i:
                parents[i] = parents[parents[i]]
                i = parents[i]
            return i
        edges = {}
        for i, face in enumerate(triangles):
            for a, b in zip(face, np.roll(face, -1, axis=0)):
                key = tuple(sorted((tuple(a), tuple(b))))
                if key in edges:
                    parents[find(i)] = find(edges[key])
                else:
                    edges[key] = i
        groups = defaultdict(list)
        for i in range(len(triangles)):
            groups[find(i)].append(i)
        components = []
        for ids in groups.values():
            result = shell_context(triangles[ids], [0])
            assert len(result['componentFaces']) == len(ids)
            components.append({**result, 'originalSourceFaces': ids})
        components.sort(key=lambda r: (r['bounds'][0][1], -r['triangles']))
        assert sum(r['triangles'] for r in components) == len(triangles)
        save(DOC / 'components.json.gz', {'uid': tower['uid'], 'sourceSHA256': tower['sourceSHA256'],
             'sourceTriangles': len(triangles), 'components': components, 'completeFaceAccounting': True,
             'diagnosticOnly': True, 'placementAccepted': False, 'modelGeometryChanges': 0})
        forms = [r['source']['building'] for r in rows]
        parts = [{'uid': r['uid'], 'name': r['source']['building'].get('name'), 'modelId': r['modelId'],
                  'sourceSHA256': r['sourceSHA256'], 'assetPath': r['candidate']['path'],
                  'worldBounds': r['native']['model']['worldBounds'], 'triangles': r['native']['model']['triangles'],
                  'forms': forms} for r in rows]
        primary = next(p for p in parts if p['uid'] == tower['uid'])
        primary['originalComponents'] = [p for p in parts if p is not primary]
        primary['failedSamples'] = read(OLD / 'support-checks.json.gz')['rows'][0]['interface']['unresolved']
        hashes = {str((OLD / 'result.json').relative_to(ROOT)): digest((OLD / 'result.json').read_bytes())}
        for r in rows:
            hashes[r['candidate']['path']] = r['sourceSHA256']
            p = '3d-viewer/' + r['source']['tile']
            hashes[p] = digest((ROOT / p).read_bytes())
        save(DOC / 'inputs.json', {'models': [primary], 'inputHashes': hashes})
        assert reservations.owns(lease)
        subprocess.run(['node', str(HERE / 'render-original-component-evidence.mjs'), '--inputs',
                        str((DOC / 'inputs.json').relative_to(ROOT)), '--out', str(DOC.relative_to(ROOT))],
                       cwd=ROOT, env={**os.environ, 'CHROME_PATH': '/opt/google/chrome/chrome'}, check=True)
        print(json.dumps({'sourceTriangles': len(triangles), 'componentCount': len(components),
              'lowComponents': [{k: c[k] for k in ['triangles', 'bounds', 'closedConsistentlyOriented']} for c in components[:12]],
              'captured': True}), flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
