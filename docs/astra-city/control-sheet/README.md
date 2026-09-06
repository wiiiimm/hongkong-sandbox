# City controls · HKS-190

GPT-6 Astra, 6 September 2026. This adapts the existing City inspector to a mobile bottom sheet and a desktop floating panel. Every pre-existing HTML ID remains present exactly once (118 retained IDs); existing location, layer, sky, meteor, weather, tide and sound handlers remain attached to the same elements. There is no new UI library or second copy of the controls.

On phones up to 760 px wide, the sheet starts collapsed. Its handle, Places/Sky/Weather tabs and Explore/Walk/Fly/Stargaze dock remain visible. A tab or the handle expands the scrollable controls; the handle, a downward gesture or Escape collapses them. Visiting a search result and entering a game mode return to the visible city. The sheet reserves a footer for the dock and uses the original light/dark palette, typefaces and switches, with larger touch targets and 16 px native inputs to avoid mobile input zoom.

Desktop retains an initially open 318 px floating inspector. At widths 761–1160 px its height stops above the centred mode dock; the wider desktop layout keeps its full height. The header and top-bar button now close/reopen it; `/` opens Places and focuses search. Panel selection and scroll position survive collapsing. Arrow keys follow standard tab behaviour. Collapsed content is hidden and inert, while the mobile tabs remain available. Escape closes the controls before the game's Escape action; open dialogs keep their normal handling. Sheet keyboard events do not become movement keys, and the presentation does not trap focus or block the city.

The controller listens to `visualViewport` size/offset changes to lift the sheet and dock above an on-screen keyboard. Root mode integration clears held movement input when controls open. Reduced-motion preferences disable CSS transitions through the existing global rule. Disposal removes the controller's listeners and temporary viewport styles.

## Integration

```js
import {createControlSheet} from './control-sheet.js';
const controlSheet = createControlSheet({
  onExpand: () => nav.clearInput(),
  focusMap: () => renderer.domElement.focus({preventScroll:true})
});
controlSheet.open('places', {focusSearch:true});
controlSheet.selectPanel('sky', {expand:false});
controlSheet.close({restoreFocus:false});
controlSheet.toggle();
controlSheet.dispose();
```

`state` exposes `{expanded, panel, mobile, disposed}` and is included in `window.__city.state.controls`. The controller owns the original tab and panel-toggle listeners. The app retains gameplay, selection, streaming and environment responsibilities. The new timelapse speed markup below the clock is coordinated with HKS-189; its clock logic and tests are documented by that separate task.

## Browser evidence

Run from `3d-viewer/city` with the existing local server:

```sh
node tests/control-sheet-browser.mjs
node tests/control-sheet-browser.mjs --followup
```

Reserve the GPU before running. `CITY_URL` and `CHROME_PATH` are optional overrides. The main report is `browser/verification.json`, with direct screenshots at 390×844, 320×844, 390×480 and 1440×1000 (device scale 1, Chrome 152). It verifies the collapsed and expanded states; all three tabs; full clock and lower controls; search; Explore/Walk/Fly/Stargaze; layer-independent meteor and tide input; native keyboard operations; handle gestures; and listener disposal. No page exceptions or WebGL/shader errors occurred.

The separate `browser/followup-verification.json` also passes native Space activation on the external mode dock (Walk → Explore on desktop and phone), plus the 1024×768 layout. That screenshot was visually inspected: the inspector ends at y=650 and the dock starts at y=669, leaving 19 px. The confirmed pre-fix overlap is retained in `desktop1024-before-fix.json`; the 1160 px breakpoint covers the computed intersection threshold at 1138 px with margin. A test helper was also corrected to reopen the desktop inspector after resizing a collapsed phone sheet.

The full passing run measures a 175 px collapsed phone sheet. Expanded phone content ends at y=756 and the dock begins at y=765, leaving a 9 px separation. There is no horizontal overflow. The Walk keyboard check waits for the existing chase-camera easing to settle, then records unchanged actor position and less than 1 mm residual camera drift while pressing tab arrows and a native Space button.

Exported phone, desktop, clock, lower-weather and short-viewport screenshots were inspected visually: typography and control labels remain legible, the full dial fits at the top of the Sky tab, and scrolled controls stop above the persistent dock. The first failed CSS-cascade check is preserved as `browser/first-pass.json` and `first-pass-overlap.png`; its cause was the old mobile `.explorer.open {display:block}` rule overriding flex layout, and the final rule corrects it.

The keyboard-inset assertion uses a synthetic `visualViewport` resize, plus a real short browser viewport. It verifies layout response to the browser's reported dimensions; it is not a claim of physical iOS/Android keyboard testing. No geography, source imagery, performance benchmark or astronomical accuracy claim is introduced by this presentation change.

The subsequent HKS-189 visibility correction groups the dial, toggle and speed slider at the top of Sky, ahead of the calendar controls. [Current first-open screenshots and multiplier checks](../time-cycle/README.md) supersede the earlier scroll-to-reach speed-control screenshots.
