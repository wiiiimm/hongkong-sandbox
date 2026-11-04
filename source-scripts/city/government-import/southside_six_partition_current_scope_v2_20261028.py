"""Bind every current BASIC form, original actor and terrain touching all six strips."""
import argparse
import sys
import uuid
from pathlib import Path

import numpy as np
import shapely

from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
import southside_partition_boundary_v1_20261028 as boundary

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-southside-six-partition-current-scope-v2-20261028'
DOC, LOCAL = BASE / BATCH, HERE / 'local' / BATCH
LEASE = LOCAL / 'reservation.json'
INVENTORY = 'government-xl-after-north-pair-current-inventory-v3-20261028'
PATCH = 'government-xl-southside-six-partition-validation-v1-20261028'


def owned():
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists()
    refs, pins, receipts = [Path(__file__), Path(boundary.__file__), Path(boundary.legacy.__file__)], {}, {}
    for batch in [INVENTORY, PATCH]:
        receipt, bound = authenticate(BASE / batch)
        receipts[batch] = receipt
        refs.append(BASE / batch / 'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha

    def take(path):
        key = str(path.relative_to(ROOT))
        assert digest(path.read_bytes()) == pins[key]
        refs.append(path)
        return read(path)

    receipt = receipts[PATCH]
    assert receipt['allSixPrivateNativeValidatorsPassed'] and receipt['allSixEffectiveMembersRequired']
    assert len(receipt['members']) == 6 and all(r['fullPrivateNativeValidatorPassed'] for r in receipt['members'])
    inventory = take(BASE / INVENTORY / 'complete-bounds.json.gz')
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = take(manifestpath)
    root = take(ROOT / '3d-viewer/city/data/terrain.json')
    builder = module('southside_partition_scope_extent', HERE / 'resolve-pass-indexed-parent-clipping.py')
    refs.append(Path(builder.__file__))
    nodes, domains, cells = [], [], {}
    for row in receipt['members']:
        name = row['member']
        # V1's validator checked final in-memory nodes but serialized only the
        # exact pre-overlap body. Reconstruct the same annotation from its
        # authenticated audit; then rerun full validation below. No geometry or
        # existing evidence is edited, and no overlap computation is repeated.
        directory = BASE / PATCH / ('strip-' + name)
        rawpath = directory / 'unapproved-terrain.json'
        node = take(rawpath)
        auditpath = directory / 'highest-surface-proof.json'
        audit = take(auditpath)
        assert audit['stagedGeometrySha256'] == digest(rawpath.read_bytes())
        assert not node['nativeMesh'].get('sourceOverlap')
        node['nativeMesh']['sourceOverlap'] = dict(
            policy='highest-native-surface',
            measuredProjectedExcessM2=audit['nativeProjectedExcessM2'],
            evidencePath=str(auditpath.relative_to(ROOT)),
            evidenceSHA256=digest(auditpath.read_bytes()))
        assert boundary.marker(node)['member'] == name
        own = shapely.box(*builder.extent(node['coarseCells'], root))
        position = np.asarray(node['nativeMesh']['position']).reshape(-1, 3)
        for values in [position, position.astype('float32').astype('float64')]:
            assert own.covers(shapely.box(float(values[:, 0].min()), float(values[:, 2].min()),
                                         float(values[:, 0].max()), float(values[:, 2].max())))
        nodes.append(node)
        domains.append(own)
        cells[name] = node['coarseCells']
    validator = module('southside_reconstructed_partition_validator', HERE.parent / 'island-detail-integration/native_terrain_validation.py')
    refs.append(Path(validator.__file__))
    with boundary.private_validator():
        boundary.legacy.validate_effective_coordinated_members(nodes)
        for node in nodes:
            validator.validate_native_mesh(node, root)
            save(DOC / 'private-nodes' / ('strip-' + boundary.marker(node)['member'] + '.json.gz'), node)
    rectangle = shapely.union_all(domains)
    assert rectangle.area == sum(d.area for d in domains), 'Partition domains overlap'
    bounds = list(rectangle.bounds)
    terrain = []
    for entry in manifest['terrainPatches']:
        path = ROOT / '3d-viewer' / entry['url']
        key = str(path.relative_to(ROOT))
        pins.setdefault(key, digest(path.read_bytes()))
        node = take(path)
        extent = builder.extent(node['coarseCells'], root)
        contacts = []

        def visit(item, hierarchy):
            if 'nativeMesh' in item:
                position = np.asarray(item['nativeMesh']['position']).reshape(-1, 3)
                values = np.concatenate([position, position.astype('float32').astype('float64')])
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
    native = [row for row in inventory['rows'] if not closed_disjoint(row['completeFourWorldBounds'], bounds)]
    forms = []
    for entry in manifest['tiles']:
        path = ROOT / '3d-viewer' / entry['url']
        assert digest(path.read_bytes()) == inventory['currentFormTileHashes'][str(path.relative_to(ROOT))]
        refs.append(path)
        for form in read(path)['buildings']:
            points = [p for ring in form.get('rings', []) for p in ring]
            if not points:
                continue
            values = np.asarray(points)
            low, high = values.min(0), values.max(0)
            if rectangle.intersects(shapely.box(float(low[0]), float(low[1]), float(high[0]), float(high[1]))):
                forms.append(form)
    assert len(forms) == len({form['uid'] for form in forms})
    result = dict(uids=[boundary.UID], currentNativeActors=len(inventory['rows']),
                  regionalCoarseCellsByMember=cells, domainWKT=rectangle.wkt,
                  regionalParentExtent=bounds, terrainContacts=terrain,
                  positiveAreaTerrainOverlaps=sum(t['coarseOverlapAreaM2'] > 0 or any(c['overlapAreaM2'] > 0 for c in t['packedContacts']) for t in terrain),
                  touchingNativeUids=[row['uid'] for row in native], intersectingForms=len(forms),
                  installationApproved=False, fullCurrentMapAcceptance=False,
                  allSixReconstructedNodesRevalidated=True,
                  qualification='Complete six-node coarse-cell domain; all current BASIC forms, four-world original actor bounds and nested terrain contacts nominated. Nomination is not regression acceptance. Every positive-area installed terrain overlap requires explicit retention; all source identity, physical and browser gates remain.')
    save(DOC / 'scope.json', result)
    save(DOC / 'native-obligations.json.gz', native)
    save(DOC / 'form-obligations.json.gz', forms)
    for path in set(refs):
        key = str(path.relative_to(ROOT))
        if key in pins:
            assert digest(path.read_bytes()) == pins[key]
        if key in inventory['currentFormTileHashes']:
            assert digest(path.read_bytes()) == inventory['currentFormTileHashes'][key]
    assert reservations.owns(lease)
    refs.append(HERE / 'heritage_saved_native_bounds_binding_v1_20261014.py')
    module('southside_six_partition_current_scope_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'complete-current-six-strip-original-terrain-repair-scope', list(dict.fromkeys(refs)), result)
    print(dict(currentActors=len(inventory['rows']), forms=len(forms), nativeActors=len(native),
               positiveAreaTerrainOverlaps=result['positiveAreaTerrainOverlaps']), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    if args.owned:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    claim = reservations.claim('southside-six-partition-current-scope-' + str(uuid.uuid4()),
                               ['building:' + boundary.UID], batch=BATCH, ttl=3600)
    assert claim['ok']
    execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])


if __name__ == '__main__':
    main()
