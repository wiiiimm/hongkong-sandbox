"""Merge immutable model and terrain-domain forms without dropping obligations."""

def merge(model_forms,terrain_forms,scope,*,native_count,target_uids,expected_count):
    assert scope['currentNativeActors']==native_count
    assert scope['uids']==target_uids
    assert not scope['touchingNativeUids']and not scope['terrainContacts']and scope['positiveAreaTerrainOverlaps']==0
    assert len(terrain_forms)==len({f['uid']for f in terrain_forms})==scope['intersectingForms']
    result=dict(model_forms)
    assert all(k==v['uid']for k,v in result.items())
    for form in terrain_forms:
        if form['uid']in result:assert result[form['uid']]==form
        result[form['uid']]=form
    assert len(result)==expected_count
    return result
