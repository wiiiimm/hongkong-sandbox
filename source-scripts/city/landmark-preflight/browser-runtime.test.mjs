import {test} from 'node:test';
import assert from 'node:assert/strict';
import {browserExecutable} from './browser-runtime.mjs';
const chromium={executablePath:()=>'/playwright/chromium'};
test('explicit browser takes priority and invalid override fails',()=>{
 assert.equal(browserExecutable(chromium,{CHROME_PATH:'/custom'},p=>p==='/custom'),'/custom');
 assert.throws(()=>browserExecutable(chromium,{CHROME_PATH:'/missing'},p=>p==='/playwright/chromium'),/does not exist/);
});
test('Playwright fallback and missing installation are explicit',()=>{
 assert.equal(browserExecutable(chromium,{},p=>p==='/playwright/chromium'),'/playwright/chromium');
 assert.equal(browserExecutable(chromium,{CHROMIUM_EXECUTABLE_PATH:'/custom'},p=>p==='/custom'),'/custom');
 assert.throws(()=>browserExecutable(chromium,{},()=>false),/No local Chrome/);
});
