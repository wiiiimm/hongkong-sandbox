"""Bind an acyclic multi-parent co-import graph to exact original catalogue entries."""
from candidate_availability_graph_v1_20261026 import validate


def verify(models, sources, supports):
    by = {m['uid']: m for m in models}
    assert len(by) == len(models) and {u: m['sha256'] for u, m in by.items()} == sources
    assert set(supports) == set(sources)
    graph, _ = validate(list(sources), [u + ',' + p for u, peers in supports.items() for p in peers])
    assert graph == supports
    for uid, model in by.items():
        assert model['proceduralWindows'] is False and not model.get('suppressesBuildingUids')
        expected = [dict(uid=p, state='installed', buildingCSUID=by[p]['buildingCSUID'], sha256=sources[p]) for p in supports[uid]]
        assert model.get('supportDependencies', []) == expected
    return True
