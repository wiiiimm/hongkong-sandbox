"""Batch preview against unchanged government 5 m grid; no acceptance or edits.

Historical world meshes are explicit diagnostic inputs, not current acceptance.
Positive previews still need fresh identity, full terrain/foundation/neighbour,
rendered sampler, runtime and publication checks. No model/elevation corrections.
"""
import gzip
import hashlib
import json
import math
import zipfile
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SHA = '785718f462ae6de3c9e1fed2bf9fe5affe1c1d739c0a969fd62cf3680b4b33ab'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_mesh(path, uid):
    data = json.loads(gzip.decompress(path.read_bytes()))
    row = next(r for r in data['rows'] if r['uid'] == uid)
    vertices = np.asarray(row['position']).reshape(-1, 3)
    faces = vertices[np.asarray(row['index']).reshape(-1, 3)]
    return data, row, vertices, faces


def grid_coordinates(points):
    # ASCII corner is 799997.5; sample centres start at E800000/N848000.
    return np.stack(((points[:, 0] + 834500 - 800000) / 5,
                     (848000 - (816500 - points[:, 2])) / 5), axis=1)


def heights(points, grid, bounds):
    coords = grid_coordinates(points)
    cell = np.floor(coords).astype(int)
    tx, ty = (coords - cell).T
    c, r = (cell - np.array(bounds[:2])).T
    a, b, d, e = grid[r, c], grid[r, c + 1], grid[r + 1, c], grid[r + 1, c + 1]
    assert np.min(np.stack((a, b, d, e))) > -9999
    # Original grid heights only, with a fixed SW/NE diagonal in grid space.
    return np.where(tx + ty <= 1, a + (b-a)*tx + (d-a)*ty,
                    e + (d-e)*(1-tx) + (b-e)*(1-ty))


def metrics(points, bottom, grid, bounds):
    gap = points[:, 1] - heights(points, grid, bounds)
    low = gap[points[:, 1] <= bottom + .35]
    return {'checks': len(points), 'lowRimChecks': len(low),
            'minSurfaceGap': float(gap.min()),
            'minLowGap': float(low.min()), 'maxLowGap': float(low.max())}


def eligible(m):
    return m['minSurfaceGap'] >= -.5 and m['minLowGap'] <= .1 and m['maxLowGap'] <= 1


def main():
    source = ROOT / 'references/codex/hongkong-3d-model/data/hk-landsd-5m/Whole_HK_DTM_5m.zip'
    assert digest(source) == SHA
    routing = HERE / 'local/government-xl-current-physical-routing-preview-20261007.json'
    output = HERE / 'local/government-xl-original-dtm-contact-preview-20261007'
    assert not output.exists()
    output.mkdir()
    jobs, needed = [], {}
    for row in json.loads(routing.read_bytes())['rows']:
        if 'source-identity-fit' in row['reasons']:
            continue
        path = HERE / 'local' / row['batch'] / 'runtime-geometry.json.gz'
        if not path.exists():
            continue
        data, mesh, vertices, faces = load_mesh(path, row['uid'])
        coords = grid_coordinates(vertices)
        lo, hi = np.floor(coords.min(axis=0)).astype(int), np.floor(coords.max(axis=0)).astype(int) + 1
        assert lo[0] >= 0 and lo[1] >= 0 and hi[0] < 12751 and hi[1] < 9601
        bounds = [int(lo[0]), int(lo[1]), int(hi[0]), int(hi[1])]
        grid = np.full((hi[1]-lo[1]+1, hi[0]-lo[0]+1), np.nan)
        jobs.append((row, path, digest(path), mesh['sourceSHA256'], bounds, grid))
        for r in range(lo[1], hi[1]+1):
            needed.setdefault(r, []).append((grid, r-lo[1], lo[0], hi[0]+1))
    with zipfile.ZipFile(source) as archive:
        name = next(n for n in archive.namelist() if n.lower().endswith('.asc'))
        with archive.open(name) as stream:
            header = [stream.readline().decode().strip() for _ in range(6)]
            assert header == json.loads((ROOT / 'docs/astra-city/landmark-preflight/terrain-inputs.json').read_bytes())['dtm']['asciiHeader']
            for r in range(max(needed)+1):
                line = stream.readline()
                if r in needed:
                    values = np.fromstring(line.decode(), sep=' ')
                    assert len(values) == 12751
                    for grid, ri, c0, c1 in needed[r]:
                        grid[ri] = values[c0:c1]
    results = []
    for row, path, geometry_sha, source_sha, bounds, grid in jobs:
        assert digest(path) == geometry_sha and np.isfinite(grid).all()
        data, mesh, vertices, faces = load_mesh(path, row['uid'])
        bottom = float(vertices[:, 1].min())
        points = np.concatenate((vertices, faces.mean(axis=1)))
        m = metrics(points, bottom, grid, bounds)
        edge_count = 0
        if eligible(m):
            edge_points = []
            for face in faces:
                for i in range(3):
                    a, b = face[i], face[(i+1) % 3]
                    if max(a[1], b[1]) > bottom + .35:
                        continue
                    n = math.ceil(np.linalg.norm((a-b)[[0, 2]]))
                    if n > 1:
                        edge_points.extend(a+(b-a)*j/n for j in range(1, n))
            if edge_points:
                points = np.concatenate((points, edge_points))
                edge_count = len(edge_points)
                m = metrics(points, bottom, grid, bounds)
        grid_path = output / (row['uid'].replace('landsd/', '').replace(':', '-') + '-grid.json.gz')
        grid_path.write_bytes(gzip.compress(json.dumps({'bounds': bounds, 'heights': grid.tolist(), 'sourceSHA256': SHA, 'cellSize': 5, 'origin': [800000, 848000]}).encode(), mtime=0))
        results.append({'uid': row['uid'], 'priorBatch': row['batch'],
            'geometry': {'path': str(path.relative_to(ROOT)), 'sha256': geometry_sha},
            'sourceSHA256': source_sha, 'grid': {'path': str(grid_path.relative_to(ROOT)), 'sha256': digest(grid_path)},
            'currentInputHashesMatch': all((ROOT / p).exists() and digest(ROOT / p) == sha for p, sha in data['inputHashes'].items()),
            'metrics': m, 'edgeChecks': edge_count, 'terrainContactPreviewPass': eligible(m)})
        print(json.dumps({'uid': row['uid'], 'previewPass': eligible(m), **m}), flush=True)
    result = {'source': {'path': str(source.relative_to(ROOT)), 'sha256': SHA},
              'routing': {'path': str(routing.relative_to(ROOT)), 'sha256': digest(routing)},
              'runnerSHA256': digest(Path(__file__)), 'rows': results,
              'diagnosticOnly': True, 'publication': False, 'newlyInstalled': 0,
              'modelGeometryChanges': 0, 'scriptExternalAICalls': 0}
    (output / 'result.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'models': len(results), 'positivePreviews': [r['uid'] for r in results if r['terrainContactPreviewPass']]}))


if __name__ == '__main__':
    main()
