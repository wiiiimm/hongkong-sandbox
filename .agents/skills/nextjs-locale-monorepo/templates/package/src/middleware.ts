import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import type { I18nConfig } from './config';
import { createI18nConfig } from './config';
import {
  extractLocaleFromPath,
  getLocaleFromRequest,
  shouldSkipMiddleware,
} from './utils';

/** Stamp the active locale on a response: header, Vary, and cookie (on change). */
export function setLocaleOnResponse(
  response: NextResponse,
  request: NextRequest,
  locale: string,
  config: Required<I18nConfig>,
  varyOnNegotiation = false
): NextResponse {
  // NOTE: this stamps x-locale on the *response* (diagnostics / downstream
  // proxies) — it is NOT visible to server components via headers(). Those read
  // the locale from the [locale] route param, not this header. To expose the
  // locale to the app's request pipeline instead, forward it on next():
  // NextResponse.next({ request: { headers: (() => { const h = new Headers(
  //   request.headers); h.set('x-locale', locale); return h; })() } }).
  response.headers.set('x-locale', locale);

  // Cache must vary by the inputs that decide the locale — but only when the
  // locale was actually negotiated from those inputs (the redirect branch).
  // On an already-prefixed path the locale comes from the URL, so varying on
  // Cookie/Accept-Language would fragment the CDN cache pointlessly.
  if (varyOnNegotiation) {
    const vary = response.headers.get('Vary');
    const needed = ['Accept-Language', 'Cookie'];
    const current = new Set(
      (vary ?? '').split(',').map((s) => s.trim()).filter(Boolean)
    );
    for (const h of needed) current.add(h);
    response.headers.set('Vary', Array.from(current).join(', '));
  }

  const currentCookie = request.cookies.get(config.cookieName)?.value;
  if (currentCookie !== locale) {
    const isSecure = request.nextUrl.protocol === 'https:';
    response.cookies.set(config.cookieName, locale, {
      ...config.cookieOptions,
      path: config.cookieOptions.path ?? '/',
      secure: config.cookieOptions.secure ?? isSecure,
    });
  }

  return response;
}

/**
 * Build the i18n middleware. Returns a function that returns:
 *  - undefined  → skipped (static/api) — let the app's middleware continue
 *  - a redirect → unprefixed path sent to /<locale>/…
 *  - next()     → prefixed path, locale stamped on the response
 */
export function createI18nMiddleware(userConfig: I18nConfig) {
  const config = createI18nConfig(userConfig);

  return function i18nMiddleware(request: NextRequest): NextResponse | undefined {
    const { pathname } = request.nextUrl;

    if (shouldSkipMiddleware(pathname)) {
      return undefined;
    }

    const hasLocale = !!extractLocaleFromPath(pathname, config.locales);

    if (!hasLocale) {
      const locale = getLocaleFromRequest(request, config);

      // Match createLocalizedUrl(): root `/` → `/<locale>` (no trailing slash),
      // so the redirect lands on the canonical path and avoids an extra
      // trailing-slash canonicalization hop.
      const localizedPath = `/${locale}${pathname === '/' ? '' : pathname}`;

      // Preserve the query string. clone() exists in the real runtime; the else
      // branch keeps unit tests (no clone) working. (URL hashes never reach the
      // server, so there is nothing to carry over there.)
      let url: URL;
      if (request.nextUrl.clone) {
        url = request.nextUrl.clone();
        url.pathname = localizedPath;
      } else {
        const urlObj = new URL(request.url);
        url = new URL(localizedPath, urlObj.origin);
        url.search = urlObj.search;
      }

      const response = NextResponse.redirect(url.toString());
      // Locale negotiated from Cookie / Accept-Language → Vary on them.
      return setLocaleOnResponse(response, request, locale, config, true);
    }

    const locale = extractLocaleFromPath(pathname, config.locales)!;
    const response = NextResponse.next();
    // Already-prefixed: locale comes from the path, so no negotiation Vary.
    return setLocaleOnResponse(response, request, locale, config, false);
  };
}

/** One-shot convenience wrapper around createI18nMiddleware. */
export function i18nMiddleware(
  request: NextRequest,
  config: I18nConfig
): NextResponse | undefined {
  return createI18nMiddleware(config)(request);
}
