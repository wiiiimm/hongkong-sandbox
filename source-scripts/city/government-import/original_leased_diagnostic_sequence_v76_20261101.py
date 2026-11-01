"""Use existing exact cached-terrain schema binding in the unchanged diagnostic runner.
No new geometry recipe, acceptance rule, budget, lease or publication permission.
"""
from run import HERE
from primrose_compound_foundation_v2_20261015 import module
if __name__=='__main__':
 runner=module('original_diagnostic_v74_with_cached_terrain_binding',HERE/'original_leased_diagnostic_sequence_v74_20261101.py')
 runner.ALLOWED.add('cached_original_terrain_candidate_binding_v1_20261026.py')
 runner.main()
