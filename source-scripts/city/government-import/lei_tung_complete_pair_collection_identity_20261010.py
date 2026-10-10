"""Two-original-only runtime collection policy; no standalone original path."""
from run import ROOT,digest
from lei_tung_lower_platform_current_bound_identity_20261010 import verify_files as paired_verify,UID,PLATFORM
UIDS={UID,PLATFORM};POLICY='mandatory-two-original-lei-tung-complete-current-identity-v1'
def verify_files(row,context,local):
 assert row['uid'] in UIDS
 raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];dest=local/'assets'/(row['sourceSHA256']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():assert dest.read_bytes()==raw
 else:dest.write_bytes(raw)
 proof=paired_verify(row,context,local);assert proof['mandatoryOriginalRuntimeUIDs']==[UID,PLATFORM] and proof['standaloneOriginalImportAccepted'] is False
 return {**proof,'individualIdentityPolicy':proof['policy'],'policy':POLICY,'mandatoryCompleteOriginalRuntimeAssemblyOnly':True}
