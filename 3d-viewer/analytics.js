// analytics.js — provider-agnostic custom-event analytics for the viewer (HKS-102).
//
// Call sites only ever touch track() / trackDebounced(). Providers ("sinks") live
// behind small adapters, so adding a new one (GA4, Plausible, PostHog…) is one sink
// file + one registration line — with zero changes at any call site.
//
// The library owns everything that must NOT be duplicated per call site:
//   • base props     — locale / mode / theme / device are attached ONCE, centrally.
//   • gating         — embed mode + programmatic URL-state restore are skipped here.
//   • debounce       — slider commits fan out one event, not one per input tick.
//   • canonical shape — { name, props } with string/number/boolean values only.
//   • naming         — canonical, stable, low-cardinality names; sinks re-case them.
//
// Build-free: a single vanilla ES module, no npm, no bundler.

let enabled = false;              // master gate (embed / consent) — set by initAnalytics
let armed = false;                // only fire after boot + URL restore have finished
let debug = false;
let restoringFn = () => false;    // returns true while applyState() replays URL state
let baseFn = () => ({});          // returns the shared base props (locale/mode/theme/device)
const sinks = [];

// ---------------------------------------------------------------------------
// setup
// ---------------------------------------------------------------------------

// initAnalytics({ enabled, debug, baseProps, isRestoring, sinks }) — register the
// enabled sinks and wire the central base-props + restore gate. Safe to call once
// during boot; track() stays inert until armAnalytics() is called.
export function initAnalytics(opts = {}) {
  enabled = opts.enabled !== false;
  debug = !!opts.debug;
  if (typeof opts.baseProps === 'function') baseFn = opts.baseProps;
  if (typeof opts.isRestoring === 'function') restoringFn = opts.isRestoring;
  for (const s of (opts.sinks || [])) registerSink(s);
  return { sinks: sinks.map(s => s.id) };
}

// registerSink(sink) — a sink is { id, init?(), send(evt) }. init() may return false
// to opt out (e.g. a provider with no configured key yet); it never throws upstream.
export function registerSink(sink) {
  if (!sink || !sink.id) return false;
  if (sinks.some(s => s.id === sink.id)) return false;
  try { if (typeof sink.init === 'function' && sink.init() === false) return false; }
  catch (_) { /* a broken init must not take the app (or other sinks) down */ }
  sinks.push(sink);
  return true;
}

// Arm the pipeline once the initial load + URL-state restore are complete, so the
// boot apply never inflates counts. Everything before this is silently dropped.
export function armAnalytics() { armed = true; }
export function setEnabled(v) { enabled = !!v; }
export function activeSinks() { return sinks.map(s => s.id); }

// ---------------------------------------------------------------------------
// emit
// ---------------------------------------------------------------------------

// track(name, props) — the single analytics entry point for the whole app.
export function track(name, props = {}) {
  if (!enabled || !armed) return;   // consent/embed gate + boot gate
  if (restoringFn()) return;        // URL-state restore / any programmatic set
  const evt = { name, props: { ...safeBase(), ...clean(props) } };
  if (debug) { try { console.debug('[analytics]', evt.name, evt.props); } catch (_) {} }
  for (const s of sinks) { try { s.send(evt); } catch (_) {} }
}

// trackDebounced(name, props, wait) — for sliders / rapid toggles. Keyed by name so
// two different controls debouncing at once don't clobber each other.
const _timers = new Map();
export function trackDebounced(name, props = {}, wait = 500) {
  clearTimeout(_timers.get(name));
  _timers.set(name, setTimeout(() => { _timers.delete(name); track(name, props); }, wait));
}

function safeBase() { try { return clean(baseFn()); } catch (_) { return {}; } }

// Keep only finite string / number / boolean values (both Vercel and GA4 reject
// objects & arrays). null / undefined / objects / arrays / functions are dropped —
// this is also the privacy backstop: it structurally refuses anything that isn't a
// plain scalar, so a stray object can never leak through.
function clean(o) {
  const out = {};
  if (!o) return out;
  for (const k in o) {
    const v = o[k];
    const t = typeof v;
    if (t === 'string' || t === 'boolean') out[k] = v;
    else if (t === 'number' && Number.isFinite(v)) out[k] = v;
    // everything else (null/undefined/object/array/function/symbol/NaN) is dropped
  }
  return out;
}

// ---------------------------------------------------------------------------
// sinks
// ---------------------------------------------------------------------------

// VercelSink — Vercel Web Analytics custom events (loaded script-tag form in
// index.html). No-ops whenever window.va is absent (forks / localhost / other hosts),
// so it is always safe to register.
export function VercelSink() {
  return {
    id: 'vercel',
    init() { return true; },
    send(evt) {
      const va = (typeof window !== 'undefined') && window.va;
      if (typeof va !== 'function') return;                 // script not present → no-op
      va('event', { name: evt.name, ...evt.props });
    },
  };
}

// GA4Sink — the "next" provider (HKS-102 scope split #2). Loads gtag.js lazily and
// maps the canonical event to GA4's API. Enabling GA4 later is literally one line:
//   registerSink(GA4Sink({ measurementId: 'G-XXXXXXX' }))
// (or set window.__GA4_ID). No call-site edits. init() opts out until an ID exists.
//
// GA4 constraints handled here: snake_case event + param names, ≤ 25 params, only
// string/number values (enforced by clean() upstream), and locale sent both as an
// event param AND a user_property so GA4 segments by language natively.
export function GA4Sink(opts = {}) {
  const id = opts.measurementId || '';
  let ready = false;
  return {
    id: 'ga4',
    init() {
      if (!id || typeof document === 'undefined') return false;   // no property yet → skip
      const s = document.createElement('script');
      s.async = true;
      s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
      document.head.appendChild(s);
      window.dataLayer = window.dataLayer || [];
      window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
      window.gtag('js', new Date());
      window.gtag('config', id, { send_page_view: false });     // pageviews come from the base tag
      ready = true;
      return true;
    },
    send(evt) {
      if (!ready || typeof window.gtag !== 'function') return;
      const params = {};
      let n = 0;
      for (const k in evt.props) {
        if (n++ >= 25) break;                                    // GA4 caps params per event
        params[ga4Key(k)] = evt.props[k];
      }
      if (evt.props.locale)                                      // segment by language natively
        window.gtag('set', 'user_properties', { locale: evt.props.locale });
      window.gtag('event', ga4Key(evt.name), params);
    },
  };
}

// canonical name → GA4 snake_case (our names are already snake_case, so this is a
// no-op for them; it just guards any stray camelCase / punctuation).
function ga4Key(s) {
  return String(s)
    .replace(/([a-z0-9])([A-Z])/g, '$1_$2')
    .toLowerCase()
    .replace(/[^a-z0-9_]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .slice(0, 40);
}
