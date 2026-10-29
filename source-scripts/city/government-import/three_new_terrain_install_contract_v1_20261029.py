"""Require an exact three-patch append while retaining every installed entry."""


def terrain_delta(before, after, planned):
    assert len(planned) == 3
    assert all(not p.get('replaces') and not p.get('replacesMany') for p in planned)
    destinations = [p['destination'] for p in planned]
    assert len(set(destinations)) == 3
    assert not set(destinations).intersection(r['url'] for r in before)
    assert len(after) == len(before) + 3 and after[:-3] == before
    for row, plan in zip(after[-3:], planned):
        assert row['url'] == plan['destination'] and row['sha256'] == plan['sha256']
        assert row['resolution'] == plan['resolution'] and row['area'] == plan['area']
