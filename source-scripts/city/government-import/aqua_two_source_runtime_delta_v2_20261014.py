"""Only the explicitly reviewed source namespace/scanner substitutions."""
def assert_exact_delta(old,new):
    expected=old.replace('aqua_marine193086138449_current_actual_attributes_v1_20261014.mjs','aqua_marine193086138449_current_actual_attributes_v2_20261014.mjs').replace('literal_production_module_dependency_closure_20261010.mjs','exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs')
    assert old.count('literal_production_module_dependency_closure_20261010.mjs')==2
    assert expected.encode()==new.encode()
    return True
