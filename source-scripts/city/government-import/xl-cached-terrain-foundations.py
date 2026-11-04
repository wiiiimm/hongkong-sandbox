"""Audit every cached held XL terrain candidate against original model faces."""
import importlib.util
import shapely
from run import ROOT, HERE, read, save, digest


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


final = module('cached_terrain_final', 'xl-final-script-pass.py')
patches = module('cached_terrain_patch', 'native_patch_resolution.py')
BASE = ROOT / 'docs/astra-city/government-import/government-xl-remaining-20260923'


def run():
    held = {r['uid'] for r in read(BASE / 'reconciliation.json.gz')['rows'] if r['primaryHold'] == 'terrain-contact'}
    selection = {r['uid']: r for r in read(BASE / 'selection.json.gz')['rows']}
    output = []
    for path in sorted(BASE.glob('*terrain-diagnostic*/result.json')):
        result = read(path)
        targets = [uid for uid in result.get('uids', []) if uid in held]
        if not targets:
            continue
        patch_path = ROOT / result['patchPath']
        assert digest(patch_path.read_bytes()) == result['patchSHA256']
        terrain = patches._faces(read(patch_path))
        for uid in targets:
            row = selection[uid]
            record = {'uid': uid, 'name': row.get('name'), 'diagnostic': str(path.parent.relative_to(ROOT)),
                      'sourceSHA256': row['sourceSHA256'], 'patchSHA256': result['patchSHA256']}
            try:
                model = final.s.glb_triangles(row)
                # Use the frozen exact form, not an inferred box.
                form = row['source']['building']
                assert form['uid'] == uid
                footprint = shapely.Polygon(form['rings'][0], form['rings'][1:])
                foundation = final.foundation_context(model, terrain, footprint)
                record['foundation'] = foundation
                record['strictFoundationAccepted'] = (foundation['completeTerrainTriangles'] == foundation['triangles'] and foundation['fullyBuriedUpwardTriangles'] == 0 and foundation['fullyBuriedAreaFraction'] <= .001)
            except (FileNotFoundError, KeyError) as error:
                record['unavailable'] = str(error)
            output.append(record)
            print({k: v for k, v in record.items() if k not in ('foundation', 'sourceSHA256', 'patchSHA256')}, flush=True)
    save(BASE / 'cached-terrain-foundations-20260929.json', {'rows': output, 'aiCalls': 0, 'modelGeometryChanges': 0, 'publication': False})


if __name__ == '__main__':
    run()
