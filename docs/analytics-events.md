# Viewer analytics — provider-agnostic event library (HKS-102)

The 3D viewer fires **custom analytics events** through a small provider-agnostic
library, so we can understand what people actually do inside the map — broken down
by **locale** (en / zh-HK), **mode**, **theme** and **device** — and swap or add
analytics providers (Vercel now, GA4 next) without touching a single call site.

## Files

- **`3d-viewer/analytics.js`** — the library. Build-free, no npm; a single vanilla
  ES module. Owns the canonical event shape, the base props, the gating, the
  debounce and the per-provider sinks.
- **`3d-viewer/main.js`** — imports `initAnalytics`, `track`, `armAnalytics`,
  `VercelSink`, `GA4Sink`; wires exactly one `track()` call at each control's
  existing handler.

## How it works

```
control handler ── track(name, props) ──▶ [gate] ──▶ baseProps() merged in ──▶ fan out to every sink
                                            │
                    embed / not-armed / URL-state restore → dropped
```

- **`track(name, props)` is the only analytics entry point in the app.** Call sites
  never touch `window.va` or `gtag` directly.
- **Base props** (`locale`, `mode`, `theme`, `device`) are attached **once**,
  centrally, in `initAnalytics({ baseProps })` — so every event segments by language
  and context without per-call-site boilerplate.
- **Gating** is centralised: events are dropped in **embed** mode (`?embed=1`),
  before the app is **armed** (the initial load + `applyState()` URL-state restore),
  and while `restoring` is true. Programmatic/synthetic control changes are also
  ignored because each DOM handler additionally checks `event.isTrusted`.
- **Slider commits** (`sky_time_scrub`, `wind`) are logged on the range input's
  `change` event (fired on release), not per `input` tick — one event per scrub.
- **Privacy**: no PII. GPS is tracked as **state only** (`follow | compass | off`),
  never coordinates. `clean()` structurally drops anything that isn't a plain scalar.

## Sinks (providers)

Each provider is a small adapter `{ id, init(), send(evt) }`, registered
independently. The library owns the canonical event; each sink maps it to that
provider's API.

- **VercelSink** (now) — `window.va('event', { name, ...props })`. No-ops if
  `window.va` is absent (forks / localhost / other hosts).
- **GA4Sink** (next) — loads `gtag.js` lazily and maps to
  `gtag('event', snake_case_name, params)`. Respects GA4 constraints: snake_case
  names, ≤ 25 params, string/number values only, `locale` sent as an event param
  **and** a `user_property`. It **opts itself out until a measurement ID exists**.

### Adding GA4 later = one line, zero call-site edits

GA4Sink is already registered in `main.js`; it simply skips itself until it has an
ID. To enable it once the GA4 property exists, either set `window.__GA4_ID` before
`main.js` loads, or pass the ID directly:

```js
sinks: [VercelSink(), GA4Sink({ measurementId: 'G-XXXXXXXXXX' })],
```

Adding a further provider (Plausible / PostHog / …) is **one new sink file + one
registration line** — no call-site churn.

## Event catalogue

`?adebug` in the URL logs every fired event to the console (`[analytics] …`).

| Group | Event · props |
|-------|---------------|
| Session | `app_load` `{ shared, embed, start_mode, start_skin, surface, source }` |
| Modes & camera | `mode_enter` / `mode_exit` `{ mode: orbit\|fly\|walk\|stargaze }` · `camera_view` `{ view: chase\|eye\|cockpit, mode }` · `takeoff` · `auto_walk` `{ on }` · `view_lock` `{ on }` |
| Look / theme | `look_matrix` `{ on }` · `look_neon` `{ on }` · `theme` `{ bg: dark\|paper }` |
| Map & plane | `map_source` `{ source }` · `map_surface` `{ surface }` · `plane_skin` `{ skin }` · `spin` `{ dir: off\|cw\|ccw }` · `layer_toggle` `{ layer, on }` |
| Manual weather | `weather_toggle` `{ kind, on }` · `typhoon` `{ signal }` · `wind` `{ dir, strength_bucket }` · `live_weather` `{ on }` |
| Sky / time | `sky_mode` `{ mode: live\|fixed\|off }` · `sky_time_scrub` `{ via }` · `sound` `{ on }` |
| Stargaze | `sg_orient` `{ on }` · `sg_clock` `{ on }` · `sg_time_mode` `{ mode }` · `constellation_tap` `{ on }` · `gps` `{ state: follow\|compass\|off }` |
| Share | `share_open` · `share_action` `{ channel: copy\|embed\|native\|x\|threads\|whatsapp }` |
| Chrome / help / info | `settings_open` · `panel_collapse` `{ via }` · `help_open` · `credits_open` · `weather_panel_open` · `fullscreen` `{ on }` · `screenshot` · `reset_view` · `language` `{ to: en\|zh }` · `compass_click` `{ dir }` · `topo_rotate` `{ delta }` |
| PWA | `install_prompt_shown` `{ platform }` · `install_result` `{ outcome }` · `coach_dismiss` |

### Notes on a couple of catalogue items

- **`weather_lock`** in the original spec maps to the `#wxlock` element, which is a
  **read-only status note** (shown under live weather / a storm signal / stargaze),
  not a user control. Its state is fully derived from `live_weather`, `typhoon` and
  the stargaze `mode_enter/exit` events we already fire, so there is no separate
  genuine user action to instrument. It is intentionally **not** a distinct event.
- **`wind`** fires from both the direction `<select>` and the strength slider commit;
  each carries `dir` + `strength_bucket` (`calm|light|moderate|strong|severe`).

## Verifying (Vercel)

On the production deploy, confirm events land in **Vercel Analytics → Events**.
Custom events only appear on the deployed site where `/_vercel/insights/script.js`
resolves (they no-op on forks / localhost). Interact with the viewer (switch modes,
toggle weather, open Share, etc.) and the event names above should appear.
