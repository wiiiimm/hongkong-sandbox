"""Admit existing immutable source selection refresh to the explicit leased diagnostic runner.
All existing lease, hash, source and no-publication guards remain unchanged.
"""
from run import HERE
from primrose_compound_foundation_v2_20261015 import module
if __name__=='__main__':
 runner=module('original_diagnostic_v74_with_selection_refresh',HERE/'original_leased_diagnostic_sequence_v74_20261101.py')
 runner.ALLOWED.add('selected_original_refresh_selection_v1.py')
 runner.main()
