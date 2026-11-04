"""Prepare immutable pointwise original-surface diagnostics; never accept models."""
import argparse
import importlib.util
import math
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest


def parent_heights(points, data):
    g = data['meta']['georef']; w, h = data['w'], data['h']
    c = (points[:, 0]+834500-g['bE'])/g['aE']
    r = (816500-points[:, 2]-g['bN'])/g['aN']
    i = np.clip(c.astype(int), 0, w-2); j = np.clip(r.astype(int), 0, h-2)
    u, v = c-i, r-j
    elevations = np.asarray(data['elev'], dtype=float)
    display = np.maximum(1.2, elevations); display[elevations <= 0] = -4
    if data.get('renderedElev'):
        overrides = np.array([np.nan if value is None else value for value in data['renderedElev']])
        display = np.where(np.isfinite(overrides), overrides, display)
    a, b, d, e = [display[idx] for idx in (j*w+i, j*w+i+1, (j+1)*w+i, (j+1)*w+i+1)]
    return np.where(u+v <= 1, a+(b-a)*u+(d-a)*v, e+(d-e)*(1-u)+(b-e)*(1-v))


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--batch', required=True); args = parser.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    output = HERE/'local'/args.batch; assert not output.exists()
    preview_path = ROOT/'docs/astra-city/government-import/government-xl-original-dtm-contact-preview-20261007/result.json'
    preview = read(preview_path); assert digest((ROOT/preview['source']['path']).read_bytes()) == preview['source']['sha256']
    manifest_path = ROOT/'3d-viewer/city/data/manifest.json'; manifest = read(manifest_path)
    installed = {m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
    parent_path = ROOT/'3d-viewer/city/data/terrain.json'; parent = read(parent_path)
    spec = importlib.util.spec_from_file_location('exact_dtm_preview', HERE/'xl-original-dtm-contact-preview.py')
    dtm = importlib.util.module_from_spec(spec); spec.loader.exec_module(dtm)
    rows = []
    for old in preview['rows']:
        if old['uid'] in installed: continue
        geometry_path = ROOT/old['geometry']['path']; assert digest(geometry_path.read_bytes()) == old['geometry']['sha256']
        geometry = read(geometry_path); model = next(r for r in geometry['rows'] if r['uid'] == old['uid'])
        assert model['sourceSHA256'] == old['sourceSHA256']
        positions = np.asarray(model['position']).reshape(-1, 3)
        faces = positions[np.asarray(model['index']).reshape(-1, 3)]; bottom = float(positions[:, 1].min())
        points = [positions, faces.mean(axis=1)]; edges = []
        for face in faces:
            for index in range(3):
                a, b = face[index], face[(index+1)%3]
                if max(a[1], b[1]) > bottom+.35: continue
                count = math.ceil(np.linalg.norm((a-b)[[0, 2]]))
                edges.extend(a+(b-a)*part/count for part in range(1, count))
        if edges: points.append(np.array(edges))
        points = np.concatenate(points)
        grid_path = ROOT/old['grid']['path']; assert digest(grid_path.read_bytes()) == old['grid']['sha256']
        grid = read(grid_path); assert grid['sourceSHA256'] == preview['source']['sha256']
        path = output/(old['uid'].split('/')[1].replace(':','-')+'-samples.json.gz')
        save(path, {'uid': old['uid'], 'sourceSHA256': old['sourceSHA256'], 'geometry': old['geometry'],
            'points': points.tolist(), 'bottom': bottom, 'edgeChecks': len(edges),
            'originalParentHeights': parent_heights(points,parent).tolist(),
            'originalDTMHeights': dtm.heights(points,np.array(grid['heights']),grid['bounds']).tolist(),
            'grid': old['grid'], 'currentInputHashesMatch': all((ROOT/p).exists() and digest((ROOT/p).read_bytes())==sha for p,sha in geometry['inputHashes'].items())})
        rows.append({'uid':old['uid'],'samples':{'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}})
    save(output/'inputs.json',{'rows':rows,'parent':{'path':str(parent_path.relative_to(ROOT)),'sha256':digest(parent_path.read_bytes())},
        'source':preview['source'],'manifest':{'path':str(manifest_path.relative_to(ROOT)),'sha256':digest(manifest_path.read_bytes())},
        'preview':{'path':str(preview_path.relative_to(ROOT)),'sha256':digest(preview_path.read_bytes())},
        'runnerSHA256':digest(Path(__file__).read_bytes()),'diagnosticOnly':True,'publication':False,'modelGeometryChanges':0})
    print({'models':len(rows),'diagnosticOnly':True},flush=True)

if __name__=='__main__': main()
