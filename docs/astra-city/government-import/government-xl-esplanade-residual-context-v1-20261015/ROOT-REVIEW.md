# Esplanade residual source review — 15 October 2026

Neon job 3236d682cc114eec15728e2982e1a49c440ed10870e32363421d13a47ba83ccf completed/read back. Existing exact support checker reports 233 samples: 207 strict contacts, five same-triangle wall intersections, 21 unresolved (14 no vertical support, seven rim above support). No tolerance changes, automatic cantilever credit or geometry edits.

All 1,476 podium faces were tested against drawn candidate terrain with the existing continuous-minimum algorithm. All covered; four fail the -0.5 m bound: 510, 516, 518, 1276. All near vertical; no upward-facing failure. Ten non-height-field terrain faces retained separately by index. Minimum -2.7622571663 m. This is floating-intersection continuous minimum evidence, not a complete maximum-envelope certificate.

Root inspected residuals.png: failing tower samples lie around original perimeter facade segments; podium crossings are local near-vertical source walls alongside steep terrain. Image alone grants no architectural role, identity, support or placement acceptance.

Point-only authentic-terrain samples understated three crossings. Full-face replay with face_ground_context over the unchanged original 5-SE-15B terrain confirms minima -2.7588945975, -2.6515964655, -2.5742240146, -2.5568845106 m. These reproduce the candidate failures. There is no established patch error to fix by lowering terrain. Both observations retained in context.json and four-face-original-terrain.json.

Next: source-specific grade-wall review at the four faces, and exact facade/source-body context for the 21 tower rim failures. Podium identifier-cell hold remains separate. No corrupt/uninstallable classification. No installation or AI geometry modelling. Fixed XL count remains 236 installed / 285 unfinished / 521.
