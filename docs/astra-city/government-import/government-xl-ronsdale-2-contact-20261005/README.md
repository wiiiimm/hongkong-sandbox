# Ronsdale Garden Block 2 — completed terrain investigation, held

Codex root, 5 October 2026; HKS-203 / HKS-215 / HKS-199. Unchanged original
`landsd/256702:0` and original 11-SE-11A terrain were processed locally.
Source/archive/model hashes, full metrics and neighbour evidence are saved here;
original acquisition files remain local-only. No AI architectural judgement,
geometry edits, elevation shifts or acceptance tolerance changes.

Whole-source foundation checks complete with zero buried area, but ground contact
fails: minimum clearance 4.005207m and maximum low-rim gap 13.786076m. Loader
diagnostics flag the same terrain gap. Two basic forms, `landsd/256898:0` and
`landsd/307560:0`, regress under the proposed terrain. No terrain is published.
An exact original supporting assembly/contact investigation is the next step;
these failures alone do not establish that AI or human decisions are required.

Neon job `d58fee7f0a2f041472c758162978c11f854de855371bb1295e173a1b5f2403b7`
is complete with exact readback; source leases released, zero active/queued workers
and zero installations. Current status: Held technical/unknown. Reuse `result.json`
and its evidence hashes instead of rerunning the completed terrain work.

Historical command: `python source-scripts/city/government-import/xl-terrain-source-case-20261005.py ronsdale-2`.
