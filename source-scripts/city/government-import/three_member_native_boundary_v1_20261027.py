"""Strict three-member terrain chain composed from unchanged finite pair checks.

Only explicit chain markers use this private adapter. Other paths retain their
existing verifier. This module grants no model or publication acceptance.
"""
import copy,json,sys
from contextlib import contextmanager
from pathlib import Path
import shapely
INTEGRATION=Path(__file__).resolve().parents[1]/'island-detail-integration'
if str(INTEGRATION)not in sys.path:sys.path.insert(0,str(INTEGRATION))
import coordinated_native_boundary as legacy
POLICY='finite-native-three-member-chain-v1'
PAIR_BOUNDARY=legacy.coordinated_boundary
PAIR_EFFECTIVE=legacy.validate_effective_coordinated_members

def marker(node):return node.get('nativeMesh',{}).get('source',{}).get('coordinatedBoundary')

def load_chain(ref,parent=None):
    proof=legacy.reference(ref)
    assert set(proof)=={'policy','parent','members','pairs'} and proof['policy']==POLICY
    members=proof['members'];assert len(members)==3 and len(proof['pairs'])==2
    root=legacy.reference(proof['parent'])
    if parent is not None:assert root==parent,'Chain parent differs'
    candidates={};rectangles={}
    for name,item in members.items():
        assert set(item)=={'before','candidate','canonicalSHA256'}
        before=legacy.reference(item['before']);candidate=legacy.reference(item['candidate'])
        assert before.get('nativeMesh') and candidate.get('nativeMesh') and not candidate.get('patches') and not candidate.get('hydro')
        assert not marker(candidate) and not candidate['nativeMesh'].get('sourceOverlap')
        assert legacy.canonical_sha(candidate)==item['canonicalSHA256']
        assert set(before['meta']['targetUids'])<=set(candidate['meta']['targetUids'])
        candidates[name]=candidate;rectangles[name]=shapely.box(*legacy.bounds(candidate))
    names=sorted(members);touching=set()
    for i,left in enumerate(names):
        for right in names[i+1:]:
            overlap=rectangles[left].intersection(rectangles[right]);assert overlap.area==0,'Chain member interiors overlap'
            if overlap.length>0:
                assert overlap.geom_type=='LineString';touching.add(frozenset([left,right]))
    edges=[];pairs=[]
    for pairref in proof['pairs']:
        pair=legacy.reference(pairref)
        assert set(pair)=={'policy','parent','members','editRegionWKT'} and pair['policy']==legacy.POLICY
        assert pair['parent']==proof['parent'] and len(pair['members'])==2
        assert set(pair['members'])<=set(members)
        assert all(item==members[name]for name,item in pair['members'].items()),'Pair body differs from chain'
        edge=frozenset(pair['members']);assert edge not in edges,'Duplicate chain edge';edges.append(edge);pairs.append((pairref,pair))
    assert set(edges)==touching and len(touching)==2,'Every shared chain edge must have exactly one pair proof'
    degrees={n:sum(n in edge for edge in edges)for n in names}
    assert sorted(degrees.values())==[1,1,2],'Three-member chain is disconnected'
    return proof,candidates,pairs

def coordinated_boundary(node,parent):
    own=marker(node)
    if own is None or own.get('policy')!=POLICY:return PAIR_BOUNDARY(node,parent)
    assert set(own)=={'policy','proof','member'}
    proof,candidates,pairs=load_chain(own['proof'],parent)
    name=own['member'];assert name in candidates
    assert legacy.canonical_sha(node)==proof['members'][name]['canonicalSHA256'],'Chain own body changed'
    callbacks=[]
    for pairref,pair in pairs:
        if name not in pair['members']:continue
        temporary=copy.deepcopy(node)
        temporary['nativeMesh']['source']['coordinatedBoundary']=dict(policy=legacy.POLICY,proof=pairref,member=name)
        callbacks.append(PAIR_BOUNDARY(temporary,parent))
    assert callbacks
    return lambda x,y,z:any(callback(x,y,z)for callback in callbacks)

def validate_effective_coordinated_members(nodes):
    ordinary=[node for node in nodes if not marker(node) or marker(node).get('policy')!=POLICY]
    PAIR_EFFECTIVE(ordinary)
    checked=set()
    for node in nodes:
        own=marker(node)
        if not own or own.get('policy')!=POLICY:continue
        assert set(own)=={'policy','proof','member'}
        proof,candidates,_=load_chain(own['proof'])
        assert own['member'] in candidates
        assert legacy.canonical_sha(node)==proof['members'][own['member']]['canonicalSHA256']
        key=(own['proof']['path'],own['proof']['sha256'])
        if key in checked:continue
        for name,candidate in candidates.items():
            matches=[other for other in nodes if tuple(other['coarseCells'])==tuple(candidate['coarseCells']) and legacy.canonical_sha(other)==proof['members'][name]['canonicalSHA256']]
            assert len(matches)==1,'All three exact chain members must be present exactly once'
            assert marker(matches[0])==dict(policy=POLICY,proof=own['proof'],member=name),'Chain markers disagree'
        checked.add(key)

@contextmanager
def private_validator():
    """Dispatch only in this process; never modify canonical source files."""
    old_boundary,old_effective=legacy.coordinated_boundary,legacy.validate_effective_coordinated_members
    assert old_boundary is PAIR_BOUNDARY and old_effective is PAIR_EFFECTIVE
    legacy.coordinated_boundary=coordinated_boundary
    legacy.validate_effective_coordinated_members=validate_effective_coordinated_members
    try:yield
    finally:
        legacy.coordinated_boundary=old_boundary
        legacy.validate_effective_coordinated_members=old_effective
