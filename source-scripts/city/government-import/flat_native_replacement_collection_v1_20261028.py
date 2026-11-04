"""Complete explicit flat-native replacement scope, including all old targets.

Metadata/schema contract only; no geometric or retained-actor approval follows.
"""


def verify(scope, receipt, old_by_url, candidate):
    records=receipt.get('replacedNativeTerrain',[])
    assert 1<=len(records)<=8
    urls=[r['url'] for r in records]
    assert len(urls)==len(set(urls)) and set(old_by_url)==set(urls)
    overlaps=[r['url'] for r in scope['terrainContacts']
              if r['coarseOverlapAreaM2']>0 or any(c['overlapAreaM2']>0 for c in r['packedContacts'])]
    assert len(overlaps)==scope['positiveAreaTerrainOverlaps']==len(records)
    assert len(overlaps)==len(set(overlaps)) and set(overlaps)==set(urls)
    assert candidate.get('nativeMesh')
    assert not candidate['nativeMesh'].get('source',{}).get('coordinatedBoundary')
    assert candidate['meta']['parentTerrain']=='city/data/terrain.json'
    assert receipt['uids'] and len(receipt['uids'])==len(set(receipt['uids']))
    wanted=set(receipt['uids']);result=[]
    aa,bb,cc,dd=candidate['coarseCells']
    assert all(type(v) is int for v in [aa,bb,cc,dd])
    for record in records:
        old=old_by_url[record['url']]
        assert old.get('nativeMesh') and not old['nativeMesh'].get('source',{}).get('coordinatedBoundary')
        assert old['meta']['parentTerrain']==candidate['meta']['parentTerrain']
        assert old['meta']['parentSha256']==candidate['meta']['parentSha256']
        assert old['coarseCells']==record['coarseCells']
        assert old['meta']['targetUids']==record['targetUids']
        ids=old['meta']['targetUids'];assert ids and len(ids)==len(set(ids))
        a,b,c,d=old['coarseCells']
        assert all(type(v) is int for v in [a,b,c,d])
        assert aa<=a<c<=cc and bb<=b<d<=dd
        wanted.update(ids)
        result.append(dict(url=record['url'],sha256=record['sha256'],retainedUids=ids))
    for ids in [candidate['meta']['targetUids'],scope['uids']]:
        assert ids and len(ids)==len(set(ids)) and set(ids)==wanted
    assert scope['regionalCoarseCells']==candidate['coarseCells']
    return result
