/** Portable local browser selection; explicit overrides never silently fall back. */
import {existsSync} from 'node:fs';
import {join} from 'node:path';
export function browserExecutable(chromium, env=process.env, exists=existsSync) {
  const explicit=env.CHROME_PATH || env.CHROMIUM_EXECUTABLE_PATH;
  if(explicit){if(!exists(explicit))throw new Error(`Browser executable does not exist: ${explicit}`);return explicit;}
  const candidates=[
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    chromium.executablePath(),
    '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium', '/usr/bin/chromium-browser', '/opt/google/chrome/chrome',
    ...[env.PROGRAMFILES,env['PROGRAMFILES(X86)'],env.LOCALAPPDATA].filter(Boolean).map(p=>join(p,'Google','Chrome','Application','chrome.exe')),
  ];
  const found=candidates.find(p=>p && exists(p));
  if(!found)throw new Error('No local Chrome/Chromium found. Set CHROME_PATH or CHROMIUM_EXECUTABLE_PATH, or install the project Playwright Chromium browser.');
  return found;
}
