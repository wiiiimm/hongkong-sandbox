"""Declare complete Lippo source scope; root independently verifies all versions.

This only constructs a path inventory, never an acceptance certificate or a
numeric leaf exemption. Frozen baseline scope and new receipt references remain
fully available to the independent recursive verifier.
"""
from pathlib import Path
import argparse,json
from run import ROOT,HERE,read
BASE=ROOT/'docs/astra-city/government-import'
DOCS=[
 'government-xl-complete-native-actual-position-post-block17-delta-v1-20261011',
 'xl-terrain-recovery-20261011-complete-current-native-position-inventory-v8',
 'government-xl-lippo-tower-current-complete-original-identity-diagnostic-v5-20261011',
 'government-xl-lippo-tower-only-current-complete-inputs-v5-20261011',
 'government-xl-lippo-tower-only-unchanged-current-ordinary-physical-v3-20261011',
 'government-xl-lippo-tower-all-current-native-actual-position-separation-v2-20261011',
 'government-xl-lippo-current-role-v2-ground-scope-negative-20261011',
 'government-xl-lippo-tower-only-current-complete-role-acceptance-v2-20261011',
 'government-xl-lippo-tower-only-current-complete-role-acceptance-v3-20261011']
FILES=[
 'xl-complete-native-actual-position-post-block17-delta-v1-20261011.py',
 'xl-complete-native-actual-position-post-block17-delta-v1-20261011.mjs',
 'actual_native_post_block17_census_20261011.py','test_actual_native_post_block17_census_20261011.py',
 'xl-terrain-recovery-20261011-complete-current-native-position-inventory-v8.py',
 'xl-lippo-tower-only-current-complete-inputs-v5-20261011.py','xl-lippo-tower-only-current-complete-geometry-v5-20261011.mjs',
 'xl-current-original-identity-diagnostic-20261010.py',
 'xl-lippo-tower-only-unchanged-current-ordinary-physical-v3-20261011.py',
 'xl-lippo-tower-all-current-native-actual-position-separation-v2-20261011.py',
 'exact_current_delta_catalogue_reference_binding_20261011.py','test_exact_current_delta_catalogue_reference_binding_20261011.py',
 'exact_complete_owned_bounds_runtime_ground_binding_20261011.py','test_exact_complete_owned_bounds_runtime_ground_binding_20261011.py',
 'lippo_tower_current_basic_complete_role_policy_v2_20261011.py','test_lippo_tower_current_basic_complete_role_policy_v2_20261011.py',
 'lippo_tower_current_basic_complete_role_current_bound_v2_20261011.py','test_lippo_tower_current_basic_complete_role_current_bound_v2_20261011.py',
 'lippo_tower_current_basic_complete_role_current_bound_v3_20261011.py','test_lippo_tower_current_basic_complete_role_current_bound_v3_20261011.py',
 'xl-lippo-tower-only-current-complete-role-acceptance-v2-20261011.py','xl-lippo-tower-only-current-complete-role-acceptance-v3-20261011.py',
 'xl-lippo-tower-current-basic-support-availability-budget-v2-20261011.mjs',
 'lippo_current_basic_drawn_carrier_witness_v1_20261011.mjs','test_lippo_current_basic_drawn_carrier_witness_v1_20261011.mjs',
 'xl-lippo-current-basic-solid-browser-v1-20261011.mjs',
 'xl-lippo-tower-current-basic-unchanged-stage-v1-20261011.py','xl-lippo-tower-current-basic-unchanged-stage-v2-20261011.py',
 'xl-lippo-tower-current-basic-unchanged-live-install-v1-20261011.py']
def main():
 p=argparse.ArgumentParser();p.add_argument('--baseline-scope',required=True);p.add_argument('--out',required=True);a=p.parse_args()
 paths=set(read(Path(a.baseline_scope)));assert paths
 def add(f):
  f=Path(f).resolve();assert f.is_relative_to(ROOT) and f.is_file(),str(f);paths.add(str(f.relative_to(ROOT)))
 for name in DOCS:
  for folder in [BASE/name,HERE/'local'/name]:
   for f in folder.rglob('*'):
    if f.is_file():add(f)
 for name in FILES:add(HERE/name)
 add(Path(__file__))
 accepted=read(BASE/DOCS[-1]/'result.json');assert accepted['jobId']=='86eff0b79a4a9bdaa5d7441e8e994c3dd46cc351d3428a4d06a793f71b68d542'
 assert accepted['physicalAccepted'] and accepted['acceptanceReadyForStaging'] and not accepted['publication'] and accepted['newlyInstalled']==0
 for r in accepted['evidenceRefs']:add(ROOT/r['path'])
 for name in DOCS[:6]:
  receipt=read(BASE/name/'result.json')
  for r in receipt['evidenceRefs']:add(ROOT/r['path'])
 for path in paths:assert (ROOT/path).is_file(),path
 Path(a.out).write_text(json.dumps(sorted(paths),indent=2)+'\n')
 print(json.dumps(dict(paths=len(paths),pathInventoryOnly=True,independentlyVerified=False,installationApproved=False)))
if __name__=='__main__':main()
