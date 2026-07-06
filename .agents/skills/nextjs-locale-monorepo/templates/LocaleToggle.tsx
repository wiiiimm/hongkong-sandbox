// apps/<app>/components/LocaleToggle.tsx
'use client';

import { useRouter, usePathname } from 'next/navigation';
import { supportedLanguages } from 'configs/locale';
import { useCurrentLocale } from 'i18n-routing/client';

export function LocaleToggle() {
  const router = useRouter();
  const pathname = usePathname();
  const current = useCurrentLocale();

  function switchTo(locale: string) {
    if (locale === current) return;

    const segments = (pathname ?? '/').split('/').filter(Boolean);
    // Match the first segment case-insensitively (the middleware/layout accept
    // `/EN-HK/…`), else `/EN-HK/x` would gain a second prefix: `/zh-hk/EN-HK/x`.
    const first = segments[0]?.toLowerCase();
    if (supportedLanguages.some((l) => l.id.toLowerCase() === first)) {
      segments[0] = locale; // replace existing prefix
    } else {
      segments.unshift(locale); // unprefixed — add one
    }

    const search = typeof window !== 'undefined' ? window.location.search : '';
    const hash = typeof window !== 'undefined' ? window.location.hash : '';
    router.push(`/${segments.join('/')}${search}${hash}`);

    // The middleware writes NEXT_LOCALE on this navigation, so the choice sticks.
  }

  return (
    <div className="flex gap-2">
      {supportedLanguages.map((l) => (
        <button
          key={l.id}
          type="button"
          onClick={() => switchTo(l.id)}
          aria-current={l.id === current ? 'true' : undefined}
          // min-w/min-h 44px → meets the 44×44 minimum touch target;
          // focus-visible ring → keyboard focus is always visible.
          className={[
            'inline-flex min-h-[44px] min-w-[44px] items-center justify-center px-3',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
            l.id === current ? 'font-semibold underline' : '',
          ]
            .filter(Boolean)
            .join(' ')}
        >
          {l.title}
        </button>
      ))}
    </div>
  );
}
