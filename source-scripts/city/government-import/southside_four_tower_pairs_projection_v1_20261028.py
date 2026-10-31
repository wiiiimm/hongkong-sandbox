"""Complete paired original-source projection diagnostics; no identity exceptions."""
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
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-southside-four-tower-pairs-projection-v1-20261028'
DOC, LOCAL = BASE / BATCH, HERE / 'local' / BATCH
LEASE = LOCAL / 'reservation.json'
CAP = BASE / 'government-xl-southside-project-original-recovery-v1-20261028'
IDENTITY = BASE / 'government-xl-southside-project-original-identities-v1-20261028'
PAIRS = {'La Marina 2': ['landsd/311761:0', 'landsd/311762:0'],
         'Southland 2': ['landsd/311759:0', 'landsd/311763:0'],
         'Southland 1': ['landsd/330243:0', 'landsd/330244:0'],
         'La Montagne 2': ['landsd/315027:0', 'landsd/315028:0']}


def owned():
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists()
    _, pins = authenticate(CAP)
    _, identity_pins = authenticate(IDENTITY)
    path = CAP / 'selection.json.gz'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    selected = {r['uid']: r for r in read(path)['rows']}
    wanted = {u for pair in PAIRS.values() for u in pair}
    assert {'building:' + u for u in wanted} <= set(lease['resources'])
    refs = [Path(__file__), CAP/'result.json', IDENTITY/'result.json', path, HERE/'exact_packed_world_geometry_20261009.py']
    projections, targets, sources, raw = {}, {}, {}, {}
    for uid in sorted(wanted):
        row = selected[uid]
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256']
        refs.append(asset)
        tri = decode_original_world_triangles(asset.read_bytes())
        assert len(tri) == row['triangles']
        projections[uid] = shapely.union_all(shapely.polygons(tri[:, :, [0, 2]]))
        form = row['source']['building']
        tile = ROOT / '3d-viewer' / row['source']['tile']
        assert digest(tile.read_bytes()) == row['source']['tileSHA256']
        assert next(f for f in read(tile)['buildings'] if f['uid'] == uid) == form
        refs.append(tile)
        shape = shapely.GeometryCollection()
        for ring in form['rings']:
            shape = shape.symmetric_difference(shapely.Polygon(ring))
        assert shape.is_valid and shape.area > 0
        targets[uid] = shape
        sources[uid] = dict(uid=uid, name=form.get('name'), parent=form.get('parent'),
                            buildingCSUID=form['buildingCSUID'], sourceSHA256=row['sourceSHA256'],
                            originalWorldSHA256=digest(tri.astype('<f8').tobytes()), completeFaces=len(tri))
        identity = IDENTITY / uid.split('/')[1] / 'identity.json'
        assert digest(identity.read_bytes()) == identity_pins[str(identity.relative_to(ROOT))]
        refs.append(identity)
        raw[uid] = read(identity)
    results = []
    for label, uids in PAIRS.items():
        combined = shapely.union_all([projections[u] for u in uids])
        target = shapely.union_all([targets[u] for u in uids])
        rows = []
        for uid in uids:
            own, form = projections[uid], targets[uid]
            rows.append(dict(uid=uid, rawIndividualIdentityPassed=raw[uid]['passed'], rawIndividualReasons=raw[uid]['reasons'],
                             ownMissingM2=form.difference(own).area, pairMissingM2=form.difference(combined).area,
                             ownCoverage=own.intersection(form).area/form.area, pairCoverage=combined.intersection(form).area/form.area,
                             ownExcessOutsidePairTargetsM2=own.difference(target).area))
        results.append(dict(label=label, uids=uids, rows=rows, combinedMissingM2=target.difference(combined).area,
                            combinedExcessM2=combined.difference(target).area, combinedTargetM2=target.area))
    result = dict(uids=sorted(wanted), pairs=results, sources=sources,
                  rawIndividualIdentityFailuresPreserved=True, identityAccepted=False, physicalAccepted=False,
                  installationApproved=False, sourceGeometryChanges=0,
                  qualification='Four explicitly named current tower-pair hypotheses, each tested using complete original face projections and exact current target polygons. Podium and other project projections excluded to avoid hiding missing tower coverage. Pair labels are diagnostic grouping, not approved compound ownership, an identity exception, support or installation acceptance. All individual raw negatives and source bytes retained.')
    save(DOC/'summary.json', result)
    assert reservations.owns(lease)
    module('southside_four_tower_pair_projections_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'four-complete-original-tower-pair-projection-diagnostics', list(dict.fromkeys(refs)), result)
    print(results, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    if args.owned:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    claim = reservations.claim('southside-four-tower-pairs-' + str(uuid.uuid4()),
                               ['building:' + u for u in sorted({u for pair in PAIRS.values() for u in pair})], batch=BATCH, ttl=3600)
    assert claim['ok']
    execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])


if __name__ == '__main__':
    main()
