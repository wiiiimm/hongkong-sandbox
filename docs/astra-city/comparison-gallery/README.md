# Independent location gallery — HKS-228

Gallery view has seven rows and three version cells per row. Each location is centred and framed independently; its Basic/Light/High variants share one camera. The seven location cameras have different orbital phases. Global Play/Pause,0.25–3×speed, Orbit/Fly around and compact/roomy row controls are available. Motion starts paused. Manual drag pauses all motion; paused rendering is event-driven.

One additional shared renderer uses viewport/scissor rectangles to draw only visible gallery cells. It does not allocate21contexts. The existing three tour canvases remain cached but hidden and their animation is suspended in gallery mode. Switching back retains the travelling tour. Gallery resources are created once and reused on re-entry. Each row uses equal scale across variants; scales differ between locations for legibility.

Compact desktop rows fit seven locations in a1000px-high window; smaller screens scroll readable rows. Roomy rows provide larger models for detailed viewing. Mobile cells allow vertical page panning. Physical touch devices/performance remain unverified.

`node source-scripts/city/comparison-gallery/verify.mjs` verifies desktop/mobile viewport layouts,21cells, one gallery canvas, animation, stable pause,2×speed, scroll redraw and repeated return to tour/gallery. Saved screenshots inspected. No model geometry, Neon review state or production deployment changed.
