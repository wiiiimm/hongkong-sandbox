// app/locale-provider.tsx
'use client';

import { createContext, useContext, type ReactNode } from 'react';

const LocaleContext = createContext<string | null>(null);

export function LocaleProvider({
  locale,
  children,
}: {
  locale: string;
  children: ReactNode;
}) {
  if (!locale) throw new Error('LocaleProvider: locale prop is required');
  return (
    <LocaleContext.Provider value={locale}>{children}</LocaleContext.Provider>
  );
}

/** Current locale in client components. Throws if used outside the provider. */
export function useCurrentLocale(): string {
  const locale = useContext(LocaleContext);
  if (!locale) {
    throw new Error('useCurrentLocale must be used within <LocaleProvider>');
  }
  return locale;
}

export function useIsLocale(target: string): boolean {
  return useCurrentLocale() === target;
}
