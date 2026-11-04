"""Bind unchanged private terrain to an explicit actor subset; no acceptance.

All current affected forms remain leased and require fresh neighbour checks.
Only target metadata and its dependent overlap receipt change. The complete
terrain mesh, grid, water mask, source provenance and existing validators remain.
"""
import argparse
import copy
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'patch', 'resources-plan']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--uid', action='append', required=True)
    parser.add_argument('--owned', action='store_true')
    a = parser.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.patch])
    base = ROOT / 'docs/astra-city/government-import'
    planpath = (ROOT / a.resources_plan).resolve()
    assert planpath.is_relative_to(base)
    plan = read(planpath)
    wanted = set(a.uid)
    assert 0 < len(wanted) == len(a.uid) and wanted <= set(plan['uids'])
    resources = set(plan['resources'])
    assert {'terrain:city/data/terrain.json'} | {'building:' + u for u in plan['uids']} <= resources
    out, local = base / a.batch, HERE / 'local' / a.batch
    assert not out.exists()
    control = local / 'reservation.json'
    if not a.owned:
        assert not local.exists()
        claim = reservations.claim('original-terrain-target-subset-' + str(uuid.uuid4()),
                                   sorted(resources), batch=a.batch, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], control,
                                [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(control)
    assert reservations.owns(lease) and set(lease['resources']) == resources
    receipt, pins = authenticate(base / a.patch)
    assert receipt['status'] == 'private-terrain-validator-passed'
    path = ROOT / receipt['candidate']['path']
    assert digest(path.read_bytes()) == receipt['candidate']['sha256'] == pins[str(path.relative_to(ROOT))]
    before = read(path)
    assert set(before['meta']['targetUids']) == set(receipt['uids']) == set(plan['uids'])
    assert wanted < set(receipt['uids'])
    patch = copy.deepcopy(before)
    patch['meta']['targetUids'] = sorted(wanted)
    refs = [Path(__file__), planpath, base / a.patch / 'result.json', path]
    for p, value in pins.items():
        assert digest((ROOT / p).read_bytes()) == value
        refs.append(ROOT / p)
    # Overlap evidence binds all metadata, so regenerate it honestly even though
    # every position/index and elevation value remains byte-for-byte equivalent.
    overlap = module('target_subset_overlap', HERE / 'sham_shui_po_pool_shared_terrain_v2_20261016.py')
    overlap.DOC = out
    overlap.overlap_proof(patch, refs)
    old_body, new_body = copy.deepcopy(before), copy.deepcopy(patch)
    old_body['meta']['targetUids'] = new_body['meta']['targetUids']
    old_body['nativeMesh'].pop('sourceOverlap', None)
    new_body['nativeMesh'].pop('sourceOverlap', None)
    assert old_body == new_body, 'Only actor target metadata may change'
    parentpath = ROOT / '3d-viewer' / patch['meta']['parentTerrain']
    assert digest(parentpath.read_bytes()) == patch['meta']['parentSha256']
    builder = module('target_subset_validator', HERE / 'resolve_pass_indexed_parent_clipping_v2.py')
    builder.validate_patch(patch, read(parentpath))
    destination = local / 'candidate-terrain.json'
    save(destination, patch)
    summary = dict(uids=sorted(wanted), candidate=dict(path=str(destination.relative_to(ROOT)), sha256=digest(destination.read_bytes())),
                   previousTargetUids=receipt['uids'], terrainGeometryExactlyUnchanged=True,
                   sourceGeometryChanges=0, sourcePoseChanges=0, terrainTriangles=len(patch['nativeMesh']['index']) // 3,
                   status='private-terrain-validator-passed', replacedNativeTerrain=receipt.get('replacedNativeTerrain', []),
                   retainedNativeTerrainTargets=receipt.get('retainedNativeTerrainTargets', []),
                   physicalAcceptance=False, installationApproved=False, publication=False,
                   qualification='Target metadata subset only. Complete parent/grid/water/native arrays and source provenance unchanged; overlap evidence regenerated and existing terrain validator passed. Removed target actors remain current BASIC forms and require full fresh regression checks; no original-source identity or acceptance transferred.')
    save(out / 'summary.json', summary)
    assert reservations.owns(lease)
    refs.extend([destination, parentpath, HERE / 'sham_shui_po_pool_shared_terrain_v2_20261016.py',
                 HERE / 'resolve_pass_indexed_parent_clipping_v2.py'])
    module('target_subset_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'exact-unchanged-terrain-explicit-target-subset-no-acceptance', list(dict.fromkeys(refs)), summary)


if __name__ == '__main__':
    main()
