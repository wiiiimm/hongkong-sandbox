"""Byte-identical optimization of the immutable original make_patch function.

Only distant parent triangles are excluded from the broad-phase lookup. The
original clipping predicates, arithmetic, source ordering, sampler, guards and
output metadata remain unchanged. This helper provides zero acceptance credit.
"""
import inspect,hashlib
from parent_cell_clip_broad_phase_20261010 import ParentCellClipIndex
def indexed_builder(original_module):
    source=inspect.getsource(original_module.make_patch)
    old='[exact.parent_clip(poly,pt) for pt in pcells]'
    assert source.count(old)==1 and source.count('    regions=')==1
    replacement=source.replace('    regions=','    parent_index=ParentCellClipIndex(pcells)\n    regions=',1).replace(old,'parent_index.clip(poly,exact.parent_clip)',1)
    namespace=dict(original_module.make_patch.__globals__);namespace['ParentCellClipIndex']=ParentCellClipIndex
    exec(compile(replacement,'<indexed-original-make_patch-20261010>','exec'),namespace)
    return namespace['make_patch'],{'originalFunctionSourceSHA256':hashlib.sha256(source.encode()).hexdigest(),
        'indexedFunctionSourceSHA256':hashlib.sha256(replacement.encode()).hexdigest(),
        'onlyChange':'Conservative parent-cell candidate lookup, identical original clipping arithmetic and stable candidate order',
        'acceptanceChange':False,'sourceGeometryChanges':0}
