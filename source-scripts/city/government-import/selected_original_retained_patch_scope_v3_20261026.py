"""Complete source and retained-target terrain scope; all current actor checks retained."""
import argparse
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'inventory', 'patch']:
        parser.add_argument('--' + key, required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / args.batch
    assert not doc.exists()
    refs, pins = [Path(__file__)], {}
    receipts = {}
    for name in [args.inventory, args.patch]:
        receipt, bound = authenticate(base / name)
        receipts[name] = receipt
        refs.append(base / name / 'result.json')
        for key, sha in bound.items():
            assert key not in pins or pins[key] == sha
            pins[key] = sha

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    inventory = take(base / args.inventory / 'complete-bounds.json.gz')
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = take(manifestpath)
    candidate = receipts[args.patch]['candidate']
    patchpath = ROOT / candidate['path']
    patch = take(patchpath)
    rootpath = ROOT / '3d-viewer/city/data/terrain.json'
    root = take(rootpath)
    builder = module('selected_scope_extent', HERE / 'resolve-pass-indexed-parent-clipping.py')
    bounds = builder.extent(patch['coarseCells'], root)
    rectangle = shapely.box(*bounds)
    positions = np.asarray(patch['nativeMesh']['position']).reshape(-1, 3)
    for values in [positions, positions.astype('float32').astype('float64')]:
        assert rectangle.covers(shapely.box(float(values[:, 0].min()), float(values[:, 2].min()), float(values[:, 0].max()), float(values[:, 2].max())))
    terrain = []
    for entry in manifest['terrainPatches']:
        path = ROOT / '3d-viewer' / entry['url']
        # These current terrain files are named by the freshly bound manifest;
        # they need not have appeared in the historical source-only receipt.
        key = str(path.relative_to(ROOT))
        pins.setdefault(key, digest(path.read_bytes()))
        node = take(path)
        extent = builder.extent(node['coarseCells'], root)
        contacts = []

        def visit(item, hierarchy):
            if 'nativeMesh' in item:
                values = np.asarray(item['nativeMesh']['position']).reshape(-1, 3)
                values = np.concatenate([values, values.astype('float32').astype('float64')])
                low, high = values.min(0), values.max(0)
                box = shapely.box(float(low[0]), float(low[2]), float(high[0]), float(high[2]))
                if rectangle.intersects(box):
                    contacts.append(dict(hierarchy=hierarchy, packedBounds=list(box.bounds), overlapAreaM2=rectangle.intersection(box).area))
            for index, child in enumerate(item.get('patches', [])):
                visit(child, hierarchy + [index])

        visit(node, [])
        area = rectangle.intersection(shapely.box(*extent)).area
        if contacts or area > 0:
            terrain.append(dict(url=entry['url'], extent=extent, coarseOverlapAreaM2=area, packedContacts=contacts))
    native = [r for r in inventory['rows'] if not closed_disjoint(r['completeFourWorldBounds'], bounds)]
    forms = []
    for entry in manifest['tiles']:
        path = ROOT / '3d-viewer' / entry['url']
        assert digest(path.read_bytes()) == inventory['currentFormTileHashes'][str(path.relative_to(ROOT))]
        refs.append(path)
        for form in read(path)['buildings']:
            points = [point for ring in form.get('rings', []) for point in ring]
            if not points:
                continue
            values = np.asarray(points)
            low, high = values.min(0), values.max(0)
            if rectangle.intersects(shapely.box(float(low[0]), float(low[1]), float(high[0]), float(high[1]))):
                forms.append(form)
    assert len(forms) == len({f['uid'] for f in forms})
    receipt_uids=receipts[args.patch]['uids'];target_uids=patch['meta']['targetUids']
    assert len(receipt_uids)==len(set(receipt_uids)) and len(target_uids)==len(set(target_uids))
    retained=set()
    for record in receipts[args.patch].get('replacedNativeTerrain',[]):
        path=ROOT/'3d-viewer'/record['url']
        assert record['url']in {r['url']for r in manifest['terrainPatches']}
        assert digest(path.read_bytes())==record['sha256']
        old=read(path);assert old['meta']['targetUids']==record['targetUids'] and old['coarseCells']==record['coarseCells']
        assert old['meta']['parentTerrain']==patch['meta']['parentTerrain'] and old['meta']['parentSha256']==patch['meta']['parentSha256']
        a,b,c,d=old['coarseCells'];aa,bb,cc,dd=patch['coarseCells'];assert aa<=a<c<=cc and bb<=b<d<=dd
        retained.update(old['meta']['targetUids']);refs.append(path)
    assert set(target_uids)==set(receipt_uids)|retained, 'Target scope must exactly retain every old obligation plus all new sources'
    result = dict(uids=target_uids, currentNativeActors=len(inventory['rows']), regionalCoarseCells=patch['coarseCells'], regionalParentExtent=bounds, terrainContacts=terrain, positiveAreaTerrainOverlaps=sum(t['coarseOverlapAreaM2'] > 0 or any(c['overlapAreaM2'] > 0 for c in t['packedContacts']) for t in terrain), touchingNativeUids=[r['uid'] for r in native], intersectingForms=len(forms), installationApproved=False, qualification='Complete coarse-cell domain, closed original/literal/two-Float32 bounds and all current base forms. Every touching actor still needs regression checks; positive-area terrain overlap requires explicit retention.')
    save(doc / 'scope.json', result)
    save(doc / 'native-obligations.json.gz', native)
    save(doc / 'form-obligations.json.gz', forms)
    for path in set(refs):
        key = str(path.relative_to(ROOT))
        if key in pins:
            assert digest(path.read_bytes()) == pins[key]
        if key in inventory['currentFormTileHashes']:
            assert digest(path.read_bytes()) == inventory['currentFormTileHashes'][key]
    refs.extend([HERE / 'resolve-pass-indexed-parent-clipping.py', HERE / 'heritage_saved_native_bounds_binding_v1_20261014.py'])
    module('selected_scope_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'complete-selected-original-terrain-repair-scope', list(dict.fromkeys(refs)), result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
