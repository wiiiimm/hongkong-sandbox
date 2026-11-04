# Panoramic comparison tour — HKS-228 follow-up

All-locations mode stacks three full-width horizontal views. Each uses the same camera position and look target. Single-location mode keeps its previous comparison layout. Video view reduces titles and chrome so the three lanes fit a desktop recording frame; mobile retains readable lane heights and may scroll.

Start fly-through enables overview and visits all seven study locations. Each stop has an eight-second partial orbit followed by four seconds of eased travel to the next stop; the cycle repeats. Pause/resume retains elapsed tour time. Manual dragging pauses automatic movement. Reset returns to the overview; standalone spin and the tour are mutually exclusive. Starting motion always requires a click, including for reduced-motion users.

These are relocated study models, not a geographic flight route. All variants retain identical placement and scale within the study. No model geometry, acceptance state or database record changed.

`node source-scripts/city/comparison-flight/verify.mjs` checks1440/390 widths, stacked full-width lanes, all seven stops, identical cameras, stable pause, resume, reset and return to individual views. Saved PNGs were visually inspected, including a close HSBC stop and the panoramic layout. Browser emulation is not physical-phone testing.
