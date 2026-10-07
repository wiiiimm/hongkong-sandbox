"""Persist the user-requested Hoi Tai later-pass flag in the existing Neon job ledger."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'source-scripts/city/government-import'))
from run import read, save, digest, connect, reservations, jobs, Jsonb, dict_row

DOC = Path(__file__).resolve().parent
BATCH = DOC.name
STAGE = 'held-source-deferred-disposition-v1'
UID = 'landsd/229881:0'
REVIEW_PATH = ROOT / 'docs/astra-city/government-import/government-xl-hoi-tai-ai-evidence-review-20261007/result.json'

def main():
    review = read(REVIEW_PATH)
    assert review['uid'] == UID and review['reviewOutcome'] == 'unresolved'
    assert not review['installationApproved'] and review['newlyInstalled'] == 0
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                           (review['jobId'],)).fetchone() == ('complete', review)
    decision = {
        'uid': UID, 'name': 'HOI TAI HOUSE (BLK D)', 'component': 'government podium source',
        'sourceSHA256': review['sourceSHA256'], 'relatedTowerUid': 'landsd/235557:0',
        'state': 'held-for-second-pass', 'humanStatus': 'held-unknown',
        'displayStatus': 'Held — revisit later', 'deferred': True, 'revisitLater': True,
        'nextPass': 2, 'blockedBy': 'missing-authoritative-ground-and-component-support-evidence',
        'reasons': review['reasons'], 'installationApproved': False,
        'retainCurrentModel': True, 'modelGeometryChanges': 0, 'newlyInstalled': 0,
        'publication': False, 'needsHumanDecision': False, 'needsAIProcessing': None,
        'computeOnlyRecoveryEstablished': False, 'aiEvidenceReviewCompleted': True,
        'reviewJobId': review['jobId'], 'minimumSampledWallClearanceM': -1.072214603424075,
        'wallClearanceLimitM': -0.5,
        'revisitTriggers': [
            'Authoritative finished-grade/foundation/retaining-wall evidence with HKPD elevations matching this source epoch.',
            'Authoritative podium/tower component and supporting-deck interface evidence.',
            'A corrected official model or terrain revision, followed by fresh acceptance checks.'
        ],
        'nextStep': 'Retain the current viewer model; revisit when new authoritative evidence or a corrected source is available. Reuse the completed review and source-bound receipts; do not repeat unchanged checks.',
        'qualification': 'Not currently installable under the existing checks. Not established permanently invalid. Completed AI evidence review did not establish architectural intent, a code defect, or a safe recovery. Deferred disposition is not acceptance or installation; no modelling work or follow-up worker is queued.',
    }
    save(DOC / 'decision.json', decision)
    refs = [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p.read_bytes())}
            for p in (Path(__file__).resolve(), DOC / 'decision.json', REVIEW_PATH)]
    payload = {'uid': UID, 'sourceSHA256': decision['sourceSHA256'], 'evidenceRefs': refs}
    claim = reservations.claim('codex-hoi-tai-deferred-disposition', ['building:' + UID], batch=BATCH)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        jid = jobs.enqueue(BATCH, STAGE, payload)
        result = {**decision, **payload, 'batch': BATCH, 'stage': STAGE, 'jobId': jid}
        with connect() as con:
            prior = con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone()
        if prior[0] != 'complete':
            job = jobs.claim(BATCH, lease['owner'], [STAGE], lease_seconds=300)
            assert job and job['id'] == jid
            with connect() as con:
                con.row_factory = dict_row
                con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
                assert reservations._current(con, lease)
                for ref in refs:
                    assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
                assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jid, job['owner'], job['token'])).rowcount == 1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', result)
            assert con.execute("SELECT result->>'state',result->>'revisitLater' FROM astra_modelling.jobs WHERE id=%s AND result->>'uid'=%s", (jid, UID)).fetchone() == ('held-for-second-pass', 'true')
        save(DOC / 'result.json', result)
        save(DOC / 'neon-sync.json', {'jobId': jid, 'resultVerified': True, 'deferredFlagVerified': True, 'ledger': 'astra_modelling.jobs'})
        print(jid)
    finally:
        assert reservations.release(lease)

if __name__ == '__main__':
    main()
