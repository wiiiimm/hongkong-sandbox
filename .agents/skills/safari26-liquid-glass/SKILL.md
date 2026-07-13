---
name: safari26-liquid-glass
description: How iOS 26 / iPadOS 26 Safari's "Liquid Glass" translucent status & address bars interact with web content, the viewport/keyboard facts behind them, and what to watch for when a design gets creative (immersive/edge-to-edge layouts, custom drawers/modals, gesture panning, themeable backgrounds, canvas). Use when an iPhone/iPad web page shows black/grey bars, content "cut off" at the bar edge, cropped shadows, the top status bar turning opaque/tinted under a sticky or fixed header, a drawer/modal that breaks the layout, an inner scroll that won't scroll, the page jumping after the soft keyboard closes, or a canvas blur that won't render on iOS — or before building any full-screen/immersive iOS web UI.
metadata:
  author: stealth-engine
  co-author: wiiiimm
  version: "2.3.0"
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

### The bar *tint* — Safari derives it from your CSS (`theme-color` is dead)

Beyond the live bleed, Safari 26 tints the glass with a **solid colour derived from
your CSS**. `theme-color` is **ignored** (it still parses; the value does nothing).
The derivation, in order:

1. the `background-color` of a **`fixed`/`sticky` element at that edge** — it borders
   the "obscured content inset" (where the bar overlaps content), so Safari extends its
   colour into the bar for continuity;
2. else the **`body`** `background-color` — `html`'s is **ignored**, and this same
   `body` colour is what the overscroll "rubber-band" shows, so **match `body` to your
   design** or you get flashes (a white `body` on a dark site flashes white on overscroll);
3. else the system default.

- **Derived from the CSS, not live from JS** — mutating a background via JS after paint
  does **not** re-tint the bar (Safari re-derives on scroll/layout, not on a bare style
  change).
- **Solid vs translucent flips control:** a solid colour tints the bar to exactly that
  colour (yours); an **`rgba()`/semi-transparent** background makes Safari sample the
  *computed* colour showing through → unpredictable. Use opaque for control.
- **Users can disable tinting** (iOS: Settings ▸ Apps ▸ Safari ▸ Tabs ▸ "Allow Website
  Tinting") → the bar reverts to system default, so your design must still read then.
- **The blur is softer on iPhone than macOS** — more of the page shows through the bar,
  so a colour mismatch between your sampled edge element and the content behind it is
  more visible/jarring here. Getting the sampled colour right matters most on iPhone.

**The tint is a feature — decide your intent:**

- **Want the bar tinted to match a header/brand (i.e. you do NOT want a transparent
  status bar):** give a top element a solid `background-color` and let Safari sample it.
  **`sticky` is the reliable trigger** — a bare `fixed` header's colour is sampled
  inconsistently (see §2 and WebKit #301756); setting `body`'s background also works.

  ```css
  header { position: sticky; top: 0; background: #1a1a1a; } /* → status bar #1a1a1a */
  ```

- **Want an immersive / transparent bar:** control this on the **edge (fixed/sticky)
  element**, not by stripping `body`. Keep an opaque `background` *off the edge element*
  and use §2's field-note knobs (a `fixed; top:0` header keeps the top bar glassy).
  **Leave `body` painted** — §5/§2 need it for the overscroll rubber-band and the
  load-flash guard, so don't remove it here; a painted `body` is only the *fallback*
  tint, and the finicky edge-element behaviour (§2, WebKit #301756) is what actually
  decides whether the bar goes transparent.

Same-mechanism gotchas: a **fixed full-screen modal backdrop** (`inset: 0; background:
rgba(0,0,0,.5)`) *can* get sampled and darken the whole bar — but fixed-element sampling
is **unreliable** (see the §2 "fixed backdrop is a trap" note for the flip side, where
the fixed layer is ignored instead); **two fixed elements** (header + footer) → Safari
picks one, not reliably; and there is **no `theme-color` override — the CSS *is* the
API** (WebKit #301756 tracks fixed-element tinting issues).

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
(A "fixed full-screen backdrop" is an **unreliable** tint source: in our build the
in-flow background *behind* it did the tinting and the fixed layer added nothing — the
flip side of the same finicky fixed-element sampling that *elsewhere* lets a fixed
`rgba` backdrop darken the bar (§1). Either way it crops its children, so **don't use a
fixed layer to control the bar tint** — use a `sticky` element or `body`.)

**Field note — a top-pinned header and the *top-bar tint* is a separate axis.**
The bleed/shadow rule above is about content clipping; whether the **top status bar
stays transparent** under a header pinned to the very top behaves differently — and
here `fixed` is actually the *safe* choice:

Offsets below are written as Tailwind classes (what was tested): `top-0` = `top: 0`,
`top-1` = `top: 0.25rem`, `top-2` = `top: 0.5rem`. (Nonzero CSS lengths need a unit —
`top: 1`/`top: 2` are invalid; use `0.25rem`/`0.5rem`.)

- `position: fixed` at `top-0` — top status bar **stays transparent**. `fixed` does
  **not** kill it here.
- `position: sticky` at `top-0` — **kills** it (bar goes opaque). `top-1` still kills
  it; **`top-2` restores** the transparent bar — a sticky top header needs a small
  offset off the bar edge to keep it.

So "never `position:fixed`" is a *bleed/shadow* rule, not a top-tint one: for a
top header specifically, `position: fixed` at the top — or a `sticky` header with a
≥ `top-2` (`0.5rem`) offset — keeps the bar transparent. Single-setup observation on
iOS 26.x; re-verify on your build.

*Why (ties to §1's tint derivation):* a `sticky` header with a **solid
`background-color`** sitting at the very edge is exactly what Safari **samples** into
the bar — so it *tints*, it doesn't "break"; the `top-2` offset stops it bordering the
bar edge, so it isn't sampled. In this test a `fixed; top:0` header left the bar
transparent even so — **fixed-element sampling is less reliable** (WebKit #301756).
Practical rule: for a **deliberate tint**, `sticky` + a solid bg is the reliable
trigger; for **transparent**, `fixed; top:0` or `sticky` with a ≥ `top-2` offset.

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
then fall back to `body`" behavior match independent Safari 26 reporting (Apple
published no official web-dev docs for it; the specific derivation order below is the
one write-up cited in References). §1's **bar-tint derivation order**
(fixed/sticky edge → `body` → default; `html` ignored; sampled at render; overscroll
rubber-band = `body`) follows Ben Nasedkin's write-up; the less-reliable fixed-element
case is WebKit #301756. The **`innerWidth <= 760`**
gate is a **rule of thumb, not an Apple constant** — the split is by window width,
but the exact breakpoint isn't documented; **measure/treat it as approximate** and
tune per layout rather than copying 760 verbatim.

The §2 top-bar-tint thresholds (`fixed; top:0` keeps the top bar transparent; a
`sticky` top header needs a ≥ `top-2` offset) are a **single-setup on-device
observation** — confirmed once, not yet corroborated by outside write-ups. Treat the
exact `top` threshold as approximate and re-verify.

Everything here is as-of **iOS/iPadOS 26.x**; behavior is evolving across point
releases (see the keyboard-bug status note in §2). **Re-verify on your target OS
build** before relying on any specific fact.

References: WebKit #297779 (keyboard/visualViewport offset; acknowledged, partly
improved in 26.1), WebKit #198416 (canvas `ctx.filter`; RESOLVED FIXED but
disabled by default in shipping Safari 18–26.x), WebKit #301756 (fixed-element
toolbar tinting), and Ben Nasedkin, "Why iOS 26 Safari Toolbar Colors Work
Differently" (nasedk.in) — the source for §1's tint-derivation order.
