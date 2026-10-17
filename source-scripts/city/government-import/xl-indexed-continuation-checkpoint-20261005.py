"""Freeze seven completed XL continuations and exact narrowed blockers in Neon."""
import json
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, Jsonb, dict_row

BATCH = 'government-xl-indexed-continuation-checkpoint-20261005'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
BASE = ROOT / 'docs/astra-city/government-import'
CASES = [('landsd/285509:0', 'seaview-garden-podium', 'source-clearance-foundation'),
         ('landsd/80343:0', 'science-museum', 'overlapping-component'),
         ('landsd/284938:0', 'hampton-loft', 'overlapping-component'),
         ('landsd/242706:0', 'fortune-city-one-plus', 'source-clearance')]


def ref(path): return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def run():
    assert not DOC.exists(), 'Immutable completed checkpoint already exists'
    completed, refs, rows = [], [], []
    for uid, slug, category in CASES:
        phase = 'disjoint-parent' if slug in ('science-museum', 'hampton-loft') else 'indexed-terrain'
        folder = BASE / ('government-xl-' + slug + '-' + phase + '-20261005')
        result = read(folder / 'result.json'); sync = read(folder / 'neon-sync.json')
        assert result['uid'] == uid and result['humanStatus'] == 'held-unknown' and result['reasons']
        assert sync['jobId'] == result['jobId'] and sync['resultVerified']
        completed.append((result['jobId'], result)); refs.extend([ref(folder / 'result.json'), ref(folder / 'neon-sync.json')])
        rows.append({'uid': uid, 'sourceSHA256': result['sourceSHA256'], 'category': category,
                     'humanStatus': 'held-unknown', 'reasons': result['reasons'], 'latestJobId': result['jobId'],
                     'requiresAI': False, 'requiresHumanDecision': False})
    support_folder = BASE / 'government-xl-sol-city-star-house-supports-20261005'
    support = read(support_folder / 'result.json'); completed.append((support['jobId'], support))
    refs.extend([ref(support_folder / 'result.json'), ref(support_folder / 'neon-sync.json')])
    rows.extend({**r, 'category': 'source-support-closure', 'latestJobId': support['jobId']} for r in support['rows'])
    auxiliary = []
    for source in read(support_folder / 'selection.json.gz')['rows']:
        if source['uid'] not in {r['uid'] for r in support['rows']}:
            auxiliary.append({'uid': source['uid'], 'sourceSHA256': source['sourceSHA256'], 'installed': False})
    hampton_folder = BASE / 'government-xl-hampton-loft-original-support-group-20261005'
    hampton = read(hampton_folder / 'result.json'); completed.append((hampton['jobId'], hampton))
    refs.extend([ref(hampton_folder / 'result.json'), ref(hampton_folder / 'neon-sync.json')])
    auxiliary.extend({'uid': r['uid'], 'sourceSHA256': r['sourceSHA256'], 'installed': False} for r in hampton['rows'])
    lookup_folder = BASE / 'government-xl-science-component-lookup-20261005'
    lookup = read(lookup_folder / 'result.json'); completed.append((lookup['jobId'], lookup))
    refs.extend([ref(lookup_folder / 'result.json'), ref(lookup_folder / 'neon-sync.json')])
    protected = []
    for slug in ['science-museum', 'hampton-loft']:
        folder = BASE / ('government-xl-' + slug + '-disjoint-parent-20261005')
        proof = read(folder / 'parent-preservation.json')['proof']; assert proof['sourceProjectionIntersectionM2'] < 1e-8
        checks = {r['uid']: r for r in read(folder / 'neighbour-checks.json')['rows']}
        assert all(not checks[u]['reasons'] for u in proof['protectedUids'])
        assert read(folder / 'foundation.json')['rows'][0]['strictFoundationAccepted']
        protected.extend(proof['protectedUids']); refs.append(ref(folder / 'parent-preservation.json'))
    assert len(rows) == 7 and len(auxiliary) == 3 and len(protected) == 10
    cohort = {r['uid'] for r in read(BASE / 'government-xl-remaining-20260923/selection.json.gz')['rows']}
    assert all(r['uid'] in cohort for r in rows) and all(r['uid'] not in cohort for r in auxiliary)
    pointer = read(ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json')
    scope = sorted({r['uid'] for r in rows + auxiliary} | {lookup['uid']})
    claim = reservations.claim('codex-xl-indexed-checkpoint-' + str(uuid.uuid4()), ['building:' + u for u in scope], batch=BATCH)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            for jobid, expected in completed:
                actual = con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jobid,)).fetchone()
                assert actual and actual[0] == 'complete' and actual[1] == expected
            reviews = dict(con.execute('SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s', (pointer['snapshotId'],)))
        installed = sum(reviews.get(u) == 'installed-verified' for u in cohort); assert len(cohort) == 352 and installed == 42
        for _, result in completed:
            for evidence in result.get('evidenceRefs', []): assert digest((ROOT / evidence['path']).read_bytes()) == evidence['sha256']
        payload = {'evidenceRefs': refs, 'reviewSnapshot': pointer['snapshotId'], 'pipelineSHA256': digest(Path(__file__).read_bytes())}
        stage = 'completed-indexed-original-continuations-v1'; jobid = jobs.enqueue(BATCH, stage, payload)
        job = jobs.claim(BATCH, lease['owner'], [stage], lease_seconds=1800); assert job and job['id'] == jobid
        result = {**payload, 'batch': BATCH, 'jobId': jobid, 'rows': rows, 'auxiliarySources': auxiliary,
                  'newlyInstalled': 0, 'additionalRecoveredOriginalMeshes': 3, 'removedNeighbourRegressions': 10,
                  'protectedNeighbourUids': protected, 'unresolvedSupportSamples': sum(r['unresolvedSamples'] for r in support['rows']) + sum(r['unresolved'] for r in hampton['rows']),
                  'scienceComponentLookupJobId': lookup['jobId'], 'scienceMatchingContainingDirectoryEntries': lookup['matchingDirectoryEntries'],
                  'widerXLCheckpoint': {'models': 352, 'installed': installed, 'held': 352 - installed},
                  'humanCounts': {'installed': 0, 'to-do': 0, 'held-human': 0, 'held-ai': 0, 'held-unknown': 7, 'in-process': 0},
                  'activeWorkers': 0, 'queuedFollowups': 0, 'scriptExternalAICalls': 0, 'modelGeometryChanges': 0, 'publication': False,
                  'qualification': 'Complete bounded source/terrain/support continuation and exact Neon readback. Narrowed technical blockers do not grant installation credit or establish architectural AI/human dependencies. Source and current terrain under disjoint neighbours are preserved; all acceptance limits unchanged.'}
        with connect() as con:
            con.row_factory = dict_row; con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,)); assert reservations._current(con, lease)
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jobid, job['owner'], job['token'])).rowcount == 1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY'); assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s', (jobid,)).fetchone()[0] == result
        save(DOC / 'result.json', result); save(DOC / 'neon-sync.json', {'jobId': jobid, 'resultVerified': True})
        print(json.dumps({'jobId': jobid, 'neonVerified': True, 'primarySources': 7, 'additionalOriginals': 3, 'removedNeighbourRegressions': 10, 'newlyInstalled': 0, 'XL': result['widerXLCheckpoint']}), flush=True)
    finally: reservations.release(lease)


if __name__ == '__main__': run()
