export interface I18nConfig {
  locales: string[];
  defaultLocale: string;
  cookieName?: string;
  cookieOptions?: {
    path?: string;
    sameSite?: 'strict' | 'lax' | 'none';
    httpOnly?: boolean;
    secure?: boolean;
    maxAge?: number;
  };
}

export const defaultCookieOptions = {
  path: '/',
  sameSite: 'lax' as const,
  // Server-only by default: the locale cookie is read via request.cookies, never
  // document.cookie. httpOnly:true keeps it out of reach of injected scripts.
  // Override with httpOnly:false only if client JS must read it.
  httpOnly: true,
  // Persist the toggle's choice across sessions (1 year) — without maxAge this is
  // a session cookie that dies on browser close and the "choice persists" promise
  // (and parity with nextjs-locale-standalone) breaks.
  maxAge: 60 * 60 * 24 * 365,
};

export function createI18nConfig(config: I18nConfig): Required<I18nConfig> {
  if (!config.locales || config.locales.length === 0) {
    throw new Error('i18n-routing: locales array cannot be empty');
  }
  if (!config.defaultLocale) {
    throw new Error('i18n-routing: defaultLocale is required');
  }
  if (!config.locales.includes(config.defaultLocale)) {
    throw new Error('i18n-routing: defaultLocale must be included in locales array');
  }

  return {
    locales: config.locales,
    defaultLocale: config.defaultLocale,
    cookieName: config.cookieName || 'NEXT_LOCALE',
    cookieOptions: {
      ...defaultCookieOptions,
      ...config.cookieOptions,
    },
  };
}

export interface Language {
  id: string;
  title: string;
  isDefault?: boolean;
}

/** Build an I18nConfig from language objects (locales + defaultLocale). */
export function i18nConfig(
  languages: Language[],
  overrides?: Partial<Omit<I18nConfig, 'locales' | 'defaultLocale'>>
): I18nConfig {
  const defaultLang = languages.find((lang) => lang.isDefault) || languages[0];
  if (!defaultLang) {
    throw new Error('i18n-routing: at least one language is required');
  }

  return {
    locales: languages.map((lang) => lang.id),
    defaultLocale: defaultLang.id,
    ...overrides,
  };
}
