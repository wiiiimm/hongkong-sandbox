"""Prepare unchanged original bytes for current identity replays; no source edits."""
from run import ROOT,digest
from aqua_current_bound_overhead_identity_v3_20261010 import verify_files as bound_verify
from aqua_named_original_overhead_identity_20261010 import UID,POLICY,SOURCE_SHA
UIDS={UID}
def verify_files(row,context,local):
 raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==SOURCE_SHA==row['sourceSHA256']
 dest=local/'assets'/(SOURCE_SHA+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():assert dest.read_bytes()==raw
 else:dest.write_bytes(raw)
 return bound_verify(row,context,local)
