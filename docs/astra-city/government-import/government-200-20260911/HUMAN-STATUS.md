# Government batch: 200 models

Human-facing mapping of the completed 11 September 2026 context pass. Internal
Neon states and all source/acceptance evidence remain unchanged.

| Status | Models |
| --- | ---: |
| Installed | **2** |
| To do | 0 |
| Held for human decision | **0** |
| Held for AI processing | **0** |
| Held for unknown state | 0 |
| In process | **198** |
| Total | **200** |

**What is needed next: compute and scripts.** The 198 are queued for further
source-backed terrain, coverage, support and identity investigation. No worker is
claimed to be running at this checkpoint; the completed diagnostic job released
its reservation. All 200 already started, so none belongs in To do.

No requirement for your decision or per-model AI work has been established.
This does not guarantee that existing scripts can resolve every case: further
investigation may identify a specific AI/human requirement or unknown blocker,
which will be reported explicitly before any AI modelling starts.

Installed means verified on the Astra feature branch/preview, not a new production
release. The two installed source forms are landsd/81808:0 and landsd/204515:0.
The 198 retain their existing fallback until the original import checks pass.

The internal `retained-pending` state still blocks installation. In process is a
human workflow label for started work with a known next scripted step; it does
not override that guard or grant completion credit.

[Detailed diagnostic routes and evidence](pending-context/README.md) ·
[Installed verification](acceptance/README.md).

Source checkpoint: `government-pending-context-v1`, Neon job
`037fef779d7f6c875e84a1129feef4bda641a141bac072bf2c224d3fc902d532`.
Status mapping: repository model-improvement skill v1.8.0.
