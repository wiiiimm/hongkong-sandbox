"""Complete unchanged within-actor original body contacts; no root credit.

Uses the fenced whole P/T2 census and every original facet. Cached cross-actor
contacts retain their exact producing receipt; new within-actor positives are
independently recomputed/replayed. Connectivity is nomination evidence only.
"""
import importlib.util
import time
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face, intersection_points
from exact_original_component_contacts_20261009 import contact_measure

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'xl-terrain-recovery-20261011-twin-regency-complete-internal-original-contact-graph-v1'
DOC = BASE / BATCH
INPUT = BASE / 'xl-terrain-recovery-20261011-twin-regency-tower2-podium-original-contact-census-v2'


def ref(p):
    return dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes()))


def main():
    assert not DOC.exists()
    receipt = read(INPUT / 'result.json')
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                         (receipt['jobId'],)).fetchone() == ('complete', receipt)
    refs = [ref(Path(__file__)), ref(INPUT / 'result.json')]
    assert ref(INPUT / 'diagnostic.json.gz') in receipt['evidenceRefs']
    refs.extend(receipt['evidenceRefs'])
    assert all(ref(ROOT / p['path']) == p for p in refs)
    source = read(INPUT / 'diagnostic.json.gz')
    assert source['completeOriginalFaces'] == 13519 and source['allSourceFacesAccounted']
    worlds = []
    for s in source['completeSourceInputs']:
        asset = ROOT / s['asset']['path']; assert ref(asset) == s['asset']
        worlds.append(decode_original_world_triangles(asset.read_bytes()))
    tri = np.concatenate(worlds)
    assert tri.shape == (13519, 3, 3) and digest(tri.tobytes()) == source['completeOriginalWorldSHA256']
    bodies = source['bodies']; assert len(bodies) == 1120
    members = {f: i for i, b in enumerate(bodies) for f in b['globalOriginalFaces']}
    assert len(members) + len(source['exactNonrenderingGlobalFacesRetainedUncredited']) == len(tri)
    lower = np.asarray([b['bounds'][0] for b in bodies]); upper = np.asarray([b['bounds'][1] for b in bodies])
    candidates = []; eligible = 0
    for a, body in enumerate(bodies):
        same = [b for b in range(a + 1, len(bodies)) if bodies[b]['actorUID'] == body['actorUID']]
        eligible += len(same)
        candidates.extend((a, b) for b in same
            if np.all(lower[a] <= upper[b]) and np.all(lower[b] <= upper[a]))
    helpers = [HERE / n for n in ['exact_packed_world_geometry_20261009.py',
        'exact_original_shell_intersections_20261009.py', 'exact_original_component_contacts_20261009.py',
        'xl-popcorn-source-investigations-checkpoints-20261009.py']]
    refs.extend(ref(p) for p in helpers)
    claim = reservations.claim('twin-internal-source-' + str(uuid.uuid4()),
        ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
    assert claim['ok']; lease = claim['reservation']; last = time.monotonic(); last_output = last
    rational = {}; contacts = []; point_nominations = {}; tests = 0
    face_low = tri.min(axis=1); face_high = tri.max(axis=1)
    def exact(i):
        if i not in rational: rational[i] = rational_face(tri[i])
        return rational[i]
    def pulse(force=False):
        nonlocal last
        if force or time.monotonic() - last >= 20:
            assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease)
            last = time.monotonic()
    try:
        for cursor, (a, b) in enumerate(candidates):
            left, right = bodies[a]['globalOriginalFaces'], bodies[b]['globalOriginalFaces']
            if len(left) > len(right): left, right = right, left
            right = np.asarray(right, int); witness = None
            for i in left:
                hits = right[np.all(face_low[right] <= face_high[i], axis=1) &
                             np.all(face_high[right] >= face_low[i], axis=1)]
                for j in hits:
                    j = int(j); tests += 1
                    points = intersection_points(exact(i), exact(j))
                    if len(points) == 1 and (a, b) not in point_nominations:
                        ids = [i, j] if members[i] == a else [j, i]
                        point_nominations[a, b] = dict(components=[a, b],
                            globalOriginalFaces=ids, exactContact=contact_measure(points), noBridgeCredit=True)
                    if len(points) >= 2:
                        ids = [i, j] if members[i] == a else [j, i]
                        witness = dict(components=[a, b], globalOriginalFaces=ids, exactContact=contact_measure(points))
                        assert witness['exactContact']['dimension'] > 0
                        break
                    pulse()
                if witness is not None: break
            if witness is not None: contacts.append(witness)
            pulse()
            if time.monotonic() - last_output >= 20:
                print(dict(bodyPair=cursor + 1, candidates=len(candidates),
                    positivePairs=len(contacts), exactFacePairsTested=tests), flush=True)
                last_output = time.monotonic()
        for record in contacts:
            i, j = record['globalOriginalFaces']
            assert [members[i], members[j]] == record['components']
            assert contact_measure(intersection_points(exact(i), exact(j))) == record['exactContact']
            pulse()
        all_contacts = source['oneExactPositiveNominationPerCrossActorBodyPair'] + contacts
        reached = {18, 1091}
        assert len(bodies[18]['globalOriginalFaces']) == 1550 and len(bodies[1091]['globalOriginalFaces']) == 363
        while True:
            before = set(reached)
            for record in all_contacts:
                a, b = record['components']
                if a in reached or b in reached: reached.update([a, b])
            if reached == before: break
        pulse(True); assert all(ref(ROOT / p['path']) == p for p in refs)
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                (receipt['jobId'],)).fetchone() == ('complete', receipt)
        result = dict(uids=source['uids'], completeOriginalFaces=13519,
            fullOriginalWorldSHA256=source['completeOriginalWorldSHA256'], completeBodyCensus=ref(INPUT / 'diagnostic.json.gz'),
            completeWithinActorBodyPairCensus=True, eligibleWithinActorBodyPairs=eligible,
            exactInclusiveWithinActorBodyBoundsCandidates=candidates,
            strictlyDisjointWithinActorBodyPairs=eligible - len(candidates), exactFacePairsTested=tests,
            oneExactPositiveNominationPerWithinActorBodyPair=contacts,
            encounteredPointOnlyNominationsPreservedUncredited=list(point_nominations.values()),
            encounteredPointsAreNotCompleteFaceIntersectionInventory=True,
            crossActorContactsReusedOnlyFromExactCompletedReceipt=ref(INPUT / 'result.json'),
            purelyGeometricConnectivityFromNamedMainBodies=sorted(reached),
            remainingBodiesOutsideThatGeometricGraph=sorted(set(range(len(bodies))) - reached),
            namedMainBodiesNotAcceptedRootSeeds=True, sourceOnly=True, noFreshCurrentCapture=True,
            currentAcceptance=False, noRootOrStructuralOrVisualCredit=True,
            nativeReacceptance=False, sourceGeometryChanges=0, newlyInstalled=0, evidenceRefs=refs)
        save(DOC / 'diagnostic.json.gz', result)
        spec = importlib.util.spec_from_file_location('twin_internal_freeze', helpers[-1])
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        m.freeze(BATCH, 'complete-twin-regency-internal-original-contacts-source-only-v1',
            [ROOT / p['path'] for p in refs] + [DOC / 'diagnostic.json.gz'],
            dict(uids=source['uids'], sourceOnly=True, completeOriginalFaces=13519,
                positiveWithinActorBodyPairs=len(contacts), purelyGeometricReachableBodies=len(reached),
                currentAcceptance=False, newlyInstalled=0))
        print(dict(internalPositivePairs=len(contacts), purelyGeometricReachableBodies=len(reached),
            unqualifiedBodies=1120 - len(reached)), flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__': main()
