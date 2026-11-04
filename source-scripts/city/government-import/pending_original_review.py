"""Verify an empty pending review for four explicitly scoped original XL sources.

An empty pending record is not a rejection or approval. Never discard it, accept
held/decided reviews, change a source hash, or grant installation credit here.
"""
SCOPED_UIDS = frozenset({
    'landsd/227593:0', 'landsd/235034:0',
    'landsd/276331:0', 'landsd/305582:0',
})


def verify(con, uid, source_sha, expected=None):
    assert uid in SCOPED_UIDS, 'Explicit four-source pending continuation only'
    assert isinstance(source_sha, str) and len(source_sha) == 64
    actual = con.execute(
        'SELECT snapshot_id,review_state,source_sha256,result '
        'FROM astra_modelling.model_reviews WHERE uid=%s '
        'ORDER BY updated_at DESC LIMIT 1', (uid,)).fetchone()
    assert actual, 'An existing pending record must remain present'
    snapshot, state, sha, result = actual
    assert state == 'pending' and sha == source_sha and result is None, \
        'A decided, changed-source or held review requires separate resolution'
    receipt = {'snapshotId': snapshot, 'state': state,
               'sourceSHA256': sha, 'result': result}
    if expected is not None:
        assert set(expected) == set(receipt)
        assert {k: expected[k] for k in receipt if k != 'snapshotId'} == \
            {k: receipt[k] for k in receipt if k != 'snapshotId'}
        archived = con.execute(
            'SELECT review_state,source_sha256,result '
            'FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',
            (expected['snapshotId'], uid)).fetchone()
        assert archived == ('pending', source_sha, None), \
            'The pinned pending record changed or disappeared'
    return receipt
