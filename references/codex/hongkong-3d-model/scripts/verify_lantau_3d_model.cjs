const { chromium } = require('/Users/williamli/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/.pnpm/playwright@1.61.0/node_modules/playwright');

const VIEWER_URL = 'http://127.0.0.1:4173/hongkong-3d-model/index.html';
const OUT_DIR = 'codex/reference/3d-viewer';

async function verifySource(page, value, expectedText, screenshotName) {
  await page.goto(VIEWER_URL, { waitUntil: 'domcontentloaded' });
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.locator('#source').selectOption(value);
  await page.waitForTimeout(1800);
  const readout = await page.locator('#readout').textContent();
  if (!readout || !readout.includes(expectedText)) {
    throw new Error(`Expected readout to include "${expectedText}", got: ${readout}`);
  }
  const canvas = await page.locator('#scene').boundingBox();
  if (!canvas || canvas.width < 1200 || canvas.height < 800) {
    throw new Error(`Canvas did not fill viewport: ${JSON.stringify(canvas)}`);
  }
  const output = `${OUT_DIR}/${screenshotName}`;
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
  await verifySource(page, 'hk-landsd-5m', 'Hong Kong LandsD 5 m DTM', 'consolidated-hk-landsd-5m.png');
  await verifySource(page, 'aws-terrarium', 'AWS Terrarium Terrain Tiles', 'consolidated-aws-terrarium.png');
  await browser.close();
})().catch(error => {
  console.error(error);
  process.exit(1);
});
