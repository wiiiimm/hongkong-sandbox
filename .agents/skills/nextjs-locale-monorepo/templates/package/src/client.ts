'use client';

// Client entry point (i18n-routing/client): the React provider + hooks.
// Kept separate from the default entry so the 'use client' boundary never
// leaks into middleware / server-component import graphs.
export { LocaleProvider, type LocaleProviderProps } from './provider';
export { useCurrentLocale, useIsLocale, useLocaleInfo } from './hooks';
