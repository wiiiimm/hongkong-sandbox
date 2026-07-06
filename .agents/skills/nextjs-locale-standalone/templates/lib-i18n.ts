// lib/i18n.ts — locale config + pure detection helpers (no Next imports, so it
// is safe to import from the proxy, server components, and client components).

export interface Language {
  id: string; // BCP-47-ish locale id used as the URL prefix, e.g. 'en-hk'
  title: string; // human label for the toggle
  isDefault?: boolean;
}

export const supportedLanguages: Language[] = [
  { id: 'en-hk', title: 'English (HK)', isDefault: true },
  { id: 'zh-hk', title: '繁體中文（香港）' },
];

export const locales = supportedLanguages.map((l) => l.id);
export const defaultLocale = (
  supportedLanguages.find((l) => l.isDefault) ?? supportedLanguages[0]
).id;

export const LOCALE_COOKIE = 'NEXT_LOCALE';

/** Case-insensitive lookup → the canonical supported locale id, or null. */
export function canonicalizeLocale(
  candidate: string | null | undefined
): string | null {
  if (!candidate) return null;
  const lower = candidate.toLowerCase();
  return locales.find((l) => l.toLowerCase() === lower) ?? null;
}

/** First path segment, if it is a supported locale. */
export function extractLocaleFromPath(pathname: string): string | null {
  return canonicalizeLocale(pathname.split('/')[1]);
}

/** Strip the locale prefix: '/zh-hk/about' → '/about'. */
export function removeLocaleFromPath(pathname: string): string {
  const locale = extractLocaleFromPath(pathname);
  // `locale` is canonical (lowercase) but the URL segment may be any case
  // (`/EN-HK/about`), so match the leading segment case-insensitively and only
  // at a `/` boundary (never mid-path).
  return locale
    ? pathname.replace(new RegExp(`^/${locale}(?=/|$)`, 'i'), '') || '/'
    : pathname;
}

export function isValidLocale(locale: string): boolean {
  return canonicalizeLocale(locale) !== null;
}

/** Parse an Accept-Language header into locales ordered by q-value (desc). */
function parseAcceptLanguage(header: string): string[] {
  return header
    .split(',')
    .map((part) => {
      // Split off the locale, then find the q-param tolerating optional spaces
      // (`en-US; q=0.8`). Missing q → 1. Only a well-formed 0–1 weight counts;
      // malformed/out-of-range (`q=2`, `q=0.8junk`) → NaN so it's dropped below
      // rather than silently outranking valid locales.
      const [rawLoc, ...params] = part.trim().split(';');
      const qParam = params
        .map((p) => p.trim())
        .find((p) => p.toLowerCase().startsWith('q='));
      const qRaw = qParam === undefined ? '1' : qParam.slice(2).trim();
      const q = /^\d+(\.\d+)?$/.test(qRaw) ? Number.parseFloat(qRaw) : Number.NaN;
      return { loc: rawLoc.trim().toLowerCase(), q };
    })
    // `q=0` rejects that locale; valid weights are 0–1. Keep only well-formed,
    // in-range, positive qualities (drops `q=0`, NaN, and out-of-range like `q=2`).
    .filter((x) => x.loc && x.q > 0 && x.q <= 1)
    .sort((a, b) => b.q - a.q)
    .map((x) => x.loc);
}

/**
 * Best supported locale for an Accept-Language header, or null.
 * Tries exact matches first, then primary-subtag matches (zh-TW → zh-hk).
 */
export function matchAcceptLanguage(header: string | null): string | null {
  if (!header) return null;
  const prefs = parseAcceptLanguage(header);

  for (const p of prefs) {
    const exact = canonicalizeLocale(p);
    if (exact) return exact;
  }
  for (const p of prefs) {
    const lang = p.split('-')[0];
    const match = locales.find(
      (l) => l.toLowerCase() === lang || l.toLowerCase().startsWith(`${lang}-`)
    );
    if (match) return match;
  }
  return null;
}
