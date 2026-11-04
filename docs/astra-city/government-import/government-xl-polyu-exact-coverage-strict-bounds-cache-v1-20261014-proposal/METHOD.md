# Bounded exact Fraction extrema cache for coverage-v2

This isolated draft leaves the active finite worker, first coverage-result-cache packet, canonical modules and all inputs unchanged. It is code-only preparation; no tests, imports, source calculations, worker/lease/DB calls or live mutation were executed by this author.

Coverage-v2 subtract recomputes polygon AND triangle Fraction extrema for every remaining-piece/ground-triangle call. Most pieces can survive many strictly disjoint later triangles. The new wrapper retains the same canonical coverage function bytecode in copied globals, changing only its local subtract dispatch. It caches exact existing extrema, not rounded bounds. A strict `<` separation identical to the canonical guard returns the SAME `[poly]` object. All touching/overlapping cases invoke the unchanged canonical subtract and preserve its returned objects, order, clipping and rational arithmetic. Thus exact uncovered areas, covered interval endpoints, gap ordering, remaining-piece counts and the full coverage dictionary remain identical; no new admission test is introduced.

Triangle extrema are prepared once for the current triangle object. Polygon extrema are in an LRU capped at4096 strong references; this prevents id reuse while cached. Replaced polygons are removed immediately. Eviction changes cost only. Each full coverage call creates a fresh owned cache. Canonical coverage creates its own Fraction triangle/fragment lists and never mutates those lists after handing them to subtract, so cached identities are internally immutable; the helper is not a public general-purpose cache for caller-mutated lists. Counters stay separate from the unchanged proof dictionary.

The approach always avoids repeated triangle-extrema calculation on dense calls. Polygon-extrema savings depend on working-set size; an oversized fragment set can evict entries and limit benefit. It does not reduce actual intersections/clipping, source/ground candidates or bounds/coverage/clearance policy. It is not a claim of an actual-source speedup yet. This cache can later be composed with the first exact XZ-result cache by changing its miss evaluator after ROOT review; no active code or handed-off packet is edited here.

Twelve synthetic-only fixtures compare FULL canonical results, including genuine area holes/piece counts, exact boundary touches, strict disjoint object identity, non-dyadic gaps, duplicate/winding/order variations, projected intervals/points, degenerate terrain, bounded eviction, signed-zero inputs, source/list/module nonmutation and invalid inputs. The focused strict-disjoint fixture also verifies extrema are computed once on repeated unchanged objects. ROOT must execute these before any bounded saved-input comparison or integration.

```sh
PYTHONDONTWRITEBYTECODE=1 /tmp/astra-city-venv/bin/python source-scripts/city/government-import/test_exact_coverage_strict_bounds_cache_v1_draft_20261014.py -v
```

No normal worker, resume caller or acceptance binding is part of this packet. Any future serial replacement must preserve exact completed chunks/lifecycle and use fresh reviewed code/input pins. No source geometry/assets, candidate surface, current scene, numerical threshold or installation requirement changes.
