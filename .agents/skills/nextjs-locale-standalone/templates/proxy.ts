// proxy.ts  (Next.js 16+)
//
// On Next.js ≤15, name this file `middleware.ts` and rename the exported
// `proxy` function to `middleware`. The body is identical.
//
// Redirects any unprefixed path to `/<locale>/…`, choosing the locale by:
//   1. NEXT_LOCALE cookie  (the toggle's last choice)
//   2. Accept-Language     (the browser)
//   3. defaultLocale
// Already-prefixed paths pass through and get the locale stamped on the response.

import { NextResponse, type NextRequest } from 'next/server';
import {
  LOCALE_COOKIE,
  canonicalizeLocale,
  defaultLocale,
  extractLocaleFromPath,
  matchAcceptLanguage,
} from '@/lib/i18n';

const HAS_FILE_EXT = /\.[a-z0-9]+(?:$|[?#])/i;

function shouldSkip(pathname: string): boolean {
  return (
    // Segment-aware (like /api below) so a real route such as /_nextjs isn't
    // skipped — only Next's own /_next/* internals.
    pathname.startsWith('/_next/') ||
    pathname === '/_next' ||
    pathname === '/api' ||
    pathname.startsWith('/api/') || // not '/api' alone — would catch '/apiary'
    pathname.startsWith('/.well-known') ||
    pathname.startsWith('/favicon') ||
    HAS_FILE_EXT.test(pathname)
  );
}

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  if (shouldSkip(pathname)) return;

  const current = extractLocaleFromPath(pathname);

  if (!current) {
    const fromCookie = canonicalizeLocale(
      request.cookies.get(LOCALE_COOKIE)?.value
    );
    const locale =
      fromCookie ??
      matchAcceptLanguage(request.headers.get('accept-language')) ??
      defaultLocale;

    const url = request.nextUrl.clone();
    // Root `/` → `/<locale>` (no trailing slash), so the redirect lands on the
    // canonical path and avoids an extra trailing-slash canonicalization hop.
    url.pathname = `/${locale}${pathname === '/' ? '' : pathname}`;
    // The locale here was negotiated from Cookie / Accept-Language → Vary on them.
    return stampLocale(NextResponse.redirect(url), request, locale, true);
  }

  // Already-prefixed: the locale comes from the path, so do NOT Vary on
  // Cookie/Accept-Language — that would fragment the CDN cache pointlessly.
  return stampLocale(NextResponse.next(), request, current, false);
}

function stampLocale(
  res: NextResponse,
  req: NextRequest,
  locale: string,
  varyOnNegotiation: boolean
): NextResponse {
  res.headers.set('x-locale', locale);

  // Caching must vary by the inputs that decide the locale — but only when the
  // locale was actually negotiated from those inputs (the redirect branch).
  if (varyOnNegotiation) {
    const vary = new Set(
      (res.headers.get('Vary') ?? '')
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean)
    );
    vary.add('Accept-Language');
    vary.add('Cookie');
    res.headers.set('Vary', [...vary].join(', '));
  }

  // Remember the active locale (also persists a toggle choice) — only on change.
  if (req.cookies.get(LOCALE_COOKIE)?.value !== locale) {
    res.cookies.set(LOCALE_COOKIE, locale, {
      path: '/',
      sameSite: 'lax',
      // Server-only by default: nothing reads NEXT_LOCALE from client JS (the
      // toggle relies on the proxy rewriting the cookie; the server reads it via
      // request.cookies). httpOnly:true keeps it out of reach of injected
      // scripts. Set false only if client JS genuinely must read it.
      httpOnly: true,
      secure: req.nextUrl.protocol === 'https:',
      maxAge: 60 * 60 * 24 * 365,
    });
  }

  return res;
}

export const config = {
  matcher: ['/((?!_next(?:/|$)|api(?:/|$)|.*\\..*).*)'],
};
