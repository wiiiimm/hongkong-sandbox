# Standard browser validation render scheduling — 7 October 2026

The scripted browser now suspends the actual renderer immediately after the app module starts, before asynchronous initialization resumes. It saves that renderer’s original draw function and invokes it for each inspection capture. Model loading, mobile budgets, camera controls, picking, collision, terrain sampling, and the injected download failure and user retry remain exercised through production code. This follows the assembly fixture’s existing approach and avoids rendering the entire city continuously while headless validation loads models.

Hampton Loft (landsd/284938:0) passed a fresh staged diagnostic: desktop and mobile day/night captures, original neighbours retained, picking and collision, and the mobile 503 fallback and retry. The actual mobile daytime PNG was inspected. The JSON report is retained here; images remain local, with exact hashes recorded. No models were installed by this diagnostic, no architectural geometry was edited, and no external model AI was called. Hampton still needs fresh physical and staged/live installation acceptance.

Validation: `node --check source-scripts/city/government-import/resolution-browser.mjs`; staged browser diagnostic config `source-scripts/city/government-import/local/hampton-early-render-config-20261007.json`.
