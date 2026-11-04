"""Exact source-specific identity adapters; no spatial thresholds changed."""
from direct_shared_osm_geographic_identity import verify_files as podium_verify
from routed_original_cell_identity import verify_files as tower_verify
POLICY='hoi-fu-yu-independent-original-identity-v1'
def verify_files(row,context,local):
    assert row['uid'] in {'landsd/177604:0','landsd/177605:0'}
    p=(podium_verify if row['uid']=='landsd/177604:0' else tower_verify)(row,context,local)
    p={**p,'underlyingIdentityPolicy':p['policy'],'policy':POLICY}
    if row['uid']=='landsd/177605:0':p['completeGroupForms']=[row['source']['building']]
    return p
