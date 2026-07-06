'use client';

import { createContext, useContext, type ReactNode } from 'react';

interface LocaleContextValue {
  locale: string;
}

const LocaleContext = createContext<LocaleContextValue | null>(null);

export interface LocaleProviderProps {
  children: ReactNode;
  locale: string;
}

/** Makes the current locale available to all client components below it. */
export function LocaleProvider({ children, locale }: LocaleProviderProps) {
  if (!locale) {
    throw new Error('LocaleProvider: locale prop is required');
  }
  return (
    <LocaleContext.Provider value={{ locale }}>
      {children}
    </LocaleContext.Provider>
  );
}

function useLocaleContext(): LocaleContextValue {
  const context = useContext(LocaleContext);
  if (!context) {
    throw new Error(
      'useCurrentLocale must be used within a LocaleProvider. ' +
        'Wrap your app with <LocaleProvider locale={locale}>'
    );
  }
  return context;
}

export function useCurrentLocale(): string {
  return useLocaleContext().locale;
}

export function useIsLocale(targetLocale: string): boolean {
  return useCurrentLocale() === targetLocale;
}

export function useLocaleInfo() {
  const locale = useCurrentLocale();
  // The URL segment may be any case (`/EN-HK/…` is accepted), so normalize
  // before matching language/region — otherwise `en-HK`/`zh-TW` slip through.
  const lower = locale.toLowerCase();
  return {
    locale,
    isEnglish: lower.startsWith('en'),
    isChinese: lower.startsWith('zh'),
    isHongKong: lower.endsWith('-hk'),
    isTaiwan: lower.endsWith('-tw'),
    isMainland: lower.endsWith('-cn'),
  };
}
