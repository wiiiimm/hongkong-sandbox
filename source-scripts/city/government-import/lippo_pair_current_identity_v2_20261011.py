"""Route only the named Lippo P and ordinary T identities; no physical exemptions."""
from exact_original_georef_cell_identity_20261009 import verify_files as ordinary, POLICY
from lippo_current_bound_six_roof_identity_v4_20261011 import verify_files as named, OWN, TOWER
from lippo_three_original_current_inventory_20261010 import EXPECTED
UIDS=frozenset([OWN,TOWER])
def verify_files(row,context,local):
 assert row['uid'] in UIDS and context['uid']==row['uid']
 assert row['modelId']==EXPECTED[row['uid']][0] and row['sourceSHA256']==EXPECTED[row['uid']][1]
 assert row['triangles']==EXPECTED[row['uid']][2]
 return named(row,context,local) if row['uid']==OWN else ordinary(row,context,local)
