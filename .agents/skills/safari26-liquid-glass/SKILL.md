---
name: safari26-liquid-glass
description: How iOS 26 / iPadOS 26 Safari's "Liquid Glass" translucent status & address bars interact with web content, the viewport/keyboard facts behind them, and what to watch for when a design gets creative (immersive/edge-to-edge layouts, custom drawers/modals, gesture panning, themeable backgrounds, canvas). Use when an iPhone/iPad web page shows black/grey bars, content "cut off" at the bar edge, cropped shadows, a drawer/modal that breaks the layout, an inner scroll that won't scroll, the page jumping after the soft keyboard closes, or a canvas blur that won't render on iOS — or before building any full-screen/immersive iOS web UI.
metadata:
  author: stealth-engine
  co-author: wiiiimm
  version: "2.1.0"
---

# Safari 26 "Liquid Glass" — facts, gotchas, and what to do

## 1. The model

iOS 26 and iPadOS 26 gave Safari a "Liquid Glass" chrome: the **status bar**
(top) and the **address/tab bar** (bottom) are **translucent overlays** that
show whatever the page paints **behind them**, live, as you scroll. Apple
**dropped `theme-color`** as the bar tint — the bars just reflect the page now.

This is the **iPhone Safari layout model**. It also applies on **iPadOS** — and
there it's gated by the **browser window width**, not the device: a narrow Safari
window (Split View, Slide Over, a portrait small iPad, or just a narrow window)
gets the iPhone model with the glass bars; a wide one gets the desktop-ish model.
**So decide "is this the glass model?" by width, not by user-agent** (e.g.
`innerWidth <= 760`), because the same iPad flips between the two.

Think of the screen as **two viewports**:

- **Layout / large viewport** — the full physical screen, *including* behind both
  bars. `100vh`, `100lvh`, and `window.innerHeight` all measure **this large
  viewport**. **`innerHeight` is constant** — it does NOT change when the bars
  show/hide or the keyboard opens.
- **Visual / small viewport** — only the area *between* the bars.
  `window.visualViewport.height` and `100svh` measure this; **`100dvh`** tracks
  it dynamically (it shrinks when the keyboard opens).

So on this model **`innerHeight` = the large viewport** (constant), while
`visualViewport.height` = the small viewport (changes). Any "fill the visible
area" math must be driven off `visualViewport`, never off `innerHeight`/`vh`.

The bars sit over the **edges of the layout viewport** and composite whatever DOM
pixels are painted there.

## 2. Facts we established (iOS/iPadOS 26, verified on-device)

- **A black/grey bar is just your page background showing through.** If `html`/
  `body` background is dark, the bars are dark. Paint it your page colour and the
  bars take that colour. This is also the flash you see on first load.
- **Only *scrolled document content* bleeds under the bars.** A genuinely tall,
  scrollable document paints behind the bars. A page sized to exactly the
  viewport does **not** bleed — it stops at the bar edge; the background shows
  behind the bars.
- **`innerHeight` is constant; `visualViewport.height` is what changes** (bars,
  keyboard). Measure layout with `innerHeight`; detect keyboard/bar state with
  `visualViewport`.
- **A `flex:1` / `overflow:auto` child inside a `dvh`/`vh`-sized box often won't
  scroll** (it grows to its content and the gesture falls through to the page).
  **Try the standard fix first:** the usual culprit is `min-height:auto` on a flex
  item — set **`min-height:0`** (or `min-height:0` on the flex child + the scroll
  area) and it typically scrolls. Where that isn't enough, we've observed iOS 26
  behaving as if `dvh`/`vh` heights resolve as *indefinite* for the child (so it
  never gets a scrollable box); the reliable escape is a **definite px** height
  (derived from `innerHeight`) on the scroll container. Verify per case.
- **The glass bars cache their backdrop.** They only re-sample on a **scroll or
  layout change** — changing a background colour or repainting a canvas alone
  leaves the bar **stale**. A 1px scroll nudge forces a re-composite.
- **Centre-scroll math must be measured, not `vh`-based** — `vh`/`innerHeight`
  (large) ≠ `visualViewport` (small), so a `vh` calculation leaves a strip.
  Measure the visible band with `visualViewport.height`.

### `position:fixed` is the big one

A `position:fixed` element is clipped to the **visual** viewport, so:

- **The element never paints behind a bar, and its shadow is cropped** at the bar
  edge. (A fixed button anchored with `env(safe-area-inset-bottom)` still has its
  drop-shadow chopped where the bar starts.)
- **Worse: a full-screen / overlay fixed element can collapse the *whole page's*
  bleed** — once it's on screen, the rest of the page starts clipping at the bar
  edge too, and the clip can **persist after the fixed element is gone** (until a
  scroll/layout change). We reproduced this just by opening & closing a
  `position:fixed` bottom-sheet + backdrop.

So the damage is **sometimes just the element (cropped shadow), sometimes the
entire page (collapsed bleed) — depending on the element and where it sits.**
Treat **any** `position:fixed` as a bleed-breaker on this model and verify.
(A "fixed full-screen backdrop" that *appears* to tint the bars is a trap — an
in-flow background behind it is doing the tinting; the fixed layer adds nothing
and crops its children.)

### The keyboard bug (WebKit #297779)

- Focusing an input opens the soft keyboard; iOS **scrolls the window** to keep
  the input visible.
- `innerHeight` stays constant; `visualViewport.height` shrinks. iOS fires **one
  `visualViewport` resize per transition** (one on open, one on close — *not* one
  per animation frame).
- **After dismissal the viewport can stay shifted** — `visualViewport.offsetTop`
  doesn't reset to 0 and the height can stay ~24px short — so content looks
  "slid up by the keyboard height." Affects fixed/sticky elements and any
  scroll-positioned layout. (Even apple.com is affected.)
- **Status (as of iOS 26.x):** WebKit #297779 is acknowledged by Apple; iOS 26.1
  reduced the residual offset but reports of the stuck ~24px `offsetTop` persisted
  into later 26.x releases. Treat the workaround below as still needed and
  **re-verify on your current OS build** before assuming it's fixed.
- Because **`innerHeight` is constant**, your intended scroll position is the
  **same whether the keyboard is open or closed** — so you can restore it the
  moment the field blurs, without waiting for the (late) close event.

## 3. For a normal website, all of this Just Works

A plain, tall, scrolling page — normal background, content in flow, ordinary
fixed header/footer, native inputs — bleeds correctly, tints the bars, and
recovers from the keyboard on its own. **You usually need to do nothing.** A
1990s long-article page renders perfectly. If you see black bars or clipping on a
simple page, you've *added* something from §4.

## 4. But if you get creative, BEWARE

Immersive/edge-to-edge layouts, fixed full-screen canvases, custom drawers/
modals/sheets, gesture-driven panning, themeable/live backgrounds, canvas
effects — these break the "just works" assumptions. Problems we hit:

- **Black bars** — from a dark app-shell/`body` background.
- **Content clipped at the bar edge** — from a viewport-height, non-scrolling
  shell (`height:100vh` + `overflow:hidden`, a `100dvh` flex app, or
  `position:fixed; inset:0`). It can't bleed.
- **Cropped shadows / collapsed bleed** — from `position:fixed` chrome, drawers,
  or backdrops (see §2).
- **An inner scroll area that won't scroll** — because its container is sized in
  `dvh`/`vh` (indefinite); the gesture scrolls the page instead.
- **The page scrolling away** — a drawer's inner scroll **chains** to the document
  and drifts an immersive/centred layout.
- **The bars lagging a live colour/content change** — the cached backdrop.
- **The layout shifting and not recovering after the keyboard** — §2 keyboard bug.
- **A canvas blur not rendering** — see §6.

## 5. Suggestions (case-dependent — pick what the situation needs)

**First, always:** paint `html`/`body` your page colour **in CSS** (not JS — JS is
too late and you get a first-paint flash). If the colour is dynamic, bake a sane
default into CSS and update it live afterwards.

**If you only need the bars to match a colour** (content needn't go under them):
the CSS background above is often enough. Make sure no opaque dark element covers
the bar region.

**If you need content to bleed under the bars (immersive/edge-to-edge):**

- Build a scroll **band taller than the screen** (e.g. `innerHeight + 2·PAD` px,
  `PAD≈200`) painted the page colour, and **centre it by measurement** (not `vh`)
  on mount + `resize` + `orientationchange`. It then overflows ≈`PAD` under each
  bar and fills both at once (a screen-height band can't — pushing it up to cover
  the top uncovers the bottom).
- Size the band in **definite px** (from `innerHeight`), **not `dvh`** — `dvh`
  shrinks with the keyboard and would resize the whole thing.
- Put **all chrome inside the band**, in a frame **inset by `PAD`** (= the visible
  region), with normal insets + `env(safe-area-inset-*)`.
  **Never `position: fixed`** — that re-breaks the bleed and re-crops shadows.
- Stop gestures from scrolling the band: `touch-action:none` on the interactive
  surface (canvas does its own pan/zoom) + `overscroll-behavior:none`.

**Drawers / bottom-sheets / modals (the part people get wrong):**

- Make the sheet and its backdrop **`position:absolute` inside the band, NOT
  `fixed`** (fixed collapses the bleed). Anchor the sheet under the bottom glass
  and add equal bottom **padding** inside its scroll area so content clears the bar.
- Give the sheet a **definite px height** so its inner body actually scrolls;
  pin the header with `position:absolute` (outside the scroll body) so only the
  body rubber-bands.
- **Lock the page while the sheet is open** with `overscroll-behavior:contain` on
  the sheet's scroll body + `touch-action:none` on the backdrop — **not**
  `position:fixed`/`overflow:hidden` on `body` (both break the bleed or jump the
  scroll).

**Live/themeable background colour:** update the document background live, then do
a **1px scroll nudge** (debounced) to force the bars to re-composite — otherwise
they lag until the next scroll/layout.

**Soft keyboard:** capture the scroll position on `focusin` (page is settled
then); on `focusout` **restore it** — you can do this immediately because
`innerHeight` is constant, so the target is already correct. Back it up by also
restoring when the `visualViewport` resize reports the height back near full, and
finish with a **1px scroll jiggle** to reset the stuck `offsetTop`. Don't pin the
scroll *while* the keyboard animates (iOS re-scrolls and undoes it).

## 6. Related WebKit canvas gotcha (not glass, but found here)

`CanvasRenderingContext2D.filter` (e.g. `ctx.filter='blur(4px)'`) **silently
doesn't render by default on iOS/iPadOS Safari** — the effect is a no-op even
though it works in Chrome. WebKit #198416 is **RESOLVED FIXED** (implemented in
2024), but as of Safari/iOS 18–26.x the feature ships **disabled by default,
behind a flag** — so in practice you can't rely on it. Use **`shadowBlur`**
instead (draw the shape far off-canvas and keep only its blurred shadow, tinted
as needed). SVG `feGaussianBlur` is fine; it's only the canvas 2D `filter`
property that's off by default.

## Provenance

Established iteratively, on-device, building the Made in Lantau "Lantau Type Map"
(a full-screen canvas studio) for iOS Safari 26. Every fact in §2 and every
problem in §4 was reproduced and fixed on a real iPhone/iPad.

§1's model claims are corroborated beyond that build: the `theme-color` drop and
"bars reflect the page / sample a fixed-or-sticky edge element's `background-color`
then fall back to `body`" behavior match multiple independent Safari 26 write-ups
(Apple published no official web-dev docs for it). The **`innerWidth <= 760`**
gate is a **rule of thumb, not an Apple constant** — the split is by window width,
but the exact breakpoint isn't documented; **measure/treat it as approximate** and
tune per layout rather than copying 760 verbatim.

Everything here is as-of **iOS/iPadOS 26.x**; behavior is evolving across point
releases (see the keyboard-bug status note in §2). **Re-verify on your target OS
build** before relying on any specific fact.

References: WebKit #297779 (keyboard/visualViewport offset; acknowledged, partly
improved in 26.1), WebKit #198416 (canvas `ctx.filter`; RESOLVED FIXED but
disabled by default in shipping Safari 18–26.x).
