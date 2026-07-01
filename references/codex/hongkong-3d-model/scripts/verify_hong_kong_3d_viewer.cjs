const { chromium } = require('/Users/williamli/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/.pnpm/playwright@1.61.0/node_modules/playwright');

const VIEWER_URL = 'http://127.0.0.1:4173/hongkong-3d-model/hong-kong-3d-viewer.html';
const OUT_DIR = 'codex/reference/3d-viewer';

async function verifySource(page, value, expectedText, screenshotName) {
  await page.goto(VIEWER_URL, { waitUntil: 'domcontentloaded' });
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.locator('#quality').selectOption('detail');
  await page.locator('#source').selectOption(value);
  await page.waitForTimeout(4200);
  const readout = await page.locator('#readout').textContent();
  if (!readout || !readout.includes(expectedText) || !readout.includes('detail') || !readout.includes('B50K skin')) {
    throw new Error(`Unexpected readout: ${readout}`);
  }
  const canvas = await page.locator('#scene').boundingBox();
  if (!canvas || canvas.width < 1200 || canvas.height < 800) {
    throw new Error(`Canvas did not fill viewport: ${JSON.stringify(canvas)}`);
  }
  const checkedLayers = await page.locator('input[data-layer]:checked').count();
  if (checkedLayers < 3) {
    throw new Error(`Expected default B50K skin layers to be enabled, got ${checkedLayers}`);
  }
  await page.locator('#skin-toggle').uncheck();
  const skinEnabled = await page.locator('#skin-toggle').isChecked();
  if (skinEnabled) {
    throw new Error('B50K skin master toggle did not turn off');
  }
  await page.locator('#skin-toggle').check();
  const output = `${OUT_DIR}/${screenshotName}`;
  await page.screenshot({ path: output, fullPage: true });
  console.log(`${output} ${Math.round(canvas.width)}x${Math.round(canvas.height)} ${readout}`);
}

async function verifyLantauSource(page, value, expectedText, screenshotName) {
  await page.goto(VIEWER_URL, { waitUntil: 'domcontentloaded' });
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.locator('#source').selectOption(value);
  await page.waitForTimeout(2400);
  const readout = await page.locator('#readout').textContent();
  if (!readout || !readout.includes(expectedText) || !readout.includes('B50K skin') || readout.includes('detail')) {
    throw new Error(`Unexpected Lantau readout: ${readout}`);
  }
  const qualityDisabled = await page.locator('#quality').isDisabled();
  const skinDisabled = await page.locator('#skin-toggle').isDisabled();
  if (!qualityDisabled || skinDisabled) {
    throw new Error(`Expected Lantau source to disable quality but keep B50K controls available`);
  }
  await page.locator('#skin-toggle').uncheck();
  if (await page.locator('#skin-toggle').isChecked()) {
    throw new Error('Lantau B50K skin master toggle did not turn off');
  }
  await page.locator('#skin-toggle').check();
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
  await verifySource(page, 'hk-landsd-5m', 'Hong Kong LandsD 5 m DTM', 'hong-kong-hk-landsd-5m-b50k.png');
  await verifySource(page, 'aws-terrarium', 'AWS Terrarium Terrain Tiles', 'hong-kong-aws-terrarium-b50k.png');
  await verifyLantauSource(page, 'lantau-hk-landsd-5m', 'Lantau LandsD 5 m DTM', 'combined-lantau-hk-landsd-5m.png');
  await verifyLantauSource(page, 'lantau-aws-terrarium', 'Lantau AWS Terrarium Terrain Tiles', 'combined-lantau-aws-terrarium.png');
  await browser.close();
})().catch(error => {
  console.error(error);
  process.exit(1);
});
