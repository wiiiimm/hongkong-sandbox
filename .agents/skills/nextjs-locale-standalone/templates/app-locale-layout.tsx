// app/[locale]/layout.tsx
//
// This is the ROOT layout (renders <html>/<body>) — there is no app/layout.tsx.
// Valid as long as every page lives under app/[locale]/.

import { notFound } from 'next/navigation';
import { supportedLanguages } from '@/lib/i18n';
import { LocaleProvider } from '@/app/locale-provider';
import '../globals.css';

// Pre-render one tree per locale.
export function generateStaticParams() {
  return supportedLanguages.map((l) => ({ locale: l.id }));
}

type Params = { locale: string };

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  // Next 15 made `params` a Promise; Next 14 passes it synchronously. Accept
  // both and `await Promise.resolve(...)` so the layout works on either major.
  params: Params | Promise<Params>;
}) {
  const { locale: rawLocale } = await Promise.resolve(params);
  // Match case-insensitively (URLs may arrive as `/EN-HK/…`) but render with the
  // canonical id so the provider and `<html lang>` always get the supported casing.
  const lang = supportedLanguages.find(
    (l) => l.id.toLowerCase() === rawLocale.toLowerCase()
  );
  if (!lang) notFound();
  const locale = lang.id;

  return (
    <html lang={locale}>
      <body>
        <LocaleProvider locale={locale}>{children}</LocaleProvider>
      </body>
    </html>
  );
}
