"""Exact installed-entry transition: only South availability, plus two originals."""
from copy import deepcopy
from original_independent_atomic_contract_v1_20261027 import manifest_triple_transition
from north_pair_publisher_hooks_v1_20261027 import SOURCES,EXISTING

def verify(before,after,new,group):
 assert len(before)==len({m['uid']for m in before})==6989
 assert len(after)==len({m['uid']for m in after})==6991
 assert {m['uid']:m['sha256']for m in new}==SOURCES
 assert group==sorted([*SOURCES,EXISTING])
 expected=deepcopy(before)
 old=next(m for m in expected if m['uid']==EXISTING)
 assert not old.get('activationGroup')or old['activationGroup']==[EXISTING]
 old['activationGroup']=group
 assert after==expected+new,'Only the reviewed South availability field and two originals may change'
 return True
