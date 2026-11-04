"""Require one exact complete native replacement; never grants terrain acceptance."""


def verify(scope, receipt, old, candidate):
    records = receipt.get('replacedNativeTerrain', [])
    assert len(records) == 1, 'Exactly one explicit replacement required'
    record = records[0]
    assert scope['positiveAreaTerrainOverlaps'] == 1
    overlaps = [r['url'] for r in scope['terrainContacts']
                if r['coarseOverlapAreaM2'] > 0 or any(c['overlapAreaM2'] > 0 for c in r['packedContacts'])]
    assert overlaps == [record['url']], 'Every positive terrain overlap needs explicit retention'
    assert old.get('nativeMesh') and candidate.get('nativeMesh')
    assert old['meta']['parentTerrain'] == candidate['meta']['parentTerrain'] == 'city/data/terrain.json'
    assert old['meta']['parentSha256'] == candidate['meta']['parentSha256']
    assert old['coarseCells'] == record['coarseCells']
    assert old['meta']['targetUids'] == record['targetUids']
    a, b, c, d = old['coarseCells']
    aa, bb, cc, dd = candidate['coarseCells']
    assert all(type(v) is int for v in [a, b, c, d, aa, bb, cc, dd])
    assert aa <= a < c <= cc and bb <= b < d <= dd
    for ids in [old['meta']['targetUids'], receipt['uids'], candidate['meta']['targetUids'], scope['uids']]:
        assert ids and len(ids) == len(set(ids))
    wanted = set(old['meta']['targetUids']) | set(receipt['uids'])
    assert set(candidate['meta']['targetUids']) == set(scope['uids']) == wanted
    assert scope['regionalCoarseCells'] == candidate['coarseCells']
    return dict(url=record['url'], sha256=record['sha256'], retainedUids=record['targetUids'])
