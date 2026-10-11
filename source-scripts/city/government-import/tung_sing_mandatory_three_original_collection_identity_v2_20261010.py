"""Three complete original assets only; the lower commercial platform is mandatory.

Both reviewed identity interpretations remain current/source bound. This
collection policy supplies no physical, support, collision or install credit.
"""
from run import ROOT,digest
from tung_sing_three_original_tower_current_bound_identity_v2_20261010 import verify_files as tower_verify
from lei_tung_lower_platform_current_bound_identity_v2_20261010 import verify_files as paired_verify,UID,PLATFORM
TOWER='landsd/53800:0';UIDS={TOWER,UID,PLATFORM};POLICY='mandatory-three-original-tung-sing-commercial-platform-current-identity-v1'
def verify_files(row,context,local):
 assert row['uid'] in UIDS
 raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];dest=local/'assets'/(row['sourceSHA256']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():assert dest.read_bytes()==raw
 else:dest.write_bytes(raw)
 proof=(tower_verify if row['uid']==TOWER else paired_verify)(row,context,local);assert proof['passed']
 if row['uid']!=TOWER:assert proof['mandatoryOriginalRuntimeUIDs']==[UID,PLATFORM] and proof['standaloneOriginalImportAccepted'] is False
 return {**proof,'individualIdentityPolicy':proof['policy'],'policy':POLICY,'mandatoryOriginalRuntimeUIDs':sorted(UIDS),'standaloneOriginalImportAccepted':False,'mandatoryCompleteOriginalRuntimeAssemblyOnly':True,'collectionPhysicalCredit':False}
