# Complete current original terrain diagnostics

Codex, 7 October 2026. XL352 remains 89 installed / 263 not installed, with 45 new installations from the 44/308 baseline. Alto Tower 6 is installed and pushed in `055fe8e0`; its unchanged original terrain integration is documented in `439c3f61`. This diagnostic checkpoint adds zero installation credit.

Verified Neon job: `33f76cfb8029828904c7cdff14a7cf96dff3818afceaaf150fb317740ee67939`. `result.json` and `phases.json` bind Alto's completed installation and physical receipts, 21 unchanged-loader historical meshes, and 90 meshes refreshed through the current production loader. Source bytes and exact tile records are verified. Original payloads and full world geometry are local caches identified by exact receipts and hashes.

Nine models have a positive highest-original-TIN sample diagnostic: West Kowloon Station Bus Terminus (255415), The Orchards Tower 1 (254621), Leung Chi House (132324), WEST9ZONE (227099), Tower 3 (227380), 265848, 228219, Silvercord (233997), and Hong Kong Science Museum (80343). These diagnostics check all vertices, face centers and low edges at intervals of at most 1 m. They do not establish complete coherent terrain, foundations, native/basic neighbor compatibility, source identity or runtime acceptance. Missing current terrain sheets remain explicit. Mixed TIN/DTM/root pointwise feasibility is reported separately.

The 90-mesh refresh avoids reuse of an older loader or terrain-query implementation. The 21 historical meshes retain their changed manifest as historical context only. Four point-height tests cover original slope interpolation, triangle boundaries, duplicate planes, highest-facet selection and vertical faces; 31 existing terrain/source/sampler tests also pass.

Continue the fresh common-original-terrain attempts and complete physical/browser/installed acceptance for each passing subset. Preserve all existing source, contact, foundation and neighbor limits. Use zero per-model architectural AI calls or geometry edits. Commits and reports are checkpoints within the continuing 100-new-XL goal.
