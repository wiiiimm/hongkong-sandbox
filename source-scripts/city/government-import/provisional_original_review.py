"""Recheck twelve exact provisional placement holds without erasing their decisions.

Only fresh full original-source/terrain/runtime evidence can supersede them.
This verifier grants no acceptance, publication or landmark membership.
"""
from run import ROOT, read, digest

SCOPED_UIDS = frozenset('landsd/' + str(n) + ':0' for n in (
    204143, 204144, 204145, 204146, 204154, 204155,
    322573, 74569, 74570, 78828, 78915, 79318))
DECISIONS_PATH = 'docs/astra-city/assembly-support-review/decisions.json'
DECISIONS_SHA = '7fe0d4416159c27a75624c2fb850789a688e097d03c50309bff7885bb94fab7b'
SUFFIX = ('. Native terrain/support review is ongoing; exact current-source geometry retained. '
          'Seven staged terrain-dependent candidates await the combined terrain/browser guard; '
          'this hold can be superseded with fresh evidence.')


def validate_decision(uid, source_sha, actual, row):
    """Reject substantive, source-changed or newly decided reviews fail closed."""
    assert uid in SCOPED_UIDS and isinstance(source_sha, str) and len(source_sha) == 64
    assert actual and row['uid'] == uid and row['sha256'] == source_sha
    assert row['status'] == 'held-source-component-placement'
    assert row['native1x'] and row['sourceIdentityVerifiedByRuntimeLoader']
    assert not row['placementApproved'] and not row['publicationApproved']
    assert not row['supportDependencies'], 'Unresolved explicit dependencies need their own route'
    known = row['knownHold']
    assert known is None or known['classification'] == 'rendered-terrain-contact'
    snapshot, state, sha, result = actual
    assert state == 'held' and sha == source_sha
    expected = {'commit': None, 'sha256': DECISIONS_SHA, 'evidence': DECISIONS_PATH,
                'observation': 'Provisional source-placement hold: ' + str(row['rimCounts']) + SUFFIX,
                'productionPublished': False, 'wholeLandmarkComplete': False}
    assert result == expected, 'Only the exact archived provisional placement decision is resumable'
    return {'snapshotId': snapshot, 'state': state, 'sourceSHA256': sha, 'result': result}


def verify(con, uid, source_sha, expected=None):
    assert uid in SCOPED_UIDS
    path = ROOT / DECISIONS_PATH
    assert digest(path.read_bytes()) == DECISIONS_SHA, 'Archived decisions changed'
    rows = [r for r in read(path)['rows'] if r['uid'] == uid]
    assert len(rows) == 1
    actual = con.execute('SELECT snapshot_id,review_state,source_sha256,result '
        'FROM astra_modelling.model_reviews WHERE uid=%s ORDER BY updated_at DESC LIMIT 1', (uid,)).fetchone()
    receipt = validate_decision(uid, source_sha, actual, rows[0])
    if expected is not None:
        assert set(expected) == set(receipt)
        assert {k:v for k,v in receipt.items() if k != 'snapshotId'} == \
               {k:v for k,v in expected.items() if k != 'snapshotId'}
        archived = con.execute('SELECT review_state,source_sha256,result FROM astra_modelling.model_reviews '
            'WHERE snapshot_id=%s AND uid=%s', (expected['snapshotId'], uid)).fetchone()
        assert archived == (expected['state'], source_sha, expected['result']), 'Pinned historical hold changed'
    return receipt
