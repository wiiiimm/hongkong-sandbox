"""Attribute Ocean Centre's inherited gap and nested terrain obligations exactly."""
import json
from pathlib import Path
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base = ROOT / 'docs/astra-city/government-import'
    prefix = 'government-xl-after-waterfront-ocean234188-'
    batch = prefix + 'inherited-group-context-v1-20261027'
    out = base / batch
    assert not out.exists()
    refs = [Path(__file__), ROOT / '3d-viewer/city/world.js']
    receipts = {}
    for suffix in ['parent-coverage-v1-20261027', 'retained-group-preflight-v1-20261027']:
        folder = base / (prefix + suffix)
        receipt, pins = authenticate(folder)
        for name, sha in pins.items():
            assert digest((ROOT / name).read_bytes()) == sha
        refs.append(folder / 'result.json')
        receipts[suffix] = receipt
    diagnostic = receipts['parent-coverage-v1-20261027']
    contact = receipts['retained-group-preflight-v1-20261027']['terrainContacts'][0]
    path = ROOT / '3d-viewer' / contact['url']
    assert digest(path.read_bytes()) == contact['sha256']
    refs.append(path)
    group = read(path)
    geo = group['meta']['georef']
    width, height = group['w'], group['h']
    domain = shapely.box(*diagnostic['domainBounds'])
    zero_cells = []
    for r in range(height - 1):
        for c in range(width - 1):
            a = r * width + c
            if any(group['elev'][i] for i in [a, a+1, a+width, a+width+1]):
                continue
            x = geo['bE'] + c * geo['aE'] - 834500
            z = 816500 - geo['bN'] - r * geo['aN']
            box = shapely.box(x, z, x+geo['aE'], z-geo['aN'])
            if box.intersection(domain).area:
                zero_cells.append(box.intersection(domain))
    zero_union = shapely.union_all(zero_cells)
    missing_path = base / (prefix+'parent-coverage-v1-20261027') / 'raw-missing.geojson'
    refs.append(missing_path)
    missing = shapely.from_geojson(json.dumps(read(missing_path)))
    largest = max(shapely.get_parts(missing), key=lambda p:p.area)
    assert largest.area == 1425
    assert largest.difference(zero_union).area < 1e-8
    child_domain = shapely.box(*contact['childBounds'])
    nested = []
    for index in contact['overlappingChildren']:
        child = group['patches'][index]
        c0,r0,c1,r1 = child['coarseCells']
        bounds = [geo['bE']+c0*geo['aE']-834500,816500-geo['bN']-r0*geo['aN'],
                  geo['bE']+c1*geo['aE']-834500,816500-geo['bN']-r1*geo['aN']]
        nested.append(dict(hierarchy=[index], id=child['id'], targetUids=child['meta']['targetUids'],
                           coarseBounds=bounds, overlapM2=child_domain.intersection(shapely.box(*bounds)).area,
                           nativeMesh=bool(child.get('nativeMesh'))))
    result = dict(uids=['landsd/234188:0'], currentGroupURL=contact['url'], currentGroupSHA256=contact['sha256'],
                  currentChildren=len(group['patches']), inheritedLargestGapAreaM2=largest.area,
                  inheritedGapCoveredByExistingAllZeroGridCells=True,
                  nestedTerrainObligations=nested, disjointChildRouteEligible=not nested,
                  installationApproved=False, physicalAcceptance=False, publication=False,
                  qualification='The 1425m2 inherited gap is wholly covered by grid cells omitted by the existing renderer all-zero elevation rule. This is not source corruption or numerical roundoff. A simple disjoint child is ineligible: nested original terrain obligations must be retained and revalidated. No coverage waiver, terrain edit, or permanent rejection.')
    save(out / 'summary.json', result)
    module('ocean_inherited_group_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        batch, 'exact-inherited-zero-grid-gap-and-nested-child-obligations', refs, result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
