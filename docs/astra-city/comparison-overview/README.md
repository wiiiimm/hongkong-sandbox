# HKS-228 — comparison overview and spin

The existing three renderers now support a complete seven-location study grid as well as the original single-location view. Locations come from the generated manifest; adding a group does not require editing the selector. Numbered markers and a location key avoid overlapping long labels.

All three variants use the same physical scale, camera and grid positions. This is a comparison layout, not geographic placement. Small buildings remain small beside IFC; use the per-location view or zoom for detail. Existing source geometry is not newly approved by this UI feature.

Start spin / Pause spin controls a synchronised horizontal orbit. Rotation defaults off, including with reduced-motion preferences. Manual orbit pauses automatic rotation. Video view removes editorial content and payload statistics while retaining comparison headings, controls and the location key. It does not record or post a video.

Verification: `node source-scripts/city/comparison-overview/verify.mjs` against the local viewer on port 4176. Chrome passed at 1440 and 390 pixels with seven locations, three canvases, 21 markers, no horizontal page overflow or page errors. Camera movement was asserted during spin and exact camera stability after pausing. Every per-location variant remained non-empty after returning from overview. Screenshots for both modes and viewport sizes are adjacent. These are functional browser checks, not a mobile GPU performance certification.
