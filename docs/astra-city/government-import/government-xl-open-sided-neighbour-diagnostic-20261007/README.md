# Actual open-sided neighbour geometry diagnostic

Codex, 7 October 2026. HKS-199. No historical map imagery used.

Verified Neon job: `c85efc763cf360e06e060be0227fc6bd6c0a06819bc0af8390383181db7d7c78`.

The current remaining-261 backlog was compared with completed neighbour evidence.
Twelve candidate terrain variants across nine held XL sources contain flagged
open-sided neighbours. These render as roof slabs and sparse illustrative posts,
rather than filled extrusions of the entire footprint.

The diagnostic uses the current viewer's `describeBuilding` parts, recorded
elevations, float32 coordinates and before/after terrain samplers. It checks part
boundaries and interior samples at no more than 2 m spacing, with the existing
numeric regression limits. Ground-gap checks apply to posts, not elevated roofs.
Current source-form hashes and proposed terrain hashes are verified. An explicit
terrain replacement also must match the current manifest and exact current bytes.

Results: **18 neighbour/variant pairs checked; zero pass**. Ninety-two rendered
post/variant checks retain increased ground gaps. One historical Apex replacement
is no longer current and was skipped explicitly. Roof/post sampling is a bounded
diagnostic, not proof of complete solid clearance. It grants no acceptance,
installation or geometry-change authority. Separate source contact, foundation,
identity, native-neighbour and browser gates remain required.

XL352 remains **91 installed / 261 not installed**, with **47 new installations**
from the 44/308 baseline and **53 further installations** required. No source
geometry changes, review changes, external AI calls or architectural modelling.

Reuse `geometry-checks.json`, `result.json` and `neon-sync.json` for these exact
inputs. Do not repeat unchanged failed checks. The script permits retrying an
unfinished local diagnostic, but rejects a completed result.
