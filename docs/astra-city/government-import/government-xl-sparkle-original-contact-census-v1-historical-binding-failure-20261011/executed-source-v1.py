"""Complete unchanged Sparkle/P edge census and cross-actor contact nominations.

Historical podium whole-foundation positivity is a lead, not fresh acceptance. No
shared ownership, root, load transfer, visual interpretation or native approval
is inferred. Current BASIC107780 remains a foreign actor and is not a bridge in this scope.
"""
import importlib.util
import json
import time
import subprocess
import sys
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
BATCH = 'xl-terrain-recovery-20261011-sparkle-tower-podium-original-contact-census-v1'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
INVENTORY = BASE / 'government-xl-twin-regency-evangel-three-atomic-installed-v1-20261011/full-xl-current-count.json'
HISTORICAL = BASE / 'government-xl-georef-sparkle-heya-original-supports-20261008'
PODIUM_PHYSICAL = BASE / 'government-xl-georef-support-podium-sequence-20261008-228000-0'
UIDS = ['landsd/242198:0', 'landsd/228000:0']
COUNTS = [12875, 6806]
SHAS = ['5dcc709e25d0801ae3e2cef4a59c214babfa2adc4de42ce5fd956e649315c3f3',
        '7429ad91552966b7e5ab6717626cb8e84d195da698140bcaf0b57ce890b89800']


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


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease)
    assert not DOC.exists()
    refs = [ref(Path(__file__)), ref(INVENTORY), ref(LOCAL / 'reservation.json'),
            ref(HERE.parent / 'shared-modelling/reservations.py')]
    inventory = read(INVENTORY)
    assert inventory['counts'] == dict(installedVerified=232, remaining=289, total=521)
    fixed = next(r for r in inventory['rows'] if r['uid'] == UIDS[0])
    assert fixed['installedVerified'] is False and fixed['indexedSourceSHA256'] == SHAS[0]
    assert not any(r['uid'] == UIDS[1] for r in inventory['rows'])
    # Recovered source rows and old failures are historical input evidence only.
    # No prior contact-layer sample supplies an edge/root/support credit here.
    source_rows = [next(r for r in read(HISTORICAL / 'support-inputs.json')['sources'] if r['uid'] == uid) for uid in UIDS]
    historical_receipt = read(HISTORICAL / 'result.json')
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (historical_receipt['jobId'],)).fetchone() == ('complete', historical_receipt)
    for name in ['support-inputs.json', 'support-checks.json.gz', 'support-failure-surfaces.json.gz']:
        pin = ref(HISTORICAL / name); assert pin in historical_receipt['evidenceRefs']; refs.append(pin)
    refs.append(ref(HISTORICAL / 'result.json'))
    for name in ['result.json', 'selection.json.gz', 'foundation.json', 'neighbour-checks.json']:
        refs.append(ref(PODIUM_PHYSICAL / name))
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
    tri = np.concatenate(worlds); assert len(tri) == 19681
    members = {f: i for i, body in enumerate(bodies) for f in body['globalOriginalFaces']}
    zeros = [f for f in range(len(tri)) if f not in members]
    assert len(members) + len(zeros) == len(tri)
    tower_ids = [i for i, b in enumerate(bodies) if b['actorUID'] == UIDS[0]]
    podium_ids = [i for i, b in enumerate(bodies) if b['actorUID'] == UIDS[1]]
    assert tower_ids and podium_ids
    assert set(members) | set(zeros) == set(range(19681)) and not set(members) & set(zeros)
    lower = np.asarray([b['bounds'][0] for b in bodies]); upper = np.asarray([b['bounds'][1] for b in bodies])
    candidate_pairs = [(a, b) for a in tower_ids for b in podium_ids
        if np.all(lower[a] <= upper[b]) and np.all(lower[b] <= upper[a])]
    assert reservations.owns(lease)
    last = time.monotonic()
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
        result = dict(uids=UIDS, completeOriginalFaces=19681, completeSourceInputs=sources,
            completeEdgeCensuses=inventories, bodies=bodies, completeOriginalWorldSHA256=digest(tri.tobytes()),
            exactNonrenderingGlobalFacesRetainedUncredited=zeros, allSourceFacesAccounted=True,
            allCrossActorBodyPairs=len(tower_ids) * len(podium_ids),
            exactInclusiveBodyBoundsCandidates=candidate_pairs,
            strictlyDisjointCrossActorBodyPairs=len(tower_ids) * len(podium_ids) - len(candidate_pairs),
            oneExactPositiveNominationPerCrossActorBodyPair=contacts, exactFacePairsTested=exact_tests,
            completeCrossActorBodyPairContactCensus=True, withinActorContactGraphNotYetExamined=True,
            noPointOnlyContactCredit=True, noRootOrStructuralSupportCredit=True,
            noOwnershipGrouping=True, sourceOnly=True, noFreshCurrentCapture=True,
            fixedInstalledMembershipInventory=ref(INVENTORY), historicalSupportFailuresRetained=ref(HISTORICAL / 'support-failure-surfaces.json.gz'), historicalPodiumWholeFoundationAndForeignFailuresRetained=ref(PODIUM_PHYSICAL / 'result.json'), currentAcceptance=False,
            nativeReacceptance=False, sourceGeometryChanges=0, newlyInstalled=0, evidenceRefs=refs)
        save(DOC / 'diagnostic.json.gz', result)
        spec = importlib.util.spec_from_file_location('sparkle_contact_freeze', helpers[-1])
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        module.freeze(BATCH, 'complete-original-sparkle-tower-podium-cross-body-contacts-source-only-v1',
            [ROOT / p['path'] for p in refs] + [DOC / 'diagnostic.json.gz'],
            dict(uids=UIDS, sourceOnly=True, completeOriginalFaces=19681,
                 positiveBodyPairs=len(contacts), currentAcceptance=False, newlyInstalled=0))
        print(dict(bodiesByUID={uid: len(inv['census']['sharedEdgeConnectedComponents'])
            for uid, inv in zip(UIDS, inventories)}, crossActorPositivePairs=len(contacts), exactTests=exact_tests), flush=True)
    finally:
        # The maintained canonical supervisor owns release, including exceptions.
        pass


def main():
    if '--owned' in sys.argv:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    claim = reservations.claim('sparkle-source-contacts-' + str(uuid.uuid4()),
        ['building:' + uid for uid in UIDS] + ['immutable-source-proof:' + BATCH],
        batch=BATCH, ttl=3600)
    assert claim['ok']
    save(LOCAL / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'),
        'run', '--lease-file', str(LOCAL / 'reservation.json'), '--ttl', '3600', '--',
        sys.executable, __file__, '--owned'], cwd=ROOT, check=True)


if __name__ == '__main__': main()
