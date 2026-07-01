const { chromium } = require('/Users/williamli/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/.pnpm/playwright@1.61.0/node_modules/playwright');

async function verifyViewport(page, viewport, output) {
  await page.setViewportSize(viewport);
  await page.goto('http://127.0.0.1:4173/lantau-3d-viewer.html', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1800);
  const canvas = await page.locator('#scene').boundingBox();
  const readout = await page.locator('#readout').textContent();
  if (!canvas || canvas.width < viewport.width * 0.9 || canvas.height < viewport.height * 0.9) {
    throw new Error(`Canvas did not fill viewport: ${JSON.stringify(canvas)}`);
  }
  if (!readout || !readout.includes('vertices')) {
    throw new Error(`Readout did not load mesh metadata: ${readout}`);
  }
  await page.screenshot({ path: output, fullPage: true });
  console.log(`${output} ${Math.round(canvas.width)}x${Math.round(canvas.height)} ${readout}`);
}

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  });
  const page = await browser.newPage();
  page.on('console', msg => {
    if (msg.type() === 'error') console.error(`browser console: ${msg.text()}`);
  });
  await verifyViewport(page, { width: 1440, height: 960 }, 'codex/lantau-3d-viewer-desktop.png');
  await verifyViewport(page, { width: 390, height: 844 }, 'codex/lantau-3d-viewer-mobile.png');
  await browser.close();
})().catch(error => {
  console.error(error);
  process.exit(1);
});
