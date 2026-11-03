"""Exact sixteen-member terrain validation composed with every existing policy.

Only the frozen Silvercord/Lippo graph is recognised. This is a geometry policy,
never source/model/physical/publication approval. Numerical kernels are unchanged.
"""
import copy
import gzip
import hashlib
import json
from collections import Counter
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = 'docs/astra-city/government-import/'
ADMISSION = BASE+'government-xl-silvercord-lippo-complete-floor-admission-v1-20261103/'
POLICY = 'private-silvercord-lippo-exact-sixteen-member-floor-return-v1'
PROOF = dict(path=ADMISSION+'private-graph-proof.json',sha256='d4c5f76d303ed319796dae5f261332a9a7a7540a1f793bd778160be6958df95b')
GRAPH = dict(path=BASE+'government-xl-silvercord-lippo-graph-surface-diagnostic-v4-20261103/summary.json',sha256='16c0ff35907f1484935610d1e737798154d4ed8efdb830208ee374697812483f')
SUCCESSOR_SHA = '7b75a844baf16ab3c7013c61062dfc0d82ca911d7bcc06ebbe42691fa0218b0b'
SUCCESSOR = dict(path=ADMISSION+'unapproved-successor-terrain.json',sha256=SUCCESSOR_SHA)
ARCHIVE = dict(path=BASE+'government-xl-silvercord-lippo-private-floor-restorable-payloads-v1-20261103/'+SUCCESSOR_SHA+'.bytes.gz',sha256='994651d159293a782d64ad9738447b063c70d56b35f01b61ba81d1fe8ea6866b')
NAMES = {'12','15','17',*(str(i) for i in range(18,30)),'north'}


def marker(node):
    return node.get('nativeMesh',{}).get('source',{}).get('coordinatedBoundary')


def walk(nodes):
    for node in nodes:
        yield node
        yield from walk(node.get('patches',[]))


def own(node):
    return marker(node) is not None and marker(node).get('policy') == POLICY


def verify_body(node,expected,proof_ref=PROOF):
    item = marker(node)
    assert item and set(item) == {'policy','proof','member'}
    assert item['policy'] == POLICY and item['proof'] == proof_ref
    assert item['member'] in expected,'Unknown exact floor-return member'
    body = copy.deepcopy(node)
    body['nativeMesh']['source'].pop('coordinatedBoundary')
    assert body == expected[item['member']],'Exact floor-return body changed'
    return item['member']


def verify_members(nodes,expected,proof_ref=PROOF,*,recursive):
    rows = list(walk(nodes)) if recursive else nodes
    names = [verify_body(n,expected,proof_ref) for n in rows if own(n)]
    assert Counter(names) == Counter({name:1 for name in expected}),'Exact effective floor-return members missing/duplicated'
    return len(names)


class ExactContract:
    def __init__(self):
        self.pins = {}
        proof = self.reference(PROOF)
        assert proof['policy'] == POLICY and set(proof['members']) == NAMES
        assert proof['candidateJobId'] == '458a0da1a2cf054ec39c382e4658ecf24819c743763e908b44848073255f5685'
        assert proof['graphJobId'] == '31d5d477784b974d92fa6c8128de9f74079a1bd774232eb2f88a9e1e5fefdfce'
        self.nodes = {name:self.reference(ref) for name,ref in proof['members'].items()}
        self.root = self.reference(proof['root'])
        self.reference(proof['priorParent'])
        if (ROOT/SUCCESSOR['path']).is_file():
            self.parent = self.reference(SUCCESSOR)
        else:
            raw = self.bytes(ARCHIVE)
            decoded = gzip.decompress(raw)
            assert len(decoded) == 42872054 and hashlib.sha256(decoded).hexdigest() == SUCCESSOR_SHA
            self.parent = json.loads(decoded)
        graph = self.reference(GRAPH)
        assert graph['allFiniteSeamsPassed'] and graph['allMemberSurfaceChecksPassed']
        assert graph['connectedMemberCount'] == 16 and len(graph['edges']) == 22
        from fuying_whole_parent_five_boundary_v1_20261029 import finite_callback
        self.callbacks = {name:[] for name in NAMES}
        seen = set()
        for edge in graph['edges']:
            left,right = edge['members']
            assert left != right and {left,right} <= NAMES and frozenset([left,right]) not in seen
            seen.add(frozenset([left,right]))
            pair = {left:self.nodes[left],right:self.nodes[right]}
            for name in pair:
                self.callbacks[name].append(finite_callback(pair,name))
        assert all(self.callbacks.values())

    def bytes(self,ref):
        assert set(ref) == {'path','sha256'}
        path = (ROOT/ref['path']).resolve()
        assert path.is_relative_to(ROOT)
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == ref['sha256'],'Registered terrain evidence changed'
        assert self.pins.setdefault(path,ref['sha256']) == ref['sha256']
        return raw

    def reference(self,ref):
        return json.loads(self.bytes(ref))

    def boundary(self,node,parent):
        name = verify_body(node,self.nodes)
        assert parent == (self.root if name == 'north' else self.parent),'Different actual registered parent'
        return lambda x,y,z:any(callback(x,y,z) for callback in self.callbacks[name])

    def verify_effective(self,nodes,*,root):
        expected = self.nodes if root else {n:p for n,p in self.nodes.items() if n != 'north'}
        count = verify_members(nodes,expected,recursive=root)
        if root:
            def placed(children,parent=None):
                for node in children:
                    if own(node):
                        name = marker(node)['member']
                        if name == 'north':
                            assert parent is None,'North member must be an actual top-level patch'
                        else:
                            assert parent == self.parent,'Nested member has a different effective parent'
                    placed(node.get('patches',[]),node)
            placed(nodes)
        return count

    def verify_inputs(self):
        for path,sha in self.pins.items():
            assert hashlib.sha256(path.read_bytes()).hexdigest() == sha,'Registered terrain input changed during validation'


@contextmanager
def registered_validator(legacy):
    """Compose after existing pair/chain/five-member handlers; restore all hooks."""
    import nested_coordinated_native_boundary_v1_20261027 as nested
    import nested_terrain_patch_validation_v1_20261027 as validator
    old = (legacy.coordinated_boundary,legacy.validate_effective_coordinated_members,
           nested.coordinated_boundary,nested.validate_effective_coordinated_members,
           validator.validate_effective_coordinated_members)
    contract = None
    def get():
        nonlocal contract
        if contract is None:
            contract = ExactContract()
        return contract
    def dispatch(node,parent,fallback):
        return get().boundary(node,parent) if own(node) else fallback(node,parent)
    def effective(nodes,fallback,*,root):
        considered = list(walk(nodes)) if root else nodes
        if any(own(node) for node in considered):
            get().verify_effective(nodes,root=root)
        return fallback([node for node in nodes if not own(node)])
    legacy.coordinated_boundary = lambda n,p:dispatch(n,p,old[0])
    legacy.validate_effective_coordinated_members = lambda ns:effective(ns,old[1],root=True)
    nested.coordinated_boundary = lambda n,p:dispatch(n,p,old[2])
    nested.validate_effective_coordinated_members = lambda ns:effective(ns,old[3],root=False)
    validator.validate_effective_coordinated_members = lambda ns:effective(ns,old[4],root=False)
    try:
        yield
        if contract is not None:
            contract.verify_inputs()
    finally:
        (legacy.coordinated_boundary,legacy.validate_effective_coordinated_members,
         nested.coordinated_boundary,nested.validate_effective_coordinated_members,
         validator.validate_effective_coordinated_members) = old
