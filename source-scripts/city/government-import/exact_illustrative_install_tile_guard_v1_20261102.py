"""Verify the exact enumerated illustrative-post transaction and no other tile edits."""
import copy,hashlib,json

def verify(before_tiles,after_tiles,before_bytes,after_bytes,updates):
    assert updates and len({u['uid']for u in updates})==len(updates)
    expected_tiles=copy.deepcopy(before_tiles);by_tile={}
    for u in updates:by_tile.setdefault(u['tile'],[]).append(u)
    assert set(before_bytes)==set(after_bytes)==set(by_tile)
    for tile,items in by_tile.items():
        raw=before_bytes[tile];expected=json.loads(raw)
        for u in items:
            assert hashlib.sha256(raw).hexdigest()==u['tileSHA256']
            matches=[b for b in expected['buildings']if b['uid']==u['uid']]
            assert len(matches)==1 and matches[0]==u['before']
            matches[0].update(foundationBase=u['foundationBase'],foundationPolicy='terrain-derived-illustrative-posts')
        actual=after_bytes[tile];assert json.loads(actual)==expected
        entries=[t for t in expected_tiles if t['url']==tile]
        assert len(entries)==1;entries[0]['bytes']=len(actual)
    assert after_tiles==expected_tiles
    return True
