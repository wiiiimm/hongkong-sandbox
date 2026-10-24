"""Exact parent target/native census; no physical or source-role acceptance."""
import math
from collections import Counter

EXPECTED_TARGETS = frozenset('landsd/'+v+':0' for v in
    ['101781','122298','181141','213822','232907','239367','257313',
     '263590','268032','304714','73140','93890'])
OLD_CHILD = 'government-native-central-hullett-house'

def census(parent, catalogue_rows, current_forms):
    children = parent['patches']
    assert len(children) == 10
    ids = [c['id'] for c in children]
    assert len(set(ids)) == len(ids)
    old = [c for c in children if c['id'] == OLD_CHILD]
    assert len(old) == 1 and old[0]['meta']['targetUids'] == ['landsd/73140:0']
    assert len(old[0]['nativeMesh']['index']) == 10675*3
    assert not old[0].get('patches')
    declared = []
    for c in children:
        targets = c['meta']['targetUids']
        assert targets and len(set(targets)) == len(targets)
        assert all(isinstance(u,str) for u in targets)
        declared.extend(targets)
    assert set(declared) == EXPECTED_TARGETS
    assert len(declared) == len(EXPECTED_TARGETS), 'Ambiguous terrain target membership'
    entries = [r for r in catalogue_rows if r['uid'] in EXPECTED_TARGETS]
    assert all(v == 1 for v in Counter(r['uid'] for r in entries).values()), 'Ambiguous installed native UID'
    forms = [b for b in current_forms if b['uid'] in EXPECTED_TARGETS]
    assert Counter(b['uid'] for b in forms) == Counter(EXPECTED_TARGETS), 'Incomplete/ambiguous current target census'
    for b in forms:
        assert b.get('rings') and all(len(r) >= 3 for r in b['rings'])
    native = sorted(r['uid'] for r in entries)
    basic = sorted(EXPECTED_TARGETS-set(native))
    assert native and 'landsd/73140:0' in native
    assert not basic, 'Expected twelve installed native targets; missing actor is never inferred basic'
    for e in entries:
        assert isinstance(e['sha256'],str) and len(e['sha256']) == 64
        assert e['asset'] and e['triangles'] > 0 and e['worldBounds']
    return dict(allTargetUids=sorted(EXPECTED_TARGETS), installedNativeUids=native,
                currentBasicUids=basic, allTargetsRemainOrdinaryPhysicalActors=True,
                physicalAccepted=False, supportAccepted=False)

def numeric_tree(value):
    """All finite numeric values, array order and field structure, without tolerance."""
    if isinstance(value,bool): return value
    if isinstance(value,(int,float)):
        assert math.isfinite(value), 'Nonfinite terrain number'
        return value
    if isinstance(value,list): return [numeric_tree(v) for v in value]
    if isinstance(value,dict): return {k:numeric_tree(v) for k,v in value.items()}
    assert value is None or isinstance(value,str)
    return None

def changed_strings(previous,current,pointer=''):
    assert type(previous) is type(current) or isinstance(previous,(int,float)) and isinstance(current,(int,float))
    if isinstance(previous,dict):
        assert previous.keys() == current.keys()
        return [v for k in previous for v in changed_strings(previous[k],current[k],pointer+'/'+k)]
    if isinstance(previous,list):
        assert len(previous)==len(current)
        return [v for i,(a,b) in enumerate(zip(previous,current)) for v in changed_strings(a,b,pointer+'/'+str(i))]
    if isinstance(previous,str) and previous != current:
        return [dict(jsonPointer=pointer,before=previous,after=current)]
    return []

def reconstructed_numeric_equal(previous, current, *, old_batch=None,new_batch=None,audit_hash_verifier=None):
    assert numeric_tree(previous) == numeric_tree(current), 'Reconstructed complete numeric terrain differs'
    assert [c['id'] for c in previous['patches']] == [c['id'] for c in current['patches']]
    for before,after in zip(previous['patches'],current['patches']):
        assert before['meta']['targetUids'] == after['meta']['targetUids']
        assert before.get('nativeMesh',{}).get('position') == after.get('nativeMesh',{}).get('position')
        assert before.get('nativeMesh',{}).get('index') == after.get('nativeMesh',{}).get('index')
    changes=changed_strings(previous,current)
    for change in changes:
        p=change['jsonPointer'];a=change['before'];b=change['after']
        if old_batch and new_batch and old_batch in a and a.replace(old_batch,new_batch)==b:
            assert p.rsplit('/',1)[-1] in ['path','evidencePath','supersededURL'], ('Unexpected changed role/string',p)
            change['qualifiedDifference']='explicit-old-new-batch-evidence-path'
        else:
            assert p.endswith('/nativeMesh/sourceOverlap/evidenceSHA256') and audit_hash_verifier, ('Unqualified metadata string change',p)
            child_index=int(p.split('/')[2]);audit_hash_verifier(previous['patches'][child_index],current['patches'][child_index])
            change['qualifiedDifference']='independently-hash-verified-renewed-overlap-audit'
    return dict(completeNumericTerrainEqual=True, literalPositionIndexEqual=True,
                changedStringJSONPointers=changes,numericalToleranceUsed=False, physicalAccepted=False)
