# Independent regional integration review

GPT-6 Astra review of the shared regional renderer, package validation, assembler, generated place module, search and aerial-only movement guards. Production files were reviewed read-only. The urban payload remained frozen during this review. Bridge implementation was outside this review's scope; its later UI appears incidentally in the refreshed screenshots.

Two concrete defects were found, reported to the root agent, patched there and independently verified:

1. **Late responses recreated geometry after disposal.** The controlled lifecycle fixture originally produced one detached mesh/cache after `dispose()`. The same fixture now reports zero meshes, cached tiles and retained packages when the delayed response completes. See [lifecycle.json](lifecycle.json).
2. **Procedural trees covered mapped sports courts.** Victoria Park initially had 80 generated tree centres inside source pitch polygons. The new surface exclusions reduce that number to zero, leaving 288 trees elsewhere in the park. The actual city was tested with its urban response deliberately delayed until the original trees existed: late remasking works. Travelling to Tin Shui Wai and Sha Tin evicted the park tile; returning also produced zero trees in the pitches. See [tree-mask-browser.json](tree-mask-browser.json) and [tree-overlap.json](tree-overlap.json).

The refreshed [desktop view](victoria-park-masked-1440x1000.png) and [390 px mobile view](victoria-park-masked-mobile-390x844.png) were inspected visually. Courts are clear, ordinary park trees remain, and the bilingual title fits without obscuring the minimap.

The earlier [interaction verification](verification.json) covers six urban views: Victoria Park, Repulse Bay, Lai Chi Kok, Kai Tak runway waterfront, Nan Lian Garden and Cha Kwo Ling. Actual WebGL checks passed for local-detail visibility, section-number and Traditional Chinese search on mobile, a clear Nan Lian walking arrival, aerial-only button and keyboard guards, and bounded detail geometry. There were no unexpected browser errors. The `urban-*.png`, `*-surfaces-hidden.png` and `*-surfaces-visible.png` files record the initial inspection before the procedural-tree fix; the two `victoria-park-masked-*` files show the corrected result.

[The seam audit](seams.json) found no coincident cross-package footprints among the 2,923 current surfaces. It checks all pairs with over 95% overlap of the smaller polygon and over 1 m² overlap, regardless of source IDs. This establishes no duplicate imported footprint under that criterion; it does not prove complete coastline or section coverage.

Reproduce the focused evidence from the feature-worktree root:

```sh
node 3d-viewer/city/tests/regional-review.mjs
node docs/astra-city/regional/review/lifecycle.mjs
node docs/astra-city/regional/review/tree-overlap.mjs
node docs/astra-city/regional/review/tree-mask-browser.mjs
/private/tmp/astra-city-venv/bin/python docs/astra-city/regional/review/seams.py
```

The tree-mask browser fixture appends a read-only getter to its own intercepted app-script response so it can inspect existing instance matrices. It does not edit the app on disk or change city behaviour. These checks are focused regression evidence, not full architectural, coastline or walking-route acceptance of any section. No blocking regional findings remain in this reviewed scope.
