"""Bounded exact-output acceleration of coverage-v2 strict disjoint pruning.

Only reuse unchanged Fraction extrema; touching/overlapping cases execute the
canonical subtract unchanged. No source filtering, ordering or polygon edits.
"""
from collections import OrderedDict
from types import FunctionType
import exact_original_projection_coverage_v2_20261010 as canonical

def bounds(poly):
    return tuple((min(p[k]for p in poly),max(p[k]for p in poly))for k in range(2))

class CachedSubtractor:
    def __init__(self,max_polygons=4096):
        assert type(max_polygons)is int and max_polygons>0
        self.max_polygons=max_polygons;self.polygons=OrderedDict()
        self.last_triangle=None;self.last_triangle_bounds=None
        self.calls=0;self.disjoint=0;self.canonical_calls=0
        self.polygon_bounds_computed=0;self.triangle_bounds_computed=0
    def polygon_bounds(self,poly):
        key=id(poly)
        if key in self.polygons:
            stored,b=self.polygons[key];assert stored is poly
            self.polygons.move_to_end(key);return b
        b=bounds(poly);self.polygon_bounds_computed+=1
        if len(self.polygons)>=self.max_polygons:self.polygons.popitem(last=False)
        # A strong reference prevents object-id reuse while cached. Capacity
        # bounds the retained polygons; eviction never affects geometry.
        self.polygons[key]=(poly,b);return b
    def __call__(self,poly,triangle):
        self.calls+=1;b=self.polygon_bounds(poly)
        if triangle is not self.last_triangle:
            self.last_triangle=triangle;self.last_triangle_bounds=bounds(triangle)
            self.triangle_bounds_computed+=1
        t=self.last_triangle_bounds
        if any(b[k][1]<t[k][0]or t[k][1]<b[k][0]for k in range(2)):
            self.disjoint+=1;return [poly]
        self.canonical_calls+=1;out=canonical.subtract(poly,triangle)
        # Never keep obsolete replaced fragments. All returned objects/order
        # remain exactly those produced by canonical clipping.
        if not any(q is poly for q in out):self.polygons.pop(id(poly),None)
        return out

def executor(max_polygons=4096):
    """A full coverage call owns its cache; return result and cost counters."""
    def run(source,ground):
        subtract=CachedSubtractor(max_polygons);namespace=dict(canonical.exact_coverage.__globals__)
        namespace['subtract']=subtract
        function=FunctionType(canonical.exact_coverage.__code__,namespace,canonical.exact_coverage.__name__,canonical.exact_coverage.__defaults__,canonical.exact_coverage.__closure__)
        result=function(source,ground)
        counters=dict(calls=subtract.calls,strictlyDisjoint=subtract.disjoint,canonicalSubtractCalls=subtract.canonical_calls,polygonBoundsComputed=subtract.polygon_bounds_computed,triangleBoundsComputed=subtract.triangle_bounds_computed,maxCachedPolygons=max_polygons)
        return result,counters
    return run
