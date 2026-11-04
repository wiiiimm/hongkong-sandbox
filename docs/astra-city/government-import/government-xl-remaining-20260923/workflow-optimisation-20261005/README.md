# Held-model workflow continuation — 5 October 2026

Codex root used AI for reusable code/workflow analysis only. Scripts made zero
external AI calls; no per-building architectural AI review or geometry changes.

The new metadata-only dependency preflight routes all nine held pilot sources
before expensive terrain/browser work. Citywalk immediately exposes five exact
installed Vision City fallback dependents. The other eight have no such catalogue
dependency blocker; their existing source/terrain holds remain. Passing this
preflight is not acceptance. It reuses the publisher's dependency-state semantics,
reports missing/transitive/cyclic native supports, and never edits metadata.

Eleven exact original source/support pairs were checked under a fresh reservation,
including the five Vision City towers, Festival Walk, two Parkview blocks, Beverly
Hill and installed Ocean Pride/Saxon controls. Every complete indexed support
report equals the previous checker, including face indices and all failures.
The exact 0.5m wall rule and strict source contacts are unchanged. No new install.

The conservative triangle index includes tolerance-expanded bounds, negative cell
boundaries, a bounded large-face fallback and original face ordering. It reduces
eligible wall triangle visits substantially, but local median totals across the
eleven checks were **398.5ms baseline / 402.6ms indexed**. This does not establish
an overall speedup; support sampling/index setup dominate many pairs. The next
optimisation target is repeated full-source incident-face scans, not looser gates.

Citywalk's 294 unresolved exact rim interfaces now have original source-face
indices: **200** intersect the same original vertical wall at bottom and deck but
remain outside the current contract; **94** have a source face but no same-wall
contact. These are script diagnostics, not evidence permitting a larger allowance
or resolving the assembly. Preserve the passing terrain from 4 October.

Twenty-five focused tests pass (19 Node geometry/index checks and six Python
dependency checks). The frozen previous checker comes from `4bf9293b`; relative
imports were adjusted only so the comparison is portable. `support-inputs.json`
pins exact source hashes, catalogue metadata and current source forms. Ignored
acquisition assets remain local-only; no R2 backup or viewer performance claim.

`neon-sync.json` verifies the complete fenced Neon result exactly. The supervised
reservation wrapper released every source lease after success. Pilot: one Installed
/ nine Held technical, zero In process/Held-AI/Held-human; wider XL: 39 Installed
/ 313 Held. Historical outcomes and acceptance states remain unchanged.

Commands from checkout root:

```sh
# Read the completed result/receipt; do not rerun this frozen stage.
python source-scripts/city/government-import/dependency_preflight.py \
  --catalogue path/to/new-stage/catalogue.json --out path/to/new-stage/dependencies.json
node --test source-scripts/city/government-import/triangle-point-index.test.mjs \
  source-scripts/city/government-import/support-interface.test.mjs \
  source-scripts/city/government-import/support-contact.test.mjs
python -m unittest discover -s source-scripts/city/government-import \
  -p test_dependency_preflight.py -v
```
