"""Exactly two independently source-bound originals, no physical role exemptions."""
from exact_original_georef_cell_identity_20261009 import verify_files as ordinary,POLICY
from one_peking_current_bound_installed_foreign_identity_v5_20261010 import verify_files as named

def verify_files(row,context,local):
 assert row['uid'] in ['landsd/233985:0','landsd/240487:0']
 return named(row,context,local) if row['uid']=='landsd/233985:0' else ordinary(row,context,local)
