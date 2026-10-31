"""Bind an original co-import support graph to exact tested catalogue entries."""


def verify(models,sources,supports):
    by={m['uid']:m for m in models}
    assert len(by)==len(models)and{u:m['sha256']for u,m in by.items()}==sources
    assert set(supports)<=set(sources)and set(supports.values())<=set(sources)
    for uid,m in by.items():
        assert m['proceduralWindows']is False and not m.get('suppressesBuildingUids')
        parent=supports.get(uid)
        if parent:
            assert parent!=uid
            expected=[dict(uid=parent,state='installed',buildingCSUID=by[parent]['buildingCSUID'],sha256=sources[parent])]
            assert m.get('supportDependencies')==expected
        else:assert not m.get('supportDependencies')
        seen=set();at=uid
        while at in supports:
            assert at not in seen;seen.add(at);at=supports[at]
    return True
