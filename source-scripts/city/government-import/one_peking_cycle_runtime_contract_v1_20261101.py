"""Require every exact-pair lifecycle case; no source or publication approval."""
from one_peking_cycle_retained_contract_v2_20261101 import SOURCES

def verify_atomic(report, models):
    expected = {m['uid']: (m['sha256'], m['triangles']) for m in models}
    assert len(models) == len(expected) == 2
    assert {u: s for u, (s, _) in expected.items()} == SOURCES
    ids = sorted(expected)
    cases = report['cases']
    assert report['passed'] and not report['pageErrors'] and len(cases) == 3
    assert {(c['width'], c['failedUid']) for c in cases} == {(1280, None), (390, ids[0]), (390, ids[1])}
    for c in cases:
        assert c['baseOnlyRestoredCompleteGroup'] and c['completeGroupEvicted']
        assert c['audit']['frames'] > 0 and not c['audit']['violations']
        transitions = c['audit']['transitions']
        assert transitions[0]['active'] == transitions[-1]['active'] == []
        assert all(t['active'] in [[], ids] for t in transitions)
        assert any(t['active'] == ids for t in transitions)
        assert len(c['sources']) == 2 and {s['uid']: (s['sha256'], s['triangles']) for s in c['sources']} == expected
        assert all(s['active'] for s in c['sources'])
        if c['failedUid']:
            assert c['failureKeptAllBasics']
    return True
