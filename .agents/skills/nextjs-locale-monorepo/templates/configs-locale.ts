// packages/configs/src/locale.ts
//
// Shared single source of truth for the repo's locales. Apps, middleware,
// generateStaticParams, and toggles all read from here — adding a language is a
// one-line change that every app picks up.

export interface Language {
  id: string; // URL prefix, e.g. 'en-hk'
  title: string; // toggle label
  isDefault?: boolean;
}

export const supportedLanguages: Language[] = [
  { id: 'en-hk', title: 'English (HK)', isDefault: true },
  { id: 'zh-hk', title: '繁體中文（香港）' },
];

export const defaultLanguage =
  supportedLanguages.find((l) => l.isDefault) ?? supportedLanguages[0];
