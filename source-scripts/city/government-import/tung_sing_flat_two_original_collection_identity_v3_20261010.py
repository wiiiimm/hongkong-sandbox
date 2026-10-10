"""Exact two-original binding with unchanged-byte local decode preparation."""
from run import ROOT,digest
from tung_sing_interior_two_original_collection_identity_v2_20261010 import verify_files as previous_verify,UIDS,POLICY
def verify_files(row,context,local):
 raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']
 dest=local/'assets'/(row['sourceSHA256']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():assert dest.read_bytes()==raw
 else:dest.write_bytes(raw)
 return previous_verify(row,context,local)
