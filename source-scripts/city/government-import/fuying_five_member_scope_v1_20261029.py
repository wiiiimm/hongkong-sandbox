"""Private five-member whole-old-parent scope; preserve all actual actor obligations."""
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
    proof=receipts[args.patch]
    assert args.patch=='government-xl-fuying181489-five-member-boundary-contract-v2-20261029'and proof['allTerrainValidatorsPassed']and proof['allFiveEffectiveMembersVerified']
    oldpath=ROOT / proof['oldParent']['path']
    assert digest(oldpath.read_bytes())==proof['oldParent']['sha256']
    patch=read(oldpath);refs.append(oldpath)
    patches=[take(ROOT / m['candidate']['path'])for m in proof['members']]
    import fuying_whole_parent_five_boundary_v1_20261029 as boundary
    with boundary.private_validator():boundary.validate_effective_coordinated_members(patches)
    refs.append(HERE/'fuying_whole_parent_five_boundary_v1_20261029.py')
    rootpath = ROOT / '3d-viewer/city/data/terrain.json'
    root = take(rootpath)
    builder = module('selected_scope_extent', HERE / 'resolve-pass-indexed-parent-clipping.py')
    bounds = builder.extent(patch['coarseCells'], root)
    rectangle = shapely.box(*bounds)
    positions_by_node=[]
    def collect_positions(node):
        if node.get('nativeMesh'):
            positions_by_node.append(np.asarray(node['nativeMesh']['position']).reshape(-1,3))
        else:
            geo=node['meta']['georef'];x=geo['bE']-834500;z=816500-geo['bN'];xx=x+(node['w']-1)*geo['aE'];zz=z-(node['h']-1)*geo['aN']
            positions_by_node.append(np.asarray([[x,0,z],[xx,0,z],[x,0,zz],[xx,0,zz]]))
        for child in node.get('patches',[]):collect_positions(child)
    for node in patches:collect_positions(node)
    positions = np.concatenate(positions_by_node)
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
    receipt_uids=proof['uids'];target_uids=proof['completeTargetObligations']
    old=dict(url=str(oldpath.relative_to(ROOT/'3d-viewer')),sha256=proof['oldParent']['sha256'],retainedUids=patch['meta']['targetUids'])
    assert len(receipt_uids)==1 and set(target_uids)==set(receipt_uids)|set(old['retainedUids'])and set(receipt_uids).isdisjoint(old['retainedUids'])
    retention=dict(retainedUids=old['retainedUids'],allFiveEffectiveMembersVerified=True,wholeOldExtentExactlyCovered=True,unchangedSurfaceApproval=False)
    models={}
    for url in manifest['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path)
        for entry in read(path)['models']:
            assert entry['uid']not in models;models[entry['uid']]=entry
            asset=path.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256'];refs.append(asset)
    assert {r['uid']:r['sourceSHA256']for r in inventory['rows']}=={u:m['sha256']for u,m in models.items()}and len(models)==7021
    result = dict(uids=receipt_uids, currentNativeActors=len(inventory['rows']), regionalCoarseCells=patch['coarseCells'], regionalParentExtent=bounds, terrainContacts=terrain, positiveAreaTerrainOverlaps=sum(t['coarseOverlapAreaM2'] > 0 or any(c['overlapAreaM2'] > 0 for c in t['packedContacts']) for t in terrain), touchingNativeUids=[r['uid'] for r in native], intersectingForms=len(forms), installationApproved=False, qualification='Complete coarse-cell domain, closed original/literal/two-Float32 bounds and all current base forms. Every touching actor still needs regression checks; positive-area terrain overlap requires explicit retention.')
    result['hierarchicalTargetUids']=target_uids
    result['hierarchicalRetention']=retention
    result['explicitlyReplacedTerrain']=[old]
    result['unreviewedPositiveAreaTerrainOverlaps']=sum(t['url']!=old['url'] and (t['coarseOverlapAreaM2']>0 or any(c['overlapAreaM2']>0 for c in t['packedContacts'])) for t in terrain)
    result['qualification']+=' Explicitly replaced group is retained by exact child/grid proof, not silently removed. Raw positive overlap count includes the replaced original; every other positive overlap remains an obligation.'
    result['fiveTerrainMembers']=[m['candidate']for m in proof['members']]
    result['qualification']='Whole old-native extent, all five exact derived members, every BASIC footprint and all7021actual original/literal/two-Float32 closed bounds. All touching terrain/native actors remain regression obligations. No unchanged-surface, physical, identity, browser or publication approval.'

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
