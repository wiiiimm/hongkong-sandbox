"""Require complete desktop/mobile retained-original own views."""
def verify(views,entries,widths=(390,1280)):
    assert entries and views
    expected={(uid,w,t)for uid in entries for w in widths for t in ['15:00','22:00']}
    assert len(views)==len(expected)
    assert {(v['uid'],v['width'],v['time'])for v in views}==expected
    for v in views:
        entry=entries[v['uid']]
        assert v['active'] and v['visible'] and v['fullyFramed'] and not v['fallbackFaces']
        assert v['sourceSHA256']==entry['sha256'] and v['originalTriangles']==entry['triangles']
        assert v['meshVisibility'] and len(v['meshVisibility'])==len(v['wireframeFlags'])
        assert all(v['meshVisibility']) and not any(v['wireframeFlags'])
    return True
