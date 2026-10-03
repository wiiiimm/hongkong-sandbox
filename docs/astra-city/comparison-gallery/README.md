# Independent location gallery — HKS-228

Gallery view has seven rows and three version cells per row. Each location is centred and framed independently; its Basic/Light/High variants share one camera. The seven location cameras have different orbital phases. Global Play/Pause,0.25–3×speed, Orbit/Fly around and compact/roomy row controls are available. Motion starts paused. Manual drag pauses all motion; paused rendering is event-driven.

One additional shared renderer uses viewport/scissor rectangles to draw only visible gallery cells. It does not allocate21contexts. The existing three tour canvases remain cached but hidden and their animation is suspended in gallery mode. Switching back retains the travelling tour. Gallery resources are created once and reused on re-entry. Each row uses equal scale across variants; scales differ between locations for legibility.

Compact desktop rows fit seven locations in a1000px-high window; smaller screens scroll readable rows. Roomy rows provide larger models for detailed viewing. Mobile cells allow vertical page panning. Physical touch devices/performance remain unverified.

`node source-scripts/city/comparison-gallery/verify.mjs` verifies desktop/mobile viewport layouts,21cells, one gallery canvas, animation, stable pause,2×speed, scroll redraw and repeated return to tour/gallery. Saved screenshots inspected. No model geometry, Neon review state or production deployment changed.

## Current behaviour after user review — 10 September 2026

The panorama/travelling-tour option has been removed. Gallery and single-location comparison are the two views. Gallery exit pauses motion, clears the shared framebuffer and detaches its canvas from the document; inactive resize events do not recreate or render the overlay. Re-entry reuses the same renderer.

View size is now a90–420px slider instead of compact/roomy presets. All three cells in each row have the same height. Cinematic fly-through is a32-second repeating sequence with approach, facade rise, rooftop pass, wide reveal and return. Camera elevation, distance and look target change; different row phases are retained. Close passes keep the camera outside the assembly bounds. Orbit remains available and all automatic motion requires Play.

The current verification command writes to `fixes/`. It tests three exit/re-entry cycles at desktop/mobile widths, absent overlay canvas after exit and resize, removed panorama controls, exact100/280px slider heights, five cinematic phases, varying camera/target elevations, stable pause and no camera inside the model bounds at sampled phases. Exit and cinematic PNGs were inspected. Earlier evidence and tour scripts are historical, superseded by this behaviour. No model geometry or Neon state changed.

## Portrait location views and fixed gallery cells — 10 September 2026

Single-location canvases now default to 640 px tall. The three-column grid is
capped at 1,600 px wide so those default cells stay portrait on wide displays;
mobile retains the stacked layout. Canvas height adjusts all three variants from
320 to 1,200 px in 20 px steps, with a pixel readout and keyboard range controls.
The chosen height survives location changes, video view and gallery exit/re-entry.
The location slider is hidden while the independent gallery-size slider is active.

Gallery hover enlargement is removed, including transforms, overlap drawing order
and transition-driven redraws. Cells remain fixed on mouse hover; drag, gallery
sizing, synchronised cameras and drone/orbit playback remain available. Comparison
HTML, CSS and module URLs use a new cache version together.

High detail is now the highlighted government-model reference. The explanation
clarifies that High reuses native government geometry and Light uses script-reduced
meshes or procedural façades; these are not AI reasoning-effort comparisons. The
model-improvement skill now prefers suitable original detailed government geometry,
with simplification justified by a measured runtime need and visual assessment.
No actual model assets or review records were changed by this UI work.

`verify.mjs` now uses the repository's portable browser resolver and writes fresh
evidence to `portrait/`. Real Chrome checks pass at 1440 px desktop and 390 px touch
emulation: portrait default, 320/900/1200/640 px changes, keyboard step to 660 px,
location/video persistence, identical variant cameras, fixed hover bounds, hidden
location slider in gallery, exact gallery sizing, playback/pause, sampled drone
paths, three gallery exit/re-entry cycles and no horizontal overflow or page errors.
Desktop/mobile portrait and gallery screenshots were inspected. Earlier `fixes/`
and root evidence remains historical. Physical-device performance was not measured.
