"""Whole-viewport evidence requirements; partial runs never become acceptance."""

def validate_completed(report,width,sources,retained):
    assert report.get('passed')is True and report['errors']==[]
    views=[r for r in report['views']if'time'in r]
    assert len(views)==2*len(sources)and {(r['uid'],r['time'])for r in views}=={(u,t)for u in sources for t in ['15:00','22:00']}
    for r in views:
        assert r['width']==width and r['sourceSHA256']==sources[r['uid']]['sha256']and r['originalTriangles']==sources[r['uid']]['triangles']
        assert all(r['meshVisibility'])and not any(r['wireframeFlags'])
        assert all(r[k]for k in ['active','visible','fullyFramed','solidAppearance'])and r['fallbackFaces']==0
        assert r['pick']==r['collision']==r['uid']
    native=report['retainedNativeOwnViews']
    assert len(native)==2*len(retained)and {(r['uid'],r['time'])for r in native}=={(u,t)for u in retained for t in ['15:00','22:00']}
    for r in native:
        assert r['width']==width and r['sourceSHA256']==retained[r['uid']]['sha256']and r['originalTriangles']==retained[r['uid']]['triangles']
        assert all(r[k]for k in ['active','visible','fullyFramed'])and not r['fallbackFaces']and all(r['meshVisibility'])and not any(r['wireframeFlags'])
    assert report['jointViews']
    for joint in report['jointViews']:
        assert {m['uid']:m['sourceSHA256']for m in joint['models']}=={u:r['sha256']for u,r in sources.items()}
        assert all(m['active']and m['visible']and not m['fallbackFaces']for m in joint['models'])
    if width==390:
        failures=[r for r in report['views']if r.get('phase')=='failed-download'];assert len(failures)==len(sources)and {r['uid']for r in failures}==set(sources)and all(r['fallbackRetained']for r in failures)
    return True


def unchanged_render_config(before,after):
    ignored={'doc'}
    assert {k:v for k,v in before.items()if k not in ignored}=={k:v for k,v in after.items()if k not in ignored}
    assert not before.get('retainedOnly')and not after.get('retainedOnly')
