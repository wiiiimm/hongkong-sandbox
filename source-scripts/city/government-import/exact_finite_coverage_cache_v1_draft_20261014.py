"""Isolated exact-result coverage memoisation; no canonical module mutation.

The only skipped work is an identical ordered-XZ coverage calculation. Source
and ground XYZ hashes are freshly rebound, while every exact geometric field
(including gap area, interval details and remaining-piece count) is retained.
"""
from collections import OrderedDict
from types import FunctionType, SimpleNamespace
import builtins,copy,hashlib
import numpy as np
import exact_original_projection_coverage_v2_20261010 as coverage
import exact_original_face_conservative_clearance_v5_20261010 as coarse
import exact_original_paired_finite_clearance_v3_20261011 as paired
import exact_original_paired_finite_clearance_v2_20261010 as refinement
import upton_parent_tin_regression_bookkeeping_v1_20261012 as bookkeeping

def clone(function, overrides):
    namespace=dict(function.__globals__);namespace.update(overrides)
    result=FunctionType(function.__code__,namespace,function.__name__,function.__defaults__,function.__closure__)
    result.__kwdefaults__=copy.copy(function.__kwdefaults__)
    return result

class ExactCoverageCache:
    def __init__(self,max_entries=64,max_key_bytes=16*1024*1024):
        assert type(max_entries)is int and max_entries>0
        assert type(max_key_bytes)is int and max_key_bytes>0
        self.max_entries=max_entries;self.max_key_bytes=max_key_bytes
        self.entries=OrderedDict();self.key_bytes=0;self.hits=0;self.misses=0
    def __call__(self,source_face,ground_triangles):
        source=np.asarray(source_face,float);ground=np.asarray(ground_triangles,float)
        assert source.shape==(3,3)and ground.ndim==3 and ground.shape[1:]==(3,3)
        assert np.isfinite(source).all()and np.isfinite(ground).all()
        # Full ordered bytes, not a digest or coordinate tolerance, are the
        # cache key. Keep winding, duplicate slots, signed zero and all facets.
        key=(source[:,[0,2]].tobytes(),ground[:,:,[0,2]].tobytes())
        if key in self.entries:
            self.hits+=1;self.entries.move_to_end(key);result=copy.deepcopy(self.entries[key])
        else:
            self.misses+=1;result=coverage.exact_coverage(source,ground)
            size=sum(map(len,key))
            if size<=self.max_key_bytes:
                while self.entries and (len(self.entries)>=self.max_entries or self.key_bytes+size>self.max_key_bytes):
                    old,_=self.entries.popitem(last=False);self.key_bytes-=sum(map(len,old))
                self.entries[key]=copy.deepcopy(result);self.key_bytes+=size
        result['sourceFaceSHA256']=hashlib.sha256(source.tobytes()).hexdigest()
        result['completeGroundSHA256']=hashlib.sha256(ground.tobytes()).hexdigest()
        return result

def executor(max_entries=64,max_key_bytes=16*1024*1024):
    """Return a cloned canonical finite_record and its owned bounded cache."""
    memo=ExactCoverageCache(max_entries,max_key_bytes)
    cached_coarse=clone(coarse.verify,dict(exact_coverage=memo))
    cached_prism=clone(paired.optimized_ordinary_prism,dict(exact_coverage=memo))
    cached_refine=clone(refinement.refine,dict(exact_coverage=memo))
    # Canonical verify performs a local import of refine. Redirect exactly that
    # one local dispatch in copied builtins; never replace sys.modules/globals.
    original_import=builtins.__import__
    def owned_import(name,globals=None,locals=None,fromlist=(),level=0):
        if name==refinement.__name__ and tuple(fromlist)==('refine',)and level==0:
            return SimpleNamespace(refine=cached_refine)
        return original_import(name,globals,locals,fromlist,level)
    owned_builtins=dict(vars(builtins));owned_builtins['__import__']=owned_import
    cached_paired=clone(paired.verify,dict(optimized_ordinary_prism=cached_prism,__builtins__=owned_builtins))
    record=clone(bookkeeping.finite_record,dict(coarse=cached_coarse,paired=cached_paired))
    return record,memo
