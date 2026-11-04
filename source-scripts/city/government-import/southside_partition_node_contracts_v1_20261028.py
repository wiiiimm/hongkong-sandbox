"""Regenerate each private strip's overlap proof; retain unapproved boundary results.

No parent overlap approval is copied. No boundary adapter, source model, public
terrain, acceptance state or publication gate is changed by this diagnostic.
"""
import argparse
import sys
import uuid
from pathlib import Path

import numpy as np
import shapely

from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-southside-partition-node-contracts-v1-20261028'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
LEASE = LOCAL / 'reservation.json'
SEAMS = 'government-xl-southside-partition-existing-seams-v1-20261028'
TWINS = 'government-xl-southside-partition-boundary-twins-v1-20261028'
UID = 'landsd/315025:0'


def owned():
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists()
    refs = [Path(__file__)]
    pins = {}
    for batch in [SEAMS, TWINS]:
        _, bound = authenticate(BASE / batch)
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha
        refs.append(BASE / batch / 'result.json')

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    twins = take(BASE / TWINS / 'summary.json')
    assert twins['allLegacyNegativeVerticesHaveExactOppositeSourceFaceTwins']
    assert twins['legacyNegativeVertices'] == 22
    parent_path = ROOT / '3d-viewer/city/data/terrain.json'
    parent = read(parent_path)
    refs.append(parent_path)
    producer = module('southside_child_overlap_producer', HERE / 'sham_shui_po_pool_shared_terrain_v2_20261016.py')
    validator = module('southside_child_original_validator', HERE.parent / 'island-detail-integration/native_terrain_validation.py')
    refs.extend([Path(producer.__file__), Path(validator.__file__)])
    rows = []
    for strip in range(6):
        assert reservations.owns(lease)
        path = HERE / 'local' / SEAMS / ('strip-' + str(strip) + '-unbound.json')
        node = take(path)
        assert not node['nativeMesh'].get('sourceOverlap')
        assert not node['nativeMesh'].get('source', {}).get('coordinatedBoundary')
        position_before = digest(str(node['nativeMesh']['position']).encode())
        index_before = digest(str(node['nativeMesh']['index']).encode())
        sources = [Path(__file__), path, parent_path]
        for source in node['meta']['source']['nativeSources']:
            p = ROOT / source['path']
            assert digest(p.read_bytes()) == source['sha256']
            sources.append(p)
            if p.suffix == '.gltf':
                sources.extend(q for q in p.parent.iterdir() if q.suffix == '.bin')
        sources = list(dict.fromkeys(sources))
        refs.extend(sources)
        producer.DOC = DOC / ('strip-' + str(strip))
        producer.overlap_proof(node, sources)
        tri = np.asarray(node['nativeMesh']['position'], dtype=np.float32).astype(float).reshape(-1, 3)[np.asarray(node['nativeMesh']['index']).reshape(-1, 3)]
        polygons = shapely.polygons(tri[:, :, [0, 2]])
        valid = shapely.area(polygons) > 1e-10
        union = shapely.union_all(polygons[valid])
        g = node['meta']['georef']
        x0, z0 = g['bE'] - 834500, 816500 - g['bN']
        extent = shapely.box(x0, z0, x0 + (node['w'] - 1) * g['aE'], z0 - (node['h'] - 1) * g['aN'])
        coverage_gap = union.symmetric_difference(extent).area
        tolerance = max(.001, extent.area * 1e-7)
        assert coverage_gap < tolerance, 'Child requires its own coverage investigation'
        assert len(tri) <= 25000
        assert digest(str(node['nativeMesh']['position']).encode()) == position_before
        assert digest(str(node['nativeMesh']['index']).encode()) == index_before
        # This is the complete unchanged validator, not a substituted height-only
        # validator. A root-join failure remains a failure in the saved evidence.
        try:
            validator.validate_native_mesh(node, parent)
            passed, error = True, None
        except AssertionError as exc:
            passed, error = False, str(exc)
        audit_path = producer.DOC / 'highest-surface-proof.json'
        audit = read(audit_path) if audit_path.exists() else None
        out = producer.DOC / 'private-node.json.gz'
        save(out, node)
        row = dict(strip=strip, faces=len(tri), coverageGapM2=coverage_gap,
                   coverageToleranceM2=tolerance, coveragePassed=True,
                   runtimeNodeBudgetPassed=True, overlapProofRegenerated=bool(audit),
                   positiveOverlapPairs=len(audit['float32HighestRayAgreement']['rows']) if audit else 0,
                   maximumHeightEquationErrorM=audit['float32HighestRayAgreement']['maxError'] if audit else 0,
                   unchangedNativeValidatorPassed=passed, unchangedNativeValidatorFailure=error,
                   sourceGeometryChanged=False, privateNode=str(out.relative_to(ROOT)))
        rows.append(row)
        print(row, flush=True)
    result = dict(uids=[UID], strips=rows, allSixCoverageAndBudgetChecksPassed=True,
                  allSixUnchangedNativeValidatorsPassed=all(r['unchangedNativeValidatorPassed'] for r in rows),
                  sourceGeometryChanges=0, productionGuardChanges=False,
                  identityAccepted=False, physicalAccepted=False, installationApproved=False,
                  qualification='Fresh per-child overlap proofs and exact rectangle coverage; complete original native validator results retained. No internal partition-boundary adapter, installation or acceptance. The original parent overlap approval was not transferred.')
    save(DOC / 'summary.json', result)
    assert reservations.owns(lease)
    module('southside_partition_node_contracts_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'fresh-six-strip-coverage-budget-overlap-with-unchanged-boundary-results',
        list(dict.fromkeys(refs)), result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    if args.owned:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    claim = reservations.claim('southside-child-node-contracts-' + str(uuid.uuid4()),
                               ['building:' + UID], batch=BATCH, ttl=3600)
    assert claim['ok']
    execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])


if __name__ == '__main__':
    main()
