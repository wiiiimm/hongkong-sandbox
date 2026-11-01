"""Retain all obligations for a separately replayed finite shared-edge context."""
from original_terrain_obligation_union_v2_20261025 import merge as point_merge
from original_terrain_shared_edge_v1_20261102 import CONTRACT


def merge(model_forms, terrain_forms, scope, *, native_count, target_uids,
          expected_count, point_context=None, replayed_point_contacts=None):
    replay = replayed_point_contacts
    if not replay or replay.get('contract') != CONTRACT:
        return point_merge(model_forms, terrain_forms, scope, native_count=native_count,
            target_uids=target_uids, expected_count=expected_count,
            point_context=point_context, replayed_point_contacts=replay)
    assert scope['currentNativeActors'] == native_count and scope['uids'] == target_uids
    assert not scope['touchingNativeUids'] and scope['positiveAreaTerrainOverlaps'] == 0
    assert scope['terrainContacts'] and point_context is not None
    assert {k: point_context[k] for k in replay} == replay
    assert len(replay['rows']) == len(scope['terrainContacts'])
    assert {r['url'] for r in replay['rows']} == {r['url'] for r in scope['terrainContacts']}
    assert all(r['interval'][0] < r['interval'][1] and r['comparison']['passed']
        and r['comparison']['completeFiniteUpperEnvelopesChecked']
        and r['comparison']['toleranceM'] == .01 for r in replay['rows'])
    assert len(terrain_forms) == len({f['uid'] for f in terrain_forms}) == scope['intersectingForms']
    result = dict(model_forms)
    assert all(k == v['uid'] for k, v in result.items())
    for form in terrain_forms:
        if form['uid'] in result:
            assert result[form['uid']] == form
        result[form['uid']] = form
    assert len(result) == expected_count
    return result
