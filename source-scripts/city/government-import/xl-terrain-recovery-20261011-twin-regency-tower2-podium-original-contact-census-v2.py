"""Complete unchanged P/T2 edge census and cross-actor contact nominations.

Historical authentic-TIN podium positivity is a lead, not fresh acceptance. No
shared ownership, root, load transfer, visual interpretation or native approval
is inferred. Tower1 remains a separate actor and is not a bridge in this scope.
"""
import importlib.util
import json
import time
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, NATIVE_RUN, reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_shell_intersections_20261009 import rational_face, intersection_points
from exact_original_component_contacts_20261009 import contact_measure

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'xl-terrain-recovery-20261011-twin-regency-tower2-podium-original-contact-census-v2'
DOC = BASE / BATCH
INVENTORY = BASE / 'government-xl-king-cheung-95691-unchanged-installed-v1-20261011/full-xl-current-count.json'
TOWER = BASE / 'government-xl-owned-57-sequence-20261006-222465-0'
PODIUM = BASE / 'government-xl-twin-regency-podium-original-terrain-20261007'
UIDS = ['landsd/222465:0', 'landsd/223206:0']
COUNTS = [13063, 456]
SHAS = ['812a7583ff6a789ac956154a534a3548c8c6d5bfdff94338d13a79c42051a37c',
        'fd67218f6828e36899e689d071c55bf95fa0df159ac2927643be46eead74d347']


def ref(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))


def native_lookup(building):
    """Exact saved source object/CSUID match in the fixed original native run."""
    matches = []
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        profiles = con.execute('SELECT DISTINCT cache_key,sheet FROM astra_modelling.native_model_sizes WHERE run_id=%s AND model_id LIKE %s',
            (NATIVE_RUN, 'B' + building['buildingCSUID'][:10] + '%')).fetchall()
        for key, sheet in profiles:
            record = con.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',
                (NATIVE_RUN, key)).fetchone()
            assert record is not None
            for model in record[1]['models']:
                candidates = model.get('matching', {}).get('officialCandidates', [])
                if model['modelId'][1:11] == building['buildingCSUID'][:10] and any(
                    c['objectId'] == building['objectId'] and c['buildingCSUID'] == building['buildingCSUID'] for c in candidates):
                    matches.append(dict(cacheKey=key, resultSha=record[0], sheet=sheet, model=model))
    assert len(matches) == 1
    return matches[0]


def main():
    assert not DOC.exists()
    old_failure = BASE / 'xl-terrain-recovery-20261011-twin-regency-tower2-podium-original-contact-census-v1'
    refs = [ref(Path(__file__)), ref(INVENTORY),
            ref(HERE / 'xl-terrain-recovery-20261011-twin-regency-tower2-podium-original-contact-census-v1.py'),
            ref(old_failure / 'failed-run.log'), ref(old_failure / 'failed-run.json')]
    inventory = read(INVENTORY)
    assert inventory['counts'] == dict(installedVerified=228, remaining=293, total=521)
    fixed = next(r for r in inventory['rows'] if r['uid'] == UIDS[0])
    assert fixed['installedVerified'] is False and fixed['indexedSourceSHA256'] == SHAS[0]
    # Full saved actor records, no new live form or mutable catalogue capture.
    source_rows = [next(r for r in read(folder / 'selection.json.gz')['rows'] if r['uid'] == uid)
                   for folder, uid in zip([TOWER, PODIUM], UIDS)]
    for folder in [TOWER, PODIUM]:
        for name in ['selection.json.gz', 'result.json', 'metrics.json', 'foundation.json', 'neighbour-inputs.json.gz']:
            path = folder / name
            assert path.is_file()
            refs.append(ref(path))
    helpers = [HERE / n for n in ['exact_packed_world_geometry_20261009.py',
        'exact_packed_world_bounds_v3_20261010.py', 'exact_original_shared_edge_component_census_v2_20261011.py',
        'exact_original_shell_intersections_20261009.py', 'exact_original_component_contacts_20261009.py',
        'xl-popcorn-source-investigations-checkpoints-20261009.py']]
    refs.extend(ref(p) for p in helpers)
    sources = []; worlds = []; inventories = []; bodies = []; offset = 0
    for row, uid, count, expected in zip(source_rows, UIDS, COUNTS, SHAS):
        native = native_lookup(row['source']['building'])
        asset = ROOT / row['candidate']['path']; raw = asset.read_bytes()
        assert row['sourceSHA256'] == digest(raw) == native['model']['asset']['sha256'] == expected
        assert native['model']['triangles'] == count and native['model']['modelId'] == row['modelId']
        world = decode_original_world_triangles(raw); assert world.shape == (count, 3, 3)
        assert np.isfinite(world).all()
        exact = census(world, list(range(count)))
        sources.append(dict(uid=uid, asset=ref(asset), native=native,
                            originalSavedBuilding=row['source']['building'], wholePOSITION=packed_world_bounds(raw)))
        inventories.append(dict(uid=uid, census=exact)); worlds.append(world); refs.append(ref(asset))
        for ids in exact['sharedEdgeConnectedComponents']:
            part = world[ids]
            bodies.append(dict(actorUID=uid, actorLocalFaces=ids,
                globalOriginalFaces=[offset + i for i in ids],
                bounds=[part.min(axis=(0, 1)).tolist(), part.max(axis=(0, 1)).tolist()]))
        offset += count
    tri = np.concatenate(worlds); assert len(tri) == 13519
    members = {f: i for i, body in enumerate(bodies) for f in body['globalOriginalFaces']}
    zeros = [f for f in range(len(tri)) if f not in members]
    assert len(members) + len(zeros) == len(tri)
    tower_ids = [i for i, b in enumerate(bodies) if b['actorUID'] == UIDS[0]]
    podium_ids = [i for i, b in enumerate(bodies) if b['actorUID'] == UIDS[1]]
    assert len(tower_ids) == 1091 and len(inventories[0]['census']['exactNonrenderingOriginalFaces']) == 7
    lower = np.asarray([b['bounds'][0] for b in bodies]); upper = np.asarray([b['bounds'][1] for b in bodies])
    candidate_pairs = [(a, b) for a in tower_ids for b in podium_ids
        if np.all(lower[a] <= upper[b]) and np.all(lower[b] <= upper[a])]
    claim = reservations.claim('twin-source-contacts-' + str(uuid.uuid4()),
        ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
    assert claim['ok']; lease = claim['reservation']; last = time.monotonic()
    rational = {}; contacts = []; exact_tests = 0
    face_low = tri.min(axis=1); face_high = tri.max(axis=1)
    def exact(face):
        if face not in rational: rational[face] = rational_face(tri[face])
        return rational[face]
    def pulse(force=False):
        nonlocal last
        if force or time.monotonic() - last >= 20:
            assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease)
            last = time.monotonic()
    try:
        for a, b in candidate_pairs:
            found = None; right = np.asarray(bodies[b]['globalOriginalFaces'], int)
            for i in bodies[a]['globalOriginalFaces']:
                candidates = right[np.all(face_low[right] <= face_high[i], axis=1) &
                                   np.all(face_high[right] >= face_low[i], axis=1)]
                for j in candidates:
                    j = int(j); exact_tests += 1
                    points = intersection_points(exact(i), exact(j))
                    if len(points) < 2:
                        pulse()
                        continue
                    measure = contact_measure(points)
                    if measure['dimension'] > 0:
                        found = dict(components=[a, b], globalOriginalFaces=[i, j], exactContact=measure)
                        break
                    pulse()
                if found is not None: break
            if found is not None: contacts.append(found)
            pulse()
        # Independently replay every saved positive nomination, including IDs.
        for record in contacts:
            i, j = record['globalOriginalFaces']
            assert [members[i], members[j]] == record['components']
            assert contact_measure(intersection_points(exact(i), exact(j))) == record['exactContact']
        pulse(True)
        assert all(ref(ROOT / p['path']) == p for p in refs)
        assert [native_lookup(r['source']['building']) for r in source_rows] == [s['native'] for s in sources]
        result = dict(uids=UIDS, completeOriginalFaces=13519, completeSourceInputs=sources,
            completeEdgeCensuses=inventories, bodies=bodies, completeOriginalWorldSHA256=digest(tri.tobytes()),
            exactNonrenderingGlobalFacesRetainedUncredited=zeros, allSourceFacesAccounted=True,
            allCrossActorBodyPairs=len(tower_ids) * len(podium_ids),
            exactInclusiveBodyBoundsCandidates=candidate_pairs,
            strictlyDisjointCrossActorBodyPairs=len(tower_ids) * len(podium_ids) - len(candidate_pairs),
            oneExactPositiveNominationPerCrossActorBodyPair=contacts, exactFacePairsTested=exact_tests,
            completeCrossActorBodyPairContactCensus=True, withinActorContactGraphNotYetExamined=True,
            noPointOnlyContactCredit=True, noRootOrStructuralSupportCredit=True,
            noOwnershipGrouping=True, sourceOnly=True, noFreshCurrentCapture=True,
            historicalFixedInventory=ref(INVENTORY), currentAcceptance=False,
            nativeReacceptance=False, sourceGeometryChanges=0, newlyInstalled=0, evidenceRefs=refs)
        save(DOC / 'diagnostic.json.gz', result)
        spec = importlib.util.spec_from_file_location('twin_contact_freeze', helpers[-1])
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        module.freeze(BATCH, 'complete-original-twin-regency-tower2-podium-cross-body-contacts-source-only-v2',
            [ROOT / p['path'] for p in refs] + [DOC / 'diagnostic.json.gz'],
            dict(uids=UIDS, sourceOnly=True, completeOriginalFaces=13519,
                 positiveBodyPairs=len(contacts), currentAcceptance=False, newlyInstalled=0))
        print(dict(bodiesByUID={uid: len(inv['census']['sharedEdgeConnectedComponents'])
            for uid, inv in zip(UIDS, inventories)}, crossActorPositivePairs=len(contacts), exactTests=exact_tests), flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__': main()
