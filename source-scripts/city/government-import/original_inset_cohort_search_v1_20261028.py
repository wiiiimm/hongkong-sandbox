"""Bounded construction-mask search; every model remains a required co-import.

Tests exactly the existing union/1m-core/3m-return rule. This is not model
screening, physical acceptance, terrain generation or a skip/import decision.
"""
import argparse
import itertools
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


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--runtime', required=True)
    p.add_argument('--candidate-uid', action='append', required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    pool = sorted(a.candidate_uid)
    assert 8 <= len(pool) == len(set(pool)) <= 10
    base = ROOT/'docs/astra-city/government-import'
    doc, local = base/a.batch, HERE/'local'/a.batch
    leasepath = local/'reservation.json'
    prior = base/a.runtime
    _, pins = authenticate(prior)
    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        return read(path)
    selection = take(prior/'selection.json.gz')['rows']
    assert set(pool) <= {r['uid'] for r in selection}
    if not a.owned:
        assert not doc.exists() and not local.exists()
        claim = reservations.claim('original-inset-cohort-search-'+str(uuid.uuid4()),
            sorted('building:'+r['uid'] for r in selection), batch=a.batch, ttl=3600)
        assert claim['ok']
        return execute_reserved(claim['reservation'], leasepath, [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(leasepath)
    assert reservations.owns(lease) and not doc.exists()
    geometrypath = HERE/'local'/a.runtime/'runtime-geometry.json.gz'
    geometry = {r['uid']: r for r in take(geometrypath)['rows']}
    assert set(geometry) == {r['uid'] for r in selection}
    refs = [Path(__file__), HERE/'exact_packed_world_geometry_20261009.py', prior/'result.json', prior/'selection.json.gz', geometrypath]
    projections, hashes = {}, {}
    for row in selection:
        uid = row['uid']
        path = ROOT/row['candidate']['path']
        raw = path.read_bytes()
        assert digest(raw) == row['sourceSHA256'] == geometry[uid]['sourceSHA256']
        refs.append(path)
        original = decode_original_world_triangles(raw)
        g = geometry[uid]
        literal = np.asarray(g['position']).reshape(-1, 3)[np.asarray(g['index']).reshape(-1, 3)]
        assert len(original) == len(literal) == row['triangles']
        projections[uid] = {mode: shapely.union_all([shapely.MultiPoint(face[:, [0, 2]]).convex_hull for face in tri])
                            for mode, tri in [('original', original), ('literal', literal)]}
        hashes[uid] = row['sourceSHA256']
    complete = shapely.union_all([g for pair in projections.values() for g in pair.values()])
    tested, passing = 0, []
    for cohort in itertools.combinations(pool, 8):
        core = shapely.union_all([projections[u]['literal'] for u in cohort]).buffer(1, join_style='mitre')
        tested += 1
        if core.covers(complete):
            outer = core.buffer(3, join_style='mitre')
            passing.append(dict(insetCohort=list(cohort), outerAreaM2=outer.area,
                                coreBounds=list(core.bounds), outerBounds=list(outer.bounds)))
    passing.sort(key=lambda r: (r['outerAreaM2'], r['insetCohort']))
    save(doc/'passing-cohorts.json', passing)
    result = dict(uids=sorted(projections), sourceSHA256ByUid=hashes, candidatePool=pool,
        testedCohorts=tested, passingCohorts=len(passing), proposedCohort=passing[0] if passing else None,
        sourceGeometryChanges=0, installationApproved=False,
        qualification='Every complete original/literal primitive, including projected lines and points, must be covered by the unchanged construction core. Search only this explicit bounded pool; no global impossibility inferred. Minimum return area chooses between fully covering masks, never between building quality or enhancement decisions. Independent preflight, full field construction, boundaries, retained actors, physical and visual checks still required.')
    save(doc/'summary.json', result)
    assert reservations.owns(lease)
    module('bounded_original_inset_cohort_search_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'bounded-eight-member-construction-mask-search', list(dict.fromkeys(refs)), result)
    print(dict(tested=tested, passing=len(passing), proposed=passing[0] if passing else None), flush=True)


if __name__ == '__main__':
    main()
