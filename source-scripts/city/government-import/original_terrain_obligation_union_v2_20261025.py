"""Retain all model/terrain obligations, optionally with replayed point contacts."""


def merge(model_forms, terrain_forms, scope, *, native_count, target_uids,
          expected_count, point_context=None, replayed_point_contacts=None):
    assert scope['currentNativeActors'] == native_count
    assert scope['uids'] == target_uids
    assert not scope['touchingNativeUids'] and scope['positiveAreaTerrainOverlaps'] == 0
    if scope['terrainContacts']:
        assert point_context is not None and replayed_point_contacts is not None
        assert replayed_point_contacts['contract'] == 'exact-original-terrain-single-point-contact-v1'
        assert {k: point_context[k] for k in replayed_point_contacts} == replayed_point_contacts
        assert len(replayed_point_contacts['rows']) == len(scope['terrainContacts'])
        assert {r['url'] for r in replayed_point_contacts['rows']} == {r['url'] for r in scope['terrainContacts']}
        assert all(r['noPositiveAreaOrSharedEdge'] and r['exactParentVertexAgreement'] for r in replayed_point_contacts['rows'])
    else:
        assert point_context is None and replayed_point_contacts is None
    assert len(terrain_forms) == len({f['uid'] for f in terrain_forms}) == scope['intersectingForms']
    result = dict(model_forms)
    assert all(k == v['uid'] for k,v in result.items())
    for form in terrain_forms:
        if form['uid'] in result: assert result[form['uid']] == form
        result[form['uid']] = form
    assert len(result) == expected_count
    return result
