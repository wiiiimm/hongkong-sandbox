"""One isolated executor: canonical coverage-result cache with bounds-cached misses."""
from types import SimpleNamespace
import exact_finite_coverage_cache_v1_draft_20261014 as result_cache
import exact_coverage_strict_bounds_cache_v1_draft_20261014 as bounds_cache

class CombinedMemo:
    def __init__(self,max_entries,max_key_bytes,max_polygons):
        self.base=result_cache.ExactCoverageCache(max_entries,max_key_bytes)
        self.bounds_totals={}
        def miss(source,ground):
            proof,counters=bounds_cache.executor(max_polygons)(source,ground)
            for key,value in counters.items():
                if key=='maxCachedPolygons':self.bounds_totals[key]=value
                else:self.bounds_totals[key]=self.bounds_totals.get(key,0)+value
            return proof
        self.lookup=result_cache.clone(result_cache.ExactCoverageCache.__call__,dict(coverage=SimpleNamespace(exact_coverage=miss)))
    def __call__(self,source,ground):return self.lookup(self.base,source,ground)
    def __getattr__(self,name):return getattr(self.base,name)

def executor(max_entries=64,max_key_bytes=16*1024*1024,max_polygons=4096):
    assert type(max_polygons)is int and max_polygons>0
    def memo_factory(entries,key_bytes):return CombinedMemo(entries,key_bytes,max_polygons)
    build=result_cache.clone(result_cache.executor,dict(ExactCoverageCache=memo_factory))
    return build(max_entries,max_key_bytes)
