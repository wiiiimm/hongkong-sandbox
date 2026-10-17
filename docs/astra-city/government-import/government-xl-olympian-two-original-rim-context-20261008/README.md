# Olympian City Two — exact original rim and basic-support diagnostics

Codex, 8 October 2026, HKS-203. This complete read-only diagnostic binds the existing source-local physical result,107 unchanged low-rim samples, original government terrain files and four unchanged basic tower forms. It does not approve a candidate or change the live map.

The19 samples exceeding the unchanged1m gap limit lie within x267.96875–271.34375 / z−3088.6875–−3078.375 in native viewer metres. The nearest affected neighbour is152.492647m away. Current root ground at those failing samples would bury the source by3.583504–4.066346m. The gap and the four neighbour problems are therefore spatially separate.

Direct interpolation against232,661 original terrain triangles reproduces the candidate ground at all107 rim samples within2.505793e−8m. The original source itself retains a maximum1.130128m gap and19 samples over1m. This rules out candidate clipping/interpolation error at those sampled positions; it is not a whole-terrain correctness claim, architectural judgement or permission to alter tolerances.

The original podium does not pass the conservative sampled support probe for any affected basic tower:

| Basic tower | Samples | Contacts | Missing support |
| --- | ---: | ---: | ---: |
|269837|868|99|192|
|269839|869|138|145|
|269908|1245|150|526|
|270317|1969|715|550|

Remaining samples also have out-of-range clearances. These probes grant no component identity, full floor coverage or acceptance. Retaining old ground instead was separately checked in `government-xl-olympian-two-basic-ground-retention-20261008`: it clears neighbour warnings but buries the new original mesh and fails its complete foundation.

Verified Neon job `94bc8d3f2ad7fd10d5a89a910ca7d3fe52a577fce6965e16149c34631390499a` binds the diagnostic results, exact helper/input hashes, original source files and preceding complete physical job. Supervisor completed and released its reservation. Reuse these failures; a further continuation needs changed authoritative source/terrain/component evidence or a demonstrated code correction. This does not establish permanent corruption, impossibility or a need for AI modelling.

Reproduce with `xl-original-rim-context-diagnostic.py --previous docs/astra-city/government-import/government-xl-olympian-two-source-local-terrain-20261008 --batch FRESH-government-xl-BATCH`, plus repeated `--protect` arguments for the four exact tower UIDs. It runs the bound low-rim, neighbour-location and basic-support helpers, checks original terrain receipts, then writes a fenced, read-back-verified Neon result. Use a fresh batch; completed reports and bound scripts are immutable.

No new installation. Full XL remains521=197 installed-verified+324 remaining. No model/architectural AI calls; AI was used for code development. No historical map imagery used. Linear synchronisation remains pending; no rejected disclosure is retried.
