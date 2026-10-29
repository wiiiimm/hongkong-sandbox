"""Exact manifest delta and retained-actor visual requirements for a replacement."""

def terrain_delta(before, after, planned):
    assert len(planned)==1
    new=planned[0];old=new['replaces']
    matches=[r for r in before if r['url']==old['url']]
    assert len(matches)==1 and matches[0]['sha256']==old['sha256']
    assert new['destination']not in {r['url']for r in before}
    assert len(after)==len(before)
    assert after[:-1]==[r for r in before if r['url']!=old['url']]
    entry=after[-1]
    assert entry['url']==new['destination']and entry['sha256']==new['sha256']
    assert entry['area']==new['area']and entry['resolution']==new['resolution']


def retained_views(rows, expected, widths):
    assert expected and len(rows)==2*len(widths)*len(expected)
    keys=set()
    for row in rows:
        uid=row['uid'];key=(uid,row['width'],row['time'])
        assert uid in expected and row['sourceSHA256']==expected[uid]
        assert row['width']in widths and row['time']in ['15:00','22:00']
        assert row['active']and row['visible']and row['fullyFramed']and not row['fallbackFaces']
        assert key not in keys;keys.add(key)
    assert keys=={(uid,width,time)for uid in expected for width in widths for time in ['15:00','22:00']}
