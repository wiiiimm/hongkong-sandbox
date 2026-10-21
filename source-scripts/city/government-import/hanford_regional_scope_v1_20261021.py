"""Nominate full root-cell repair scope and current neighbour obligations."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-hanford-regional-scope-v1-20261021'
DOC = BASE / BATCH
UID = 'landsd/276187:0'

def main():
    assert not DOC.exists()
    refs = [Path(__file__)]
    consumed = {}
    def take(batch, path):
        _, pins = authenticate(BASE / batch)
        key = str(path.relative_to(ROOT))
        assert digest(path.read_bytes()) == pins[key], key
        consumed[key] = pins[key]
        refs.extend([BASE / batch / 'result.json', path])
        return read(path)
    ib = 'government-xl-hanford-current-inventory-v1-20261021'
    inventory = take(ib, BASE / ib / 'complete-bounds.json.gz')
    manifest = take(ib, ROOT / '3d-viewer/city/data/manifest.json')
    pb = 'government-xl-hanford-pair-terrain-scope-v1-20261021'
    preliminary = take(pb, BASE / pb / 'scope.json')
    rootpath = ROOT / '3d-viewer/city/data/terrain.json'
    root = read(rootpath)
    consumed[str(rootpath.relative_to(ROOT))] = digest(rootpath.read_bytes())
    refs.append(rootpath)
    builder = module('illumination_scope_builder', HERE / 'resolve-pass-indexed-parent-clipping.py')
    cells = preliminary['baseReplacementCells']
    extent = builder.extent(cells, root)
    rectangle = shapely.box(*extent)
    overlaps = []
    boundary_contacts = []
    for entry in manifest['terrainPatches']:
        path = ROOT / '3d-viewer' / entry['url']
        patch = read(path)
        bounds = builder.extent(patch['coarseCells'], root)
        packed_hits = []
        def inspect(node, hierarchy):
            if 'nativeMesh' in node:
                values = np.asarray(node['nativeMesh']['position']).reshape(-1, 3)
                values = np.concatenate([values, values.astype('float32').astype('float64')])
                low, high = values.min(0), values.max(0)
                packed = [float(low[0]), float(low[2]), float(high[0]), float(high[2])]
                if rectangle.intersects(shapely.box(*packed)):
                    packed_hits.append(dict(hierarchy=hierarchy, packedBounds=packed,
                                            overlapAreaM2=rectangle.intersection(shapely.box(*packed)).area))
            for i, child in enumerate(node.get('patches', [])):
                inspect(child, hierarchy + [i])
        inspect(patch, [])
        if packed_hits:
            boundary_contacts.append(dict(url=entry['url'], contacts=packed_hits))
        if rectangle.intersection(shapely.box(*bounds)).area > 0 or any(h['overlapAreaM2'] > 0 for h in packed_hits):
            overlaps.append(dict(url=entry['url'], coarseCells=patch['coarseCells'], extent=bounds,
                                 touchingPackedDescendants=packed_hits))
        consumed[str(path.relative_to(ROOT))] = digest(path.read_bytes())
        refs.append(path)
    native = [r for r in inventory['rows'] if not closed_disjoint(r['completeFourWorldBounds'], extent)]
    forms = []
    for tile in manifest['tiles']:
        path = ROOT / '3d-viewer' / tile['url']
        refs.append(path)
        consumed[str(path.relative_to(ROOT))] = digest(path.read_bytes())
        historical = inventory['currentFormTileHashes'].get(str(path.relative_to(ROOT)))
        if historical is not None:
            assert consumed[str(path.relative_to(ROOT))] == historical
        # Unlisted tiles are freshly pinned above and rechecked at the final fence.
        hits = []
        for form in read(path)['buildings']:
            points = [p for ring in form.get('rings', []) for p in ring]
            if not points:
                continue
            values = np.asarray(points)
            lo, hi = values.min(0), values.max(0)
            if not (hi[0] < extent[0] or lo[0] > extent[2] or hi[1] < extent[1] or lo[1] > extent[3]):
                hits.append(form)
        if hits:
            forms.extend(hits)
            refs.append(path)
            consumed[str(path.relative_to(ROOT))] = digest(path.read_bytes())
    assert len({f['uid'] for f in forms}) == len(forms)
    summary = dict(uids=[UID], currentNativeActors=len(inventory['rows']), regionalCoarseCells=cells,
                   regionalParentExtent=extent, overlappingPatches=overlaps, touchingPatchBoundaries=boundary_contacts,
                   simpleRootReplacementEligible=not overlaps, touchingNativeUids=[r['uid'] for r in native],
                   intersectingForms=len(forms), installationApproved=False,
                   qualification='Full coarse-cell domain and complete current actor bounds; every touching actor requires before/after checks. Boundary-only patch contacts are retained unchanged and require seam checks; positive-area packed/coarse overlap requires explicit retention. No candidate is yet constructed. Its complete packed bounds must be proven inside this domain or trigger expanded nomination before any acceptance.')
    save(DOC / 'scope.json', summary)
    save(DOC / 'native-obligations.json.gz', native)
    save(DOC / 'form-obligations.json.gz', forms)
    for key, expected in consumed.items():
        assert digest((ROOT / key).read_bytes()) == expected, key
    refs += [HERE / 'resolve-pass-indexed-parent-clipping.py', HERE / 'heritage_saved_native_bounds_binding_v1_20261014.py']
    module('stone_scope_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'complete-original-terrain-repair-scope', list(dict.fromkeys(refs)), summary)
    print(summary, flush=True)

if __name__ == '__main__':
    main()
