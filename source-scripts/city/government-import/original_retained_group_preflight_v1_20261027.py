"""Find exact live terrain groups and disjoint child domains; diagnostic only."""
import argparse
import json
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'uid']:
        parser.add_argument('--' + key, required=True)
    args = parser.parse_args()
    base = ROOT / 'docs/astra-city/government-import'
    out = base / args.batch
    assert args.batch.startswith('government-xl-') and '/' not in args.batch and not out.exists()
    _, pins = authenticate(base / args.runtime)
    selection_path = base / args.runtime / 'selection.json.gz'
    assert digest(selection_path.read_bytes()) == pins[str(selection_path.relative_to(ROOT))]
    selection = read(selection_path)
    row = next(r for r in selection['rows'] if r['uid'] == args.uid)
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest_path.read_bytes()) == selection['manifestSHA256']
    root_path = ROOT / '3d-viewer/city/data/terrain.json'
    root = read(root_path)
    builder_path = HERE / 'resolve-pass-indexed-parent-clipping.py'
    builder = module('retained_group_preflight_builder', builder_path)
    low, high = row['native']['model']['worldBounds']
    footprint_bounds = shapely.box(low[0], low[2], high[0], high[2])
    refs = [__file__, selection_path, base / args.runtime / 'result.json',
            manifest_path, root_path, builder_path]
    contacts = []
    for entry in read(manifest_path)['terrainPatches']:
        path = ROOT / '3d-viewer' / entry['url']
        node = read(path)
        extent = builder.extent(node['coarseCells'], root)
        if not shapely.box(*extent).intersects(footprint_bounds):
            continue
        refs.append(path)
        contact = dict(url=entry['url'], sha256=digest(path.read_bytes()), extent=extent,
                       nativeMesh=bool(node.get('nativeMesh')), children=len(node.get('patches', [])))
        if not node.get('nativeMesh'):
            cells = builder.rectangle_for(row['native']['model']['worldBounds'], node)
            bounds = builder.extent(cells, node)
            overlaps = [i for i, child in enumerate(node.get('patches', []))
                        if not (cells[2] <= child['coarseCells'][0] or cells[0] >= child['coarseCells'][2]
                                or cells[3] <= child['coarseCells'][1] or cells[1] >= child['coarseCells'][3])]
            contact.update(childCells=cells, childBounds=bounds, overlappingChildren=overlaps,
                           childInsideGroup=0 <= cells[0] < cells[2] < node['w'] and 0 <= cells[1] < cells[3] < node['h'])
        contacts.append(contact)
    scope = dict(uids=[args.uid], terrainContacts=contacts)
    save(out / 'scope.json', scope)
    result = dict(**scope, sourceSHA256=row['sourceSHA256'], installationApproved=False,
                  publication=False, sourceGeometryChanges=0,
                  qualification='Exact current group/child-cell preflight only. No terrain construction, coverage waiver, placement approval or installation.')
    result = json.loads(json.dumps(result))
    module('retained_group_preflight_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        args.batch, 'original-live-terrain-group-child-domain-preflight',
        [__import__('pathlib').Path(p) for p in refs], result)
    print(contacts, flush=True)


if __name__ == '__main__':
    main()
