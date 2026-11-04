# Exact finite result caching draft

The active finite worker and every canonical kernel stay untouched. This isolated draft is code preparation only: no imports, tests, source calculations, leases, DB, signalling or worker replacement were executed by the draft author.

The current complete finite executor first calls conservative v5, which computes coverage-v2. If coverage passes but the conservative clearance bound is insufficient, paired v3 computes the same coverage in optimized_ordinary_prism; its v2 refine then computes it again. All three calls bind the same full ordered source/selected-ground tuples. Thus two expensive exact subtraction passes can be avoided without changing any result. Coverage-v2 uses only XZ coordinates geometrically; its only Y-dependent fields are full XYZ source/ground SHA bindings.

The adapter retains the exact canonical coverage calculation on a miss. A bounded LRU key contains COMPLETE ordered binary64 source and ground XZ bytes: no digest-only collision assumption, tolerance, facet filtering, reorder, deduplication or input shortening. The key preserves winding, repeated slots and signed zero. On a hit the full canonical result is copied, and only the full XYZ source/ground hashes are freshly rebound to the actual call. Every exact uncovered area, interval, remaining-positive-piece count and candidate count therefore stays identical. Identical XZ with different Y can reuse coverage geometry but never reuse clearance or a source/ground XYZ identity.

FunctionType clones retain the canonical finite_record, conservative, optimized-prism, refine and paired-verify bytecode. Their globals are owned copies. The paired verify local import of refine is redirected only for that exact module/fromlist in its copied builtins, without changing builtins or sys.modules. All actual prism, column, height, coverage and -.5m policy functions remain canonical. Cache hits can reduce three coverage evaluations to one for paired faces; they do not skip any gap/column arithmetic. First-time pathological coverage remains unchanged. No speedup percentage or actual-source equivalence is claimed before ROOT synthetic verification and any separately reviewed bounded actual comparison.

The cache has at most 64 entries and 16MiB of complete key bytes; over-budget keys are calculated normally without caching. Eviction changes cost only. Source/ground inputs and returned cached dictionaries are protected from cross-call mutation by copy semantics.

Twelve synthetic-only tests compare COMPLETE finite_record dictionaries with canonical results: paired triple-call reuse, real below-bound failure, uncovered area/piece count, degenerate segment/point projections, collapsed ground-column refinement, Y-only hash rebinding, full order/duplicates, changed projection/signed zero, return mutation, eviction/module/builtins nonmutation and invalid inputs. These tests are unexecuted here. No new acceptance predicate, geometry, terrain asset or architectural interpretation is introduced.

ROOT may review/run:

```sh
PYTHONDONTWRITEBYTECODE=1 /tmp/astra-city-venv/bin/python source-scripts/city/government-import/test_exact_finite_coverage_cache_v1_draft_20261014.py -v
```

There is no production resume caller in this packet. Any use with saved source records requires separately reviewed exact full-result comparison, closure/pins, observed old terminal/released lifecycle and honest chunk reuse; this draft never authorises replacing or restarting the live worker. A later source-footprint spatial index is not included: filtering bbox-disjoint triangles can change the conservative maximum-height bound, while deleting nonintersecting coverage triangles can change diagnostic subdivision/piece counts. Those are distinct proofs, not silently equivalent optimisations.
