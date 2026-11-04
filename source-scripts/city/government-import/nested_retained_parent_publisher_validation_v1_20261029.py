"""Compose existing nested-parent proofs with canonical publisher staging.

Private process context only; no publication or architectural acceptance.
Every canonical grid/native/alignment/overlap assertion is retained. Nested
coordinated membership gets an additional complete sibling-membership check.
"""
import ast
import inspect
import textwrap
from contextlib import contextmanager
from pathlib import Path
from disjoint_nested_append_contract_v1_20261029 import private_validator as append_validator
from nested_terrain_patch_validation_v1_20261027 import validate_patch as nested_validate

HERE = Path(__file__).resolve().parent
INTEGRATION = HERE.parent / 'island-detail-integration'


def function_tree(path, name):
    tree = ast.parse(path.read_text())
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)


def unchanged_checks():
    canonical = function_tree(INTEGRATION / 'publish.py', 'validate_patch')
    nested = function_tree(HERE / 'nested_terrain_patch_validation_v1_20261027.py', 'validate_patch')
    extra = nested.body.pop()
    assert ast.dump(extra) == ast.dump(ast.parse('validate_effective_coordinated_members(children)').body[0])
    assert ast.dump(canonical) == ast.dump(nested), 'Canonical patch checks changed'
    canonical_native = function_tree(INTEGRATION / 'native_terrain_validation.py', 'validate_native_mesh')
    nested_native = function_tree(HERE / 'nested_native_terrain_validation_v1_20261027.py', 'validate_native_mesh')
    changed = 0
    for node in ast.walk(nested_native):
        if isinstance(node, ast.ImportFrom) and node.module == 'nested_coordinated_native_boundary_v1_20261027':
            node.module = 'coordinated_native_boundary'
            changed += 1
    assert changed == 1 and ast.dump(canonical_native) == ast.dump(nested_native), 'Canonical native checks changed'


@contextmanager
def private_validator(publisher):
    unchanged_checks()
    old = publisher.validate_patch
    assert ast.dump(ast.parse(textwrap.dedent(inspect.getsource(old))).body[0]) == ast.dump(function_tree(INTEGRATION / 'publish.py', 'validate_patch'))
    publisher.validate_patch = nested_validate
    try:
        with append_validator():
            yield
    finally:
        publisher.validate_patch = old
