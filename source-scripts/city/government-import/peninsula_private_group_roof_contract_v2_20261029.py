"""Attach only the exact runtime declaration to the reviewed private experiment."""
from peninsula_private_group_roof_contract_v1_20261029 import apply as original_apply,OWNER

def apply(models,forms,review):
    out=original_apply(models,forms,review)
    owner=next(m for m in out if m['uid']==OWNER)
    owner['reviewedOsmRoofReplacement']=dict(policy='exact-original-peninsula-entrance-roof-v1',sourceSHA256=owner['sha256'],roofFormSHA256=review['roofFormSHA256'])
    return out
