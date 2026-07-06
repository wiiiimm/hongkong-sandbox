---
name: nextjs-locale-standalone
description: Add locale-prefixed i18n routing to a single (non-monorepo) Next.js App Router site — a middleware/proxy that redirects `/` and any unprefixed path to `/<locale>/…` using the locale toggle's last choice (the NEXT_LOCALE cookie) then the browser's Accept-Language, a `[locale]` layout with a LocaleProvider + hooks, and a LocaleToggle that persists the choice. Use when adding bilingual/multilingual routing to a standalone Next.js site, building `/en-hk/…` `/zh-hk/…` URL namespaces, redirecting the root to a default-or-remembered locale, persisting a language switch across visits, or detecting browser language in middleware. For a monorepo that shares this logic across several apps via a workspace package, use nextjs-locale-monorepo instead.
metadata:
  author: stealth-engine
  co-author: wiiiimm
  version: "1.1.0"
---

# Next.js locale routing — standalone site

Locale-prefixed routing for one Next.js App Router app, no shared package. Every
page lives under `/<locale>/…`; a proxy (middleware) sends unprefixed requests to
the right locale. Drop-in copy-paste files are in [`templates/`](./templates).

> Sibling skill: **nextjs-locale-monorepo** — the same behaviour factored into a
> shared workspace package for multi-app repos. Keep the two in sync.

## The behaviour (the spec both skills implement)

- **URLs are locale-namespaced:** `/en-hk/about`, `/zh-hk/about`. One locale is
  the default.
- **The proxy redirects unprefixed paths.** A request to `/about` (or `/`) with no
  known locale prefix is 307-redirected to `/<locale>/about`, preserving the query
  string. (URL hashes are client-side only — they never reach the server, so the
  proxy can't and needn't carry them; the LocaleToggle, running in the browser,
  does preserve the hash.) The locale is resolved by this **priority**:
  1. **`NEXT_LOCALE` cookie** — the toggle's last choice (if the visitor has ever switched).
  2. **`Accept-Language`** — the browser's preferred language (exact match, then language-only, e.g. `zh` → `zh-hk`).
  3. **Default locale.**
- **Already-prefixed paths pass through** (`NextResponse.next()`), and the proxy
  stamps the response: `x-locale` header and a (re)write of `NEXT_LOCALE` when it
  differs. It does **not** add `Vary: Accept-Language, Cookie` here — on a prefixed
  path the locale is fixed by the URL, so varying on those inputs would fragment
  the CDN cache for nothing. Only the negotiated **redirect** sets that `Vary`.
- **The toggle persists via that cookie.** The LocaleToggle just navigates to
  `/<newLocale>/…`; the proxy, seeing a prefixed path, writes `NEXT_LOCALE` — so
  the next time the visitor lands on `/`, step 1 sends them back to that choice.
  (The toggle doesn't set the cookie itself; the proxy is the single writer.)

## Files to create

| File | Role |
| --- | --- |
| `lib/i18n.ts` | `supportedLanguages`, `locales`, `defaultLocale`, cookie name, and pure detection helpers (no Next imports) |
| `proxy.ts` (Next 16) / `middleware.ts` (≤15) | the redirect + stamp logic |
| `app/[locale]/layout.tsx` | validates the locale, `generateStaticParams`, renders `<html lang>`, wraps in `LocaleProvider` |
| `app/locale-provider.tsx` | `'use client'` context + `useCurrentLocale` / `useIsLocale` |
| `components/LocaleToggle.tsx` | switches locale by rewriting the first path segment |

Copy them from [`templates/`](./templates) and adjust `supportedLanguages`.

## Wiring steps

1. **Define locales** in `lib/i18n.ts` (`{ id, title, isDefault? }[]`).
2. **Move pages under `app/[locale]/`.** In the App Router the *root* layout — the
   topmost `layout.tsx` — is the one that must render `<html>` + `<body>`, and
   Next errors if it doesn't. So make `app/[locale]/layout.tsx` *be* that root
   layout and have **no `app/layout.tsx` at all** — valid as long as every page
   lives under `[locale]`. (`app/globals.css`, `app/global-error.tsx`, `app/api/*`,
   `app/icon.png` stay at `app/`.) Don't keep a pass-through `app/layout.tsx` that
   returns bare `children`: it would be the root layout, and Next rejects a root
   layout without `<html>`/`<body>`. You also can't read the `[locale]` param up
   there, so there's no reason to keep it — delete it and let `[locale]` be root.
3. **Add the proxy** at the project root and the matcher (below).
4. **Add the toggle** somewhere in the layout/nav.

## Next 16: `proxy.ts` vs `middleware.ts`

Next 16 renamed the convention: the file is `proxy.ts` and the export is
`export function proxy(...)`. On Next ≤15 it's `middleware.ts` /
`export function middleware(...)` — **the body of *this* template is identical**,
only the file and function names change. **`proxy` is the go-forward direction** —
`middleware` is deprecated; Next 16 still runs a `middleware.ts` but logs a
deprecation warning and is positioning it as the edge-only escape hatch (below),
not the default. So **on Next 16+ default to `proxy.ts`**; reach for
`middleware.ts` only on Next ≤15 or when you specifically need the edge runtime.
The template ships as `proxy.ts`. Migrate an existing
file with `npx @next/codemod middleware-to-proxy .` (it also renames config flags
like `skipMiddlewareUrlNormalize` → `skipProxyUrlNormalize` and types
`NextMiddleware` → `NextProxy`).

**The rename is not purely cosmetic — `proxy` is Node.js-only.** `proxy.ts`
defaults to the **Node.js runtime and you cannot change it** — setting the
`runtime` config in a proxy file *throws*. (Middleware historically ran on the
**edge** runtime; Node support went stable in 15.5, and 16 made Node the locked
default.) For this locale logic that's a non-issue — redirects, rewrites, and
cookie stamping don't need edge. **But if you need the edge runtime, keep
`middleware.ts`** (Next will add edge guidance for proxy in a later release).
Conceptually Next now frames this feature as a **network boundary / gateway**, to
be used sparingly (redirects, rewrites, header/cookie stamping, light gating) —
not a place for app logic. Don't trust it as the *only* auth gate: a matcher
change can silently drop coverage (including Server Functions), so verify auth in
the route/Server Function too.

The matcher excludes assets and API so they never redirect:

```ts
export const config = { matcher: ['/((?!_next(?:/|$)|api(?:/|$)|.*\\..*).*)'] };
```

The `(?:/|$)` after `_next` and `api` anchors them to a path segment, so real
pages like `/apiary` still get locale-prefixed (a bare `api` would skip them).

Also guard inside the function (`shouldSkip`) for `/_next`, `/api`,
`/.well-known`, `/favicon`, and anything with a file extension — the matcher and
the guard are belt-and-suspenders.

## Gotchas

- **Cookie defaults to `httpOnly: true`** — nothing reads `NEXT_LOCALE` from
  client JS (the toggle relies on the proxy rewriting it; the server reads it via
  `request.cookies`), so keep it out of reach of injected scripts. Set
  `httpOnly: false` only if client code/analytics genuinely must read the active
  locale. `sameSite: 'lax'`, `secure` on HTTPS, 1-year `maxAge`.
- **Set `Vary: Accept-Language, Cookie`** on the *negotiated redirect* (the proxy
  does) so a CDN never serves one visitor's locale to another. Prefixed pass-through
  responses skip it — their locale is fixed by the URL, so the extra `Vary` would
  only fragment the cache.
- **Language-only fallback matters:** a browser sending `zh-TW` or `zh` should
  resolve to your `zh-hk`. The matcher in `lib/i18n.ts` tries exact, then the
  primary subtag.
- **Don't redirect-loop:** only redirect when `extractLocaleFromPath` returns
  null. Prefixed paths must pass through.
- **Invalid locales still 404, but via a prefixed path.** The proxy can't tell an
  unsupported first segment (`/xx/about`) from a normal page path (`/products/x`) —
  both have a non-locale first segment — so it prefixes *both*: `/xx/about` →
  `/en-hk/xx/about`, which 404s because no such page route exists. So a bad locale
  still yields a 404, just under a `/<default>/…` URL rather than as a bare `/xx/…`.
  Don't expect the proxy to leave `/xx/…` untouched. The layout's `notFound()`
  (below) is the backstop for the cases the proxy doesn't intercept.
- **Locale validity in the layout:** keep `notFound()` for an unknown `[locale]`
  as defense-in-depth — it catches an invalid locale that reaches `[locale]`
  directly (un-proxied render, an excluded matcher path) so it 404s instead of
  rendering with a bogus `lang`.

## Verify

- `curl -sI localhost:3000/` → `307` to `/<default>` (no trailing slash; no cookie, no Accept-Language).
- `curl -sI -H 'Accept-Language: zh-HK' localhost:3000/about` → `307` to `/zh-hk/about`.
- `curl -sI --cookie 'NEXT_LOCALE=zh-hk' localhost:3000/` → `307` to `/zh-hk` even with an English `Accept-Language` (cookie wins).
- Visiting `/zh-hk/x` sets `NEXT_LOCALE=zh-hk` in the response `Set-Cookie`.
