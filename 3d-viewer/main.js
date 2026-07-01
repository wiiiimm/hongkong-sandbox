// Hong Kong / Lantau layered 3D terrain viewer.
// Base terrain = Claude's smooth external DEM meshes; skin = draped vector layers.
// Best-of-both: shaded / elevation / matte / bare-wireframe / raster surface styles,
// per-layer vector toggles, and a vertical-exaggeration slider that drives BOTH the
// terrain and the draped skin so contours stay welded to the ridges.
import * as THREE from './vendor/three.module.js';
import { OrbitControls } from './vendor/OrbitControls.js';

// ---- source registry (extend with whole-HK + SRTM later) -------------------
const SOURCES = {
  'lantau-hk5m': {
    label: 'Lantau · LandsD 5 m DTM',
    mesh:    'data/lantau-hk5m.json',
    georef:  { file: 'data/lantau-georefs.json', key: 'hk5m' },
    texbb:   'data/lantau-texbb.json',
    overlay: 'data/lantau-b50k-vectors.json',   // re-extracted from B50K GML, grid-aligned
    landcover: 'data/lantau-b50k-landcover.json',
    ve: 2.8,
  },
  'lantau-srtm30': {
    label: 'Lantau · AWS Terrarium ~30 m',
    mesh:    'data/lantau-srtm30.json',
    georef:  { file: 'data/lantau-georefs.json', key: 'srtm30' },
    texbb:   'data/lantau-texbb.json',           // shared: B50K texture geographic bounds
    overlay: 'data/lantau-b50k-vectors.json',    // shared: vectors are in absolute E/N via texbb
    landcover: 'data/lantau-b50k-landcover.json',
    ve: 2.6,
  },
  'hk-landsd-5m': {
    label: 'Hong Kong · LandsD 5 m DTM',
    mesh:    'data/hk-dtm5m.json',
    georef:  { file: 'data/hk-georef.json' },     // flat georef (no key)
    texbb:   'data/hk-texbb.json',
    overlay: 'data/hk-b50k-vectors.json',
    landcover: 'data/hk-b50k-landcover.json',
    ve: 2.8,
  },
  'hk-srtm': {
    label: 'Hong Kong · AWS Terrarium ~30 m',
    mesh:    'data/hk-srtm.json',
    georef:  { file: 'data/hk-georef.json' },
    texbb:   'data/hk-texbb.json',
    overlay: 'data/hk-b50k-vectors.json',
    landcover: 'data/hk-b50k-landcover.json',
    ve: 2.2,
  },
};

// vector layer styling (colour + default visibility)
const LAYER_STYLE = {
  contour:  { colour: 0x7a5a36, on: true,  label: 'Contours' },
  road:     { colour: 0x5b5f68, on: true,  label: 'Roads' },
  trail:    { colour: 0xb0402c, on: true,  label: 'Trails' },
  hydro:    { colour: 0x3f6f82, on: true,  label: 'Hydro' },
  coast:    { colour: 0x2f6090, on: true,  label: 'Coast' },
  boundary: { colour: 0x9c6d8a, on: false, label: 'Boundaries' },
  cliff:    { colour: 0x6d5a4a, on: false, label: 'Cliffs' },
};

const BG = { dark: 0x0e1116, paper: 0xf4f1e9 };
const LINE_ON_PAPER = 0x2f5b43;   // wireframe colour on paper bg (the "geeky" look)
const LINE_ON_DARK  = 0x6fe0c0;

// ---- i18n (en-hk / zh-hk) --------------------------------------------------
const LOCALES = ['en-hk', 'zh-hk'];
const DEFAULT_LOCALE = 'en-hk';
const I18N = {
  'en-hk': {
    'lbl.source': 'Source', 'src.hk5m': 'Hong Kong · LandsD 5 m', 'src.hksrtm': 'Hong Kong · AWS Terrarium ~30 m',
    'src.lan5m': 'Lantau · LandsD 5 m', 'src.lansrtm': 'Lantau · AWS Terrarium ~30 m',
    'lbl.surface': 'Surface', 'surf.none': 'None (no fill)', 'surf.shaded': 'Shaded relief', 'surf.tint': 'Elevation tint (flat)',
    'surf.matte': 'Matte', 'surf.solid': 'Solid colour', 'surf.topo': 'Topographic (B50K)', 'surf.osm': 'Street map (OSM)', 'surf.sat': 'Satellite (Esri)',
    'lbl.fill': 'Fill colour', 'lbl.maprotate': 'Map rotate', 'lbl.background': 'Background', 'bg.dark': 'Dark', 'bg.paper': 'Paper', 'lbl.vertical': 'Vertical ×',
    'grp.mesh': 'Mesh', 'lbl.showmesh': 'Show mesh lines', 'lbl.density': 'Density', 'lbl.colour': 'Colour', 'btn.auto': 'auto',
    'grp.overlays': 'Overlays · stack on top', 'ov.water': 'Water', 'ov.labels': 'Labels', 'ov.stations': 'Stations (live)',
    'lyr.contour': 'Contours', 'lyr.road': 'Roads', 'lyr.trail': 'Trails', 'lyr.hydro': 'Hydro', 'lyr.coast': 'Coast', 'lyr.boundary': 'Boundaries', 'lyr.cliff': 'Cliffs',
    'grp.spin': 'Auto‑spin (horizontal)', 'lbl.direction': 'Direction', 'spin.off': 'Off', 'spin.cw': '⟳ Clockwise', 'spin.ccw': '⟲ Counter‑cw', 'lbl.speed': 'Speed',
    'grp.weather': 'Weather', 'wx.rain': 'Rain', 'wx.clouds': 'Clouds', 'wx.fog': 'Fog', 'wx.thunder': 'Thunder', 'wx.waves': 'Waves',
    'lbl.thunderrate': 'Thunder rate', 'lbl.tide': 'Tide', 'lbl.storm': 'Storm signal', 'storm.0': 'None', 'storm.1': 'T1 · Standby', 'storm.3': 'T3 · Strong wind',
    'storm.8': 'T8 · Gale / Storm', 'storm.9': 'T9 · Incr. gale', 'storm.10': 'T10 · Hurricane', 'lbl.wind': 'Wind', 'lbl.windfrom': 'Wind from',
    'btn.reset': 'Reset', 'btn.south': 'South', 'btn.top': 'Top‑down', 'btn.copylink': 'Copy link',
    'navhelp': '<b>Navigate</b><br>Mouse — drag rotate · scroll zoom · right‑drag pan<br>Touch — one finger rotate · pinch zoom · two‑finger pan<br>Reset — recenter the view',
    'live.sync': '⛅ Sync live weather', 'live.on': '⛅ Live weather · ON', 'lock.live': '◈ controls locked to live data', 'lock.storm': '◈ effects set by storm signal',
    'note.mesh': 'mesh', 'note.verts': 'verts', 'note.peak': 'peak', 'note.m': 'm', 'note.loading': 'Loading', 'note.loadfail': 'Load failed',
    'load.osm': 'street map', 'load.sat': 'satellite imagery', 'load.mapfail': 'Map load failed', 'dens.full': 'full',
    'sig.1': 'Standby Signal No.1', 'sig.3': 'Strong Wind Signal No.3', 'sig.8': 'Gale or Storm Signal No.8',
    'sig.9': 'Increasing Gale or Storm Signal No.9', 'sig.10': 'Hurricane Signal No.10', 'badge.pre': '⚠ TYPHOON SIGNAL No.', 'badge.post': '',
    'tip.humidity': 'humidity', 'tip.wind': 'wind', 'tip.gust': 'gust', 'tide.word': 'tide', 'tide.rising': '↑ rising', 'tide.falling': '↓ falling', 'tide.slack': '→ slack',
    'tide.24h': '24 h tide', 'st.QUB': 'Quarry Bay', 'st.CCH': 'Cheung Chau', 'wx.unavail': 'live weather unavailable', 'wx.live': 'Live',
  },
  'zh-hk': {
    'lbl.source': '資料來源', 'src.hk5m': '香港 · 地政總署 5 米', 'src.hksrtm': '香港 · AWS Terrarium ~30 米',
    'src.lan5m': '大嶼山 · 地政總署 5 米', 'src.lansrtm': '大嶼山 · AWS Terrarium ~30 米',
    'lbl.surface': '表面', 'surf.none': '無填色', 'surf.shaded': '陰影地貌', 'surf.tint': '高程著色（平面）',
    'surf.matte': '霧面', 'surf.solid': '純色', 'surf.topo': '地形圖 (B50K)', 'surf.osm': '街道圖 (OSM)', 'surf.sat': '衛星影像 (Esri)',
    'lbl.fill': '填色', 'lbl.maprotate': '地圖旋轉', 'lbl.background': '背景', 'bg.dark': '深色', 'bg.paper': '紙本', 'lbl.vertical': '垂直誇張 ×',
    'grp.mesh': '網格', 'lbl.showmesh': '顯示網格線', 'lbl.density': '密度', 'lbl.colour': '顏色', 'btn.auto': '自動',
    'grp.overlays': '疊加圖層', 'ov.water': '海水', 'ov.labels': '地名', 'ov.stations': '氣象站（即時）',
    'lyr.contour': '等高線', 'lyr.road': '道路', 'lyr.trail': '山徑', 'lyr.hydro': '水系', 'lyr.coast': '海岸線', 'lyr.boundary': '界線', 'lyr.cliff': '懸崖',
    'grp.spin': '自動旋轉（水平）', 'lbl.direction': '方向', 'spin.off': '關閉', 'spin.cw': '⟳ 順時針', 'spin.ccw': '⟲ 逆時針', 'lbl.speed': '速度',
    'grp.weather': '天氣', 'wx.rain': '雨', 'wx.clouds': '雲', 'wx.fog': '霧', 'wx.thunder': '雷暴', 'wx.waves': '波浪',
    'lbl.thunderrate': '雷暴頻率', 'lbl.tide': '潮汐', 'lbl.storm': '風暴信號', 'storm.0': '無', 'storm.1': '一號 · 戒備', 'storm.3': '三號 · 強風',
    'storm.8': '八號 · 烈風/暴風', 'storm.9': '九號 · 烈風增強', 'storm.10': '十號 · 颶風', 'lbl.wind': '風力', 'lbl.windfrom': '風向來自',
    'btn.reset': '重設', 'btn.south': '南面', 'btn.top': '俯視', 'btn.copylink': '複製連結',
    'navhelp': '<b>操作</b><br>滑鼠 — 拖曳旋轉 · 滾輪縮放 · 右鍵拖曳平移<br>觸控 — 單指旋轉 · 雙指縮放 · 雙指平移<br>重設 — 重新置中',
    'live.sync': '⛅ 同步即時天氣', 'live.on': '⛅ 即時天氣 · 開啟', 'lock.live': '◈ 已鎖定為即時數據', 'lock.storm': '◈ 效果由風暴信號設定',
    'note.mesh': '網格', 'note.verts': '頂點', 'note.peak': '最高', 'note.m': '米', 'note.loading': '載入中', 'note.loadfail': '載入失敗',
    'load.osm': '街道圖', 'load.sat': '衛星影像', 'load.mapfail': '地圖載入失敗', 'dens.full': '全部',
    'sig.1': '一號戒備信號', 'sig.3': '三號強風信號', 'sig.8': '八號烈風或暴風信號',
    'sig.9': '九號烈風或暴風增強信號', 'sig.10': '十號颶風信號', 'badge.pre': '⚠ 颱風信號 ', 'badge.post': ' 號',
    'tip.humidity': '濕度', 'tip.wind': '風', 'tip.gust': '陣風', 'tide.word': '潮汐', 'tide.rising': '↑ 上漲', 'tide.falling': '↓ 回落', 'tide.slack': '→ 平潮',
    'tide.24h': '24 小時潮汐', 'st.QUB': '鰂魚涌', 'st.CCH': '長洲', 'wx.unavail': '無法取得即時天氣', 'wx.live': '即時',
  },
};
let locale = DEFAULT_LOCALE;
const t = k => (I18N[locale] && I18N[locale][k] != null) ? I18N[locale][k] : (I18N[DEFAULT_LOCALE][k] != null ? I18N[DEFAULT_LOCALE][k] : k);
const isZh = () => locale === 'zh-hk';

// ---- three.js boilerplate --------------------------------------------------
const app = document.getElementById('app');
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(38, 1, 10, 400000);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.maxPolarAngle = Math.PI * 0.495;

const hemi = new THREE.HemisphereLight(0xffffff, 0x2b3038, 1.4); scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffffff, 2.0); sun.position.set(-1, 2, 1.4); scene.add(sun);

// group everything so spin rotates terrain + skin + labels together
const world = new THREE.Group(); scene.add(world);

// ---- per-source state ------------------------------------------------------
let W, H, cell, elev, zmax, peaks = [];
let meshStep = 1, gridW = 0, gridH = 0, curG = null, curTexbb = null;   // mesh density state
let firstLoad = true;   // apply per-source default VE only on the very first load
let terrain, terrainBase, wireOverlay, sea, skin;      // objects
let skinBase = new Map();                               // layer -> Float32Array of base (unexaggerated) y
let labels = [];
let VE = 2.8, surfStyle = 'shaded', bgMode = 'dark';
let matShaded, matTint, matMatte, matSolid, matTopo, texTopo = null;
const tidalMats = [];   // materials with the intertidal "wet band" shader injected
let spinDir = 1, spinSpeed = 1;   // horizontal auto-spin (0 = off; 1 = clockwise)
let wireColor = '#2a4c33';        // mesh-line colour; 'auto' button sets null = auto by background
let solidColor = '#262626';       // fill colour for the "Solid colour" surface
let texRot = 0;                   // B50K raster rotation in degrees (manual alignment)
let baseUV = null, webTex = null, webUVAttr = null, webKind = null, matWeb = null;   // web-map drape

// ---- helpers (ported from the original viewer) -----------------------------
function hyps(e, zmax) {
  const t = Math.max(0, Math.min(1, e / zmax));
  const s = [[0,[46,92,58]],[0.18,[78,110,60]],[0.42,[150,140,96]],
             [0.68,[140,110,80]],[0.86,[170,150,128]],[1,[235,232,224]]];
  for (let i = 0; i < s.length - 1; i++) {
    const a = s[i], b = s[i + 1];
    if (t >= a[0] && t <= b[0]) {
      const u = (t - a[0]) / (b[0] - a[0]);
      return [a[1][0]+(b[1][0]-a[1][0])*u, a[1][1]+(b[1][1]-a[1][1])*u, a[1][2]+(b[1][2]-a[1][2])*u];
    }
  }
  return s[s.length - 1][1];
}
function sampleE(col, row) {
  col = Math.max(0, Math.min(W - 1.001, col));
  row = Math.max(0, Math.min(H - 1.001, row));
  const c0 = Math.floor(col), r0 = Math.floor(row), fc = col - c0, fr = row - r0;
  const a = elev[r0*W+c0], b = elev[r0*W+c0+1], c = elev[(r0+1)*W+c0], d = elev[(r0+1)*W+c0+1];
  return (a*(1-fc)+b*fc)*(1-fr) + (c*(1-fc)+d*fc)*fr;
}
const skinOffset = () => cell * 0.6; // lift lines just above the surface, scaled to grid

// ---- load a source ---------------------------------------------------------
async function loadSource(id) {
  const s = SOURCES[id];
  document.getElementById('note').textContent = t('note.loading') + '…';
  // dev: propagate the page's ?v to data fetches so edits bust cache; no-op in prod
  const ver = new URLSearchParams(location.search).get('v');
  const q = ver ? ('?v=' + ver) : '';
  const fj = u => fetch(u + q, { cache: 'no-cache' }).then(r => r.json());   // revalidate (304 if unchanged) so stale DEMs never stick
  const [mesh, georefAll, texbbWrap, overlay, landcover] = await Promise.all([
    fj(s.mesh), fj(s.georef.file), fj(s.texbb), fj(s.overlay), fj(s.landcover),
  ]);
  const g = s.georef.key ? georefAll[s.georef.key] : georefAll;   // keyed (lantau) or flat (hk)
  const texbb = texbbWrap.texbb;

  W = mesh.w; H = mesh.h; cell = mesh.cell; elev = mesh.elev; zmax = mesh.zmax;
  peaks = mesh.peaks || [];
  curG = g; curTexbb = texbb;
  if (firstLoad) VE = s.ve;   // apply source default only on first load; otherwise keep user's setting
  document.getElementById('ve').value = VE;
  document.getElementById('vev').textContent = VE.toFixed(1);

  buildTerrain();
  buildSkin(overlay, g, texbb);
  buildSea();
  buildWeather();
  updateWindVisuals();     // renderSky + fog + rain/cloud look for the current wind
  buildLabels();
  if (texTopo) texTopo.dispose();
  texTopo = buildBaseTexture(landcover);   // clean B50K base map (fills only), aligned by construction
  matTopo.map = texTopo; matTopo.needsUpdate = true;
  applyTexRot();

  applyStyle(surfStyle);
  applyVE();
  frameCamera();
  updateNote();
  firstLoad = false;
}

function updateNote() {
  document.getElementById('note').textContent =
    `${gridW}×${gridH} ${t('note.mesh')} · ${(gridW*gridH/1e3).toFixed(0)}k ${t('note.verts')} · ${t('note.peak')} ${Math.round(zmax)} ${t('note.m')}`;
}

// rebuild terrain at the current density, preserving style/VE/camera
function rebuildTerrain() {
  buildTerrain();
  if (texTopo) matTopo.map = texTopo;   // re-attach texture to freshly-made material
  applyStyle(surfStyle);
  applyVE();
  updateNote();
}

// Subsampled sample indices along an axis (always includes the last row/col).
function axisSamples(n, step) {
  const s = []; for (let i = 0; i < n; i += step) s.push(i);
  if (s[s.length - 1] !== n - 1) s.push(n - 1);
  return s;
}

// Intertidal "wet band": tint terrain within uBand (world units) above the water
// line. A fixed VERTICAL band renders WIDE on gentle natural coasts/beaches and
// vanishingly THIN on steep seawalls/cliffs — so tides read only where they'd
// really show. Purely geometric; no shoreline classification needed.
function attachTidalBand(mat) {
  mat.onBeforeCompile = (sh) => {
    sh.uniforms.uWaterY = { value: -1e9 };
    sh.uniforms.uBand = { value: 12.0 };
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>\nvarying float vTideY;')
      .replace('#include <begin_vertex>', '#include <begin_vertex>\nvTideY = position.y;');
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', '#include <common>\nvarying float vTideY;\nuniform float uWaterY;\nuniform float uBand;')
      .replace('#include <dithering_fragment>',
        '#include <dithering_fragment>\n{ float d = vTideY - uWaterY; float wet = step(0.0, d) * (1.0 - smoothstep(0.0, uBand, d)); gl_FragColor.rgb = mix(gl_FragColor.rgb, vec3(0.29,0.33,0.31), wet*0.5); }');
    mat.userData.sh = sh;
  };
  mat.needsUpdate = true;
  tidalMats.push(mat);
}

function buildTerrain() {
  if (terrain) { world.remove(terrain); terrain.geometry.dispose(); }
  const rows = axisSamples(H, meshStep), cols = axisSamples(W, meshStep);
  const gW = cols.length, gH = rows.length;
  gridW = gW; gridH = gH;
  const g = curG, tb = curTexbb;
  const geo = new THREE.BufferGeometry();
  const pos = new Float32Array(gW*gH*3), col = new Float32Array(gW*gH*3), uv = new Float32Array(gW*gH*2);
  for (let j = 0; j < gH; j++) for (let i = 0; i < gW; i++) {
    const r = rows[j], c = cols[i], k = j*gW+i, e = elev[r*W+c];
    pos[k*3] = (c-W/2)*cell; pos[k*3+1] = e; pos[k*3+2] = (r-H/2)*cell;
    const cc = hyps(e, zmax); col[k*3] = cc[0]/255; col[k*3+1] = cc[1]/255; col[k*3+2] = cc[2]/255;
    const E = g.aE*c + g.bE, N = g.aN*r + g.bN;
    // the B50K raster is authored rotated 180° (stored upside-down); this UV un-rotates it
    uv[k*2] = (E-tb.E0)/(tb.E1-tb.E0); uv[k*2+1] = (N-tb.N0)/(tb.N1-tb.N0);
  }
  const idx = [];
  for (let j = 0; j < gH-1; j++) for (let i = 0; i < gW-1; i++) {
    const a = j*gW+i, b = a+1, d = a+gW, e = d+1; idx.push(a,d,b, b,d,e);
  }
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  geo.setIndex(idx);
  terrainBase = pos.slice();  // unexaggerated heights
  baseUV = uv; webKind = null;   // keep base UVs for restore; force web-map rebuild after any remesh

  matShaded = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.95, metalness: 0 });
  matTint   = new THREE.MeshBasicMaterial({ vertexColors: true });                 // flat hypsometric
  matMatte  = new THREE.MeshStandardMaterial({ color: 0x8a8f86, roughness: 1, metalness: 0 });
  matSolid  = new THREE.MeshBasicMaterial({ color: solidColor });                  // flat solid fill
  matTopo   = new THREE.MeshBasicMaterial({});   // unlit: show the map flat, no hillshade darkening
  tidalMats.length = 0;
  [matShaded, matTint, matMatte].forEach(attachTidalBand);   // wet intertidal band on the terrain surfaces

  terrain = new THREE.Mesh(geo, matShaded);
  world.add(terrain);

  // wireframe overlay (mesh lines on top of any fill) — shares live geometry
  if (wireOverlay) { world.remove(wireOverlay); wireOverlay.material.dispose(); }
  wireOverlay = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: LINE_ON_DARK, wireframe: true, transparent: true, opacity: 0.14 }));
  wireOverlay.visible = false;
  world.add(wireOverlay);
}

// build one merged LineSegments per vector layer, draped on the terrain
function buildSkin(overlay, g, texbb) {
  if (skin) { world.remove(skin); skin.traverse(o => o.geometry?.dispose()); }
  skin = new THREE.Group(); skinBase.clear();
  const layersDiv = document.getElementById('layers');
  // preserve the user's per-layer toggle choices across a source switch
  const prev = {};
  for (const inp of layersDiv.querySelectorAll('input')) prev[inp.id.replace('lyr_', '')] = inp.checked;
  layersDiv.innerHTML = '';

  for (const [name, style] of Object.entries(LAYER_STYLE)) {
    const lines = overlay[name]; if (!lines || !lines.length) continue;
    const pos = [], baseY = [];
    for (const line of lines) {
      for (let k = 0; k < line.length - 1; k++) {         // emit segment pairs (connected polyline)
        for (const p of [line[k], line[k+1]]) {
          const E = texbb.E0 + p[0]*(texbb.E1 - texbb.E0);
          const N = texbb.N1 - p[1]*(texbb.N1 - texbb.N0);
          const cc = (E - g.bE)/g.aE, rr = (N - g.bN)/g.aN;
          const y = sampleE(cc, rr);
          pos.push((cc-W/2)*cell, y, (rr-H/2)*cell);
          baseY.push(y);
        }
      }
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    const on = (name in prev) ? prev[name] : style.on;   // keep prior choice, else default
    const seg = new THREE.LineSegments(geo, new THREE.LineBasicMaterial({ color: style.colour }));
    seg.name = name;
    seg.visible = on;
    skin.add(seg);
    skinBase.set(name, new Float32Array(baseY));

    // toggle UI
    const id = 'lyr_' + name;
    const lab = document.createElement('label'); lab.className = 'chk';
    lab.innerHTML = `<input type="checkbox" id="${id}" ${on?'checked':''}/> <span data-i18n="lyr.${name}">${I18N[locale]['lyr.'+name] || style.label}</span>`;
    layersDiv.appendChild(lab);
    lab.querySelector('input').addEventListener('change', e => { seg.visible = e.target.checked; });
  }
  world.add(skin);
}

function buildSea() {
  if (sea) { world.remove(sea); sea.geometry.dispose(); sea.material.dispose(); }
  const geo = new THREE.PlaneGeometry(cell*W*1.8, cell*H*1.8);
  sea = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: 0x2b5d78, transparent: true, opacity: 0.55, roughness: 0.4, depthWrite: false }));
  sea.rotation.x = -Math.PI/2; sea.position.y = 0.5;
  world.add(sea);
}

// ---- weather effects: rain / clouds / fog / lightning / waves --------------
let rainPts = null, cloudGrp = null, wavePhase = 0, flash = 0;
const SEA_Y = 0.5;
const weather = { fog: false, rain: false, clouds: false, lightning: false, waves: false };
let tideManual = 0.5;    // slider 0..1 — used when not in live mode
let tideLevel  = 0.5;    // effective water level 0..1 (drives the sea height)
let tideSeries = null;   // live prediction: { vals[72] m, nowHour, min, max, cur, stationName } or null

// ---- wind + tropical-cyclone storm system ----------------------------------
let stormLevel = 0;      // 0 none, else HK signal 1 / 3 / 8 / 9 / 10
let windStrength = 0;    // 0..1 wind intensity (storm presets it; slider overrides)
let thunderRate = 0.4;   // 0..1 lightning strike frequency (storm/live preset it)
const flashfx = document.getElementById('flashfx');   // full-screen lightning flash
let baseHemi = 1.4, baseSun = 2.0;   // light levels before the lightning flash is added
const windVec = { x: 0, z: 1 };      // unit heading the wind blows TOWARD (screen space)
const WIND_VEC = {   // compass the wind blows FROM -> push vector (toward the opposite)
  N:[0,1], NE:[-0.707,0.707], E:[-1,0], SE:[-0.707,-0.707],
  S:[0,-1], SW:[0.707,-0.707], W:[1,0], NW:[0.707,0.707],
};
const STORM_W = { 0:0, 1:0.2, 3:0.45, 8:0.72, 9:0.86, 10:1 };   // signal -> wind strength
const SIGNAL_NAME = {
  1:'Standby Signal No.1', 3:'Strong Wind Signal No.3', 8:'Gale or Storm Signal No.8',
  9:'Increasing Gale or Storm Signal No.9', 10:'Hurricane Signal No.10',
};
const setWindDir = dir => { const v = WIND_VEC[dir] || WIND_VEC.N; windVec.x = v[0]; windVec.z = v[1]; };

const CLOUD_TEX = (() => {
  const c = document.createElement('canvas'); c.width = c.height = 128;
  const x = c.getContext('2d'), g = x.createRadialGradient(64, 64, 6, 64, 64, 64);
  g.addColorStop(0, 'rgba(255,255,255,0.85)'); g.addColorStop(0.55, 'rgba(238,242,247,0.35)'); g.addColorStop(1, 'rgba(255,255,255,0)');
  x.fillStyle = g; x.fillRect(0, 0, 128, 128);
  return new THREE.CanvasTexture(c);
})();

// (re)build rain + clouds sized to the current source; visibility follows toggles
function buildWeather() {
  const b = bounds(), hx = b.halfX, hz = b.halfZ, top = b.span * 0.45;
  if (rainPts) { world.remove(rainPts); rainPts.geometry.dispose(); rainPts.material.dispose(); }
  const N = 7000, pos = new Float32Array(N * 3);
  for (let i = 0; i < N; i++) {
    pos[i*3] = (Math.random()*2 - 1) * hx;
    pos[i*3+1] = Math.random() * top;
    pos[i*3+2] = (Math.random()*2 - 1) * hz;
  }
  const rg = new THREE.BufferGeometry();
  rg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  rainPts = new THREE.Points(rg, new THREE.PointsMaterial({ color: 0xbcd2e2, size: b.span*0.0016, transparent: true, opacity: 0.55, depthWrite: false }));
  rainPts.userData.top = top; rainPts.visible = weather.rain;
  world.add(rainPts);

  if (cloudGrp) { world.remove(cloudGrp); cloudGrp.traverse(o => o.material && o.material.dispose()); }
  cloudGrp = new THREE.Group();
  const H = b.span * 0.34, n = 22, size = b.span * 0.34;
  for (let i = 0; i < n; i++) {
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: CLOUD_TEX, color: 0xe2e8ef, transparent: true, opacity: 0.5, depthWrite: false }));
    s.position.set((Math.random()*2-1)*hx, H + Math.random()*b.span*0.12, (Math.random()*2-1)*hz);
    const w = size * (0.6 + Math.random());
    s.scale.set(w, w*0.55, 1);
    cloudGrp.add(s);
  }
  cloudGrp.visible = weather.clouds;
  world.add(cloudGrp);
}

// clear colour + light levels, darkened toward a storm sky as the wind rises
function renderSky() {
  const onPaper = bgMode === 'paper';
  const k = stormLevel > 0 ? Math.min(0.6, 0.15 + windStrength * 0.55) : 0;
  const col = new THREE.Color(BG[bgMode]).lerp(new THREE.Color(0x1a2028), k);
  renderer.setClearColor(col, 1);
  const dim = 1 - (stormLevel > 0 ? windStrength * 0.4 : 0);
  baseHemi = (onPaper ? 1.9 : 1.4) * dim;
  baseSun  = (onPaper ? 2.4 : 2.0) * dim;
  hemi.intensity = baseHemi + flash * 5;
  sun.intensity  = baseSun;
}

function setFog() {
  if (!weather.fog) { scene.fog = null; return; }
  const b = bounds(), w = stormLevel > 0 ? windStrength : 0;
  const near = Math.max(b.span * 0.12, b.span * (0.35 - 0.08 * w));   // storm fog thickens (but stays past the camera)
  const far  = b.span * (1.5 - 0.35 * w);
  scene.fog = new THREE.Fog(renderer.getClearColor(new THREE.Color()).getHex(), near, far);
}

function animateWeather() {
  const b = bounds(), w = windStrength, hx = b.halfX, hz = b.halfZ;
  if (rainPts && rainPts.visible) {
    const p = rainPts.geometry.attributes.position.array, top = rainPts.userData.top;
    const fall = b.span * 0.012 * (1 + w * 1.6);          // driving rain falls faster in wind
    const dx = windVec.x * b.span * 0.02 * w, dz = windVec.z * b.span * 0.02 * w;   // blown sideways
    for (let i = 0; i < p.length; i += 3) {
      p[i] += dx; p[i+1] -= fall; p[i+2] += dz;
      if (p[i+1] < 0) p[i+1] = top;
      if (p[i]   >  hx) p[i]   -= 2*hx; else if (p[i]   < -hx) p[i]   += 2*hx;   // wrap horizontally
      if (p[i+2] >  hz) p[i+2] -= 2*hz; else if (p[i+2] < -hz) p[i+2] += 2*hz;
    }
    rainPts.geometry.attributes.position.needsUpdate = true;
  }
  if (cloudGrp && cloudGrp.visible) {
    const spd = b.span * 0.0006 * (1 + w * 7);            // clouds race with the wind
    const cx = windVec.x * spd, cz = windVec.z * spd, lx = hx * 1.3, lz = hz * 1.3;
    for (const s of cloudGrp.children) {
      s.position.x += cx; s.position.z += cz;
      if (s.position.x >  lx) s.position.x = -lx; else if (s.position.x < -lx) s.position.x = lx;
      if (s.position.z >  lz) s.position.z = -lz; else if (s.position.z < -lz) s.position.z = lz;
    }
  }
  // tide = slow water level; storm adds a surge on top; waves = ripple that gets
  // choppier (but still upward-only, so it never drains) as the wind picks up.
  if (sea) {
    // sea rests AT the coastline (SEA_Y); tide is a small band around mean (50% = mean),
    // sized to real HK tides (~±3 m) so it never floods the city. Storm adds a modest
    // surge on top, and waves a small upward chop.
    const tide   = (tideLevel - 0.5) * b.span * 0.00016;                       // ~±5 units ≈ ±3 m
    const surge  = stormLevel >= 8 ? (stormLevel >= 10 ? 1 : stormLevel >= 9 ? 0.65 : 0.4) * b.span * 0.00022 : 0;
    const amp    = b.span * (0.00004 + w * 0.0001);
    const ripple = weather.waves ? (Math.sin(wavePhase += 0.03 * (1 + w * 3)) * 0.5 + 0.5) * amp : 0;
    sea.position.y = SEA_Y + tide + surge + ripple;
  }
  // drive the intertidal wet-band shader from the live water level (~4.5 m band)
  const wy = (sea && sea.visible) ? sea.position.y : -1e9;
  for (const m of tidalMats) { const sh = m.userData.sh; if (sh) { sh.uniforms.uWaterY.value = wy; sh.uniforms.uBand.value = 4.5 * VE; } }
  if (weather.lightning) {
    if (flash > 0) { flash -= 0.08; hemi.intensity = baseHemi + flash * 5; }
    // quadratic, zero-floored: ~0 at low rate, intense near 100% (no always-on base term)
    else if (Math.random() < thunderRate * thunderRate * 0.1) flash = 1;
  }
  if (flashfx) flashfx.style.opacity = weather.lightning ? (flash * 0.6).toFixed(3) : 0;   // white screen flash
}

function buildLabels() {
  labels.forEach(l => l.div.remove()); labels = [];
  for (const pk of peaks) {
    const div = document.createElement('div'); div.className = 'lbl';
    // names are "English 中文" — split trailing CJK from the English part
    const name = pk.name || '';
    const m = name.match(/^(.*?)\s*([㐀-鿿][㐀-鿿\s]*)$/);
    const english = (m ? m[1] : name).trim();
    const chinese = m ? m[2].trim() : '';
    const top = chinese || english;                       // Chinese on top when present
    const sub = (chinese ? english + ' · ' : '') + Math.round(pk.elev) + ' m';
    div.innerHTML = `${top}<small>${sub}</small>`;
    document.body.appendChild(div);
    labels.push({ div, col: pk.col, row: pk.row });
  }
}

// ---- vertical exaggeration drives terrain AND skin -------------------------
function applyVE() {
  const p = terrain.geometry.attributes.position.array;
  const nVerts = terrainBase.length / 3;
  for (let i = 0; i < nVerts; i++) p[i*3+1] = terrainBase[i*3+1] * VE;
  terrain.geometry.attributes.position.needsUpdate = true;
  terrain.geometry.computeVertexNormals();

  const off = skinOffset();
  for (const seg of skin.children) {
    const base = skinBase.get(seg.name);
    const arr = seg.geometry.attributes.position.array;
    for (let i = 0; i < base.length; i++) arr[i*3+1] = base[i]*VE + off;
    seg.geometry.attributes.position.needsUpdate = true;
  }
}

// ---- surface style + background -------------------------------------------
// colour + opacity of the mesh-line overlay. When the mesh is the *only* thing
// on screen (style 'none') the lines go bold; when overlaid on a fill they stay faint.
function wireLook() {
  const onPaper = bgMode === 'paper';
  const auto = onPaper ? LINE_ON_PAPER : LINE_ON_DARK;
  wireOverlay.material.color.set(wireColor != null ? wireColor : auto);
  const primary = surfStyle === 'none';
  wireOverlay.material.opacity = primary ? (onPaper ? 0.9 : 0.8) : (onPaper ? 0.22 : 0.14);
}

// paint a clean B50K base map (land-cover + water fills, no linework) onto a
// canvas at the grid's geographic aspect -> CanvasTexture. Aligned by construction.
function buildBaseTexture(lc) {
  const tb = curTexbb;
  const aspect = (tb.E1 - tb.E0) / (tb.N1 - tb.N0);
  const W = 2048, H = Math.max(1, Math.round(W / aspect));
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const ctx = cv.getContext('2d');
  ctx.fillStyle = '#efe9dd'; ctx.fillRect(0, 0, W, H);   // land base
  const paint = (rings, color) => {
    if (!rings || !rings.length) return;
    ctx.fillStyle = color; ctx.beginPath();
    for (const ring of rings) {
      ctx.moveTo(ring[0][0]*W, ring[0][1]*H);
      for (let i = 1; i < ring.length; i++) ctx.lineTo(ring[i][0]*W, ring[i][1]*H);
      ctx.closePath();
    }
    ctx.fill('evenodd');
  };
  paint(lc.wood,   '#b7cca4');   // woodland
  paint(lc.veg,    '#cfdab3');   // cultivation / other vegetation
  paint(lc.barren, '#ddccae');   // sand / mud / barren
  paint(lc.water,  '#a7c4d6');   // reservoirs / water bodies
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = renderer.capabilities.getMaxAnisotropy();
  return tex;
}

// rotate the B50K raster around its centre (manual alignment aid)
function applyTexRot() {
  const el = document.getElementById('toporotv');
  if (el) el.textContent = texRot.toFixed(1) + '°';
  if (!texTopo) return;
  texTopo.center.set(0.5, 0.5);
  texTopo.rotation = texRot * Math.PI / 180;
  texTopo.needsUpdate = true;
}

// ---- web-map drape (OSM / satellite) --------------------------------------
// The terrain is in the HK1980 grid; web tiles are Web Mercator. We reproject
// the mesh UVs (not the imagery): each vertex E/N -> lon/lat (inverse HK1980 TM)
// -> Web Mercator, so a plain tile mosaic lands exactly on the terrain.
const HK = { a: 6378388.0, FE: 836694.05, FN: 819069.80, k0: 1.0 };
HK.f = 1 / 297; HK.e2 = HK.f * (2 - HK.f);
HK.lat0 = (22 + 18/60 + 43.68/3600) * Math.PI/180;
HK.lon0 = (114 + 10/60 + 42.80/3600) * Math.PI/180;
function meridianArc(lat) {
  const e2 = HK.e2, e4 = e2*e2, e6 = e2*e2*e2;
  return HK.a * ((1 - e2/4 - 3*e4/64 - 5*e6/256)*lat - (3*e2/8 + 3*e4/32 + 45*e6/1024)*Math.sin(2*lat)
    + (15*e4/256 + 45*e6/1024)*Math.sin(4*lat) - (35*e6/3072)*Math.sin(6*lat));
}
function enToLL(E, N) {                    // HK1980 grid -> { lon, lat } degrees
  const e2 = HK.e2, ep2 = e2/(1-e2);
  const M = meridianArc(HK.lat0) + (N - HK.FN)/HK.k0;
  const mu = M / (HK.a*(1 - e2/4 - 3*e2*e2/64 - 5*e2*e2*e2/256));
  const e1 = (1 - Math.sqrt(1-e2))/(1 + Math.sqrt(1-e2));
  const phi1 = mu + (3*e1/2 - 27*e1**3/32)*Math.sin(2*mu) + (21*e1*e1/16 - 55*e1**4/32)*Math.sin(4*mu)
    + (151*e1**3/96)*Math.sin(6*mu) + (1097*e1**4/512)*Math.sin(8*mu);
  const s = Math.sin(phi1), c = Math.cos(phi1), t = Math.tan(phi1);
  const C1 = ep2*c*c, T1 = t*t, N1 = HK.a/Math.sqrt(1 - e2*s*s), R1 = HK.a*(1-e2)/Math.pow(1 - e2*s*s, 1.5);
  const D = (E - HK.FE)/(N1*HK.k0);
  const lat = phi1 - (N1*t/R1)*(D*D/2 - (5 + 3*T1 + 10*C1 - 4*C1*C1 - 9*ep2)*D**4/24
    + (61 + 90*T1 + 298*C1 + 45*T1*T1 - 252*ep2 - 3*C1*C1)*D**6/720);
  const lon = HK.lon0 + (D - (1 + 2*T1 + C1)*D**3/6
    + (5 - 2*C1 + 28*T1 - 3*C1*C1 + 8*ep2 + 24*T1*T1)*D**5/120)/c;
  return { lon: lon*180/Math.PI, lat: lat*180/Math.PI };
}
const lonToMx = lon => (lon + 180)/360;
const latToMy = lat => { const r = lat*Math.PI/180; return (1 - Math.log(Math.tan(r) + 1/Math.cos(r))/Math.PI)/2; };
// constant Web-Mercator shift for the WGS84↔HK1980 datum difference (~270 m), from
// manual alignment on the Esri satellite skin (UV offset 0.0040, -0.0030 on the HK mosaic)
const DATUM_MX = 7.3242e-6, DATUM_MY = 4.3945e-6;
const TILE_SRC = {
  osm: { url: (z,x,y) => `https://tile.openstreetmap.org/${z}/${x}/${y}.png`, attr: '© OpenStreetMap contributors' },
  sat: { url: (z,x,y) => `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/${z}/${y}/${x}`, attr: 'Imagery © Esri, Maxar, Earthstar Geographics' },
};

async function buildWebMap(kind) {
  const g = curG, tb = curTexbb;
  const corners = [[tb.E0,tb.N0],[tb.E1,tb.N0],[tb.E0,tb.N1],[tb.E1,tb.N1]].map(([E,N]) => {
    const ll = enToLL(E, N); return { mx: lonToMx(ll.lon), my: latToMy(ll.lat) };
  });
  const mx0 = Math.min(...corners.map(c=>c.mx)), mx1 = Math.max(...corners.map(c=>c.mx));
  const my0 = Math.min(...corners.map(c=>c.my)), my1 = Math.max(...corners.map(c=>c.my));
  let z = 16; while (z > 8 && (mx1-mx0)*Math.pow(2,z)*256 > 4096) z--;   // ~4k-px mosaic
  const n = Math.pow(2, z);
  const tx0 = Math.floor(mx0*n), tx1 = Math.floor(mx1*n), ty0 = Math.floor(my0*n), ty1 = Math.floor(my1*n);
  const cv = document.createElement('canvas'); cv.width = (tx1-tx0+1)*256; cv.height = (ty1-ty0+1)*256;
  const ctx = cv.getContext('2d'); ctx.fillStyle = '#8aa9c4'; ctx.fillRect(0, 0, cv.width, cv.height);
  const src = TILE_SRC[kind], jobs = [];
  for (let tx = tx0; tx <= tx1; tx++) for (let ty = ty0; ty <= ty1; ty++) {
    jobs.push(new Promise(res => {
      const img = new Image(); img.crossOrigin = 'anonymous';
      img.onload = () => { try { ctx.drawImage(img, (tx-tx0)*256, (ty-ty0)*256); } catch (_) {} res(); };
      img.onerror = () => res();
      img.src = src.url(z, tx, ty);
    }));
  }
  await Promise.all(jobs);
  const cmx0 = tx0/n, cmx1 = (tx1+1)/n, cmy0 = ty0/n, cmy1 = (ty1+1)/n;
  const pos = terrain.geometry.attributes.position.array, nV = pos.length/3, uv = new Float32Array(nV*2);
  for (let i = 0; i < nV; i++) {
    const c = pos[i*3]/cell + W/2, r = pos[i*3+2]/cell + H/2;
    const ll = enToLL(g.aE*c + g.bE, g.aN*r + g.bN);
    uv[i*2]   = (lonToMx(ll.lon) + DATUM_MX - cmx0)/(cmx1 - cmx0);   // + baked datum correction
    uv[i*2+1] = 1 - (latToMy(ll.lat) + DATUM_MY - cmy0)/(cmy1 - cmy0);
  }
  webUVAttr = new THREE.BufferAttribute(uv, 2);
  if (webTex) webTex.dispose();
  webTex = new THREE.CanvasTexture(cv);
  webTex.colorSpace = THREE.SRGBColorSpace;
  webTex.anisotropy = renderer.capabilities.getMaxAnisotropy();
  if (!matWeb) matWeb = new THREE.MeshBasicMaterial();
  matWeb.map = webTex; matWeb.needsUpdate = true;
  webKind = kind;
}
function applyWebSurface() {
  terrain.visible = true;
  terrain.geometry.setAttribute('uv', webUVAttr);
  terrain.material = matWeb;
  const a = document.getElementById('mapattr'); a.textContent = TILE_SRC[webKind].attr;
}

function applyStyle(style) {
  surfStyle = style;
  const web = (style === 'osm' || style === 'sat');
  document.getElementById('solidrow').style.display = (style === 'solid') ? '' : 'none';
  document.getElementById('toporow').style.display = (style === 'topo') ? '' : 'none';
  document.getElementById('mapattr').style.display = web ? 'block' : 'none';
  // mesh lines are an independent overlay in ALL styles (incl. none)
  wireOverlay.visible = document.getElementById('meshlines').checked;
  wireLook();
  if (web) {
    if (webKind === style && webTex) { applyWebSurface(); return; }
    document.getElementById('note').textContent = t('note.loading') + ' ' + (style === 'osm' ? t('load.osm') : t('load.sat')) + '…';
    buildWebMap(style).then(() => { if (surfStyle === style) applyWebSurface(); updateNote(); })
      .catch(err => { document.getElementById('note').textContent = t('load.mapfail'); console.error(err); });
    return;
  }
  // non-web styles: restore the base (B50K-aligned) UVs
  if (baseUV) terrain.geometry.setAttribute('uv', new THREE.BufferAttribute(baseUV, 2));
  const mats = { shaded: matShaded, tint: matTint, matte: matMatte, solid: matSolid, topo: matTopo };
  terrain.visible = (style !== 'none');   // 'none' = no filled surface
  if (terrain.visible) terrain.material = mats[style] || matShaded;
}
function applyBg(mode) {
  bgMode = mode;
  renderSky();
  if (wireOverlay) wireLook();
  setFog();
}

// storm signal badge + wind visuals (rain density, cloud tone, sky) --------
function updateStormBadge() {
  const el = document.getElementById('stormbadge');
  if (!stormLevel) { el.style.display = 'none'; return; }
  const quad = stormLevel === 8 ? document.getElementById('winddir').value : '';
  el.innerHTML = `${t('badge.pre')}${stormLevel}${t('badge.post')}${quad ? ' · ' + quad : ''}<small>${t('sig.' + stormLevel)}</small>`;
  const colours = { 1:'rgba(176,140,26,.92)', 3:'rgba(200,128,20,.93)', 8:'rgba(212,88,20,.94)', 9:'rgba(198,42,30,.95)', 10:'rgba(176,18,28,.97)' };
  el.style.background = colours[stormLevel] || 'rgba(200,60,30,.9)';
  el.classList.toggle('sev', stormLevel >= 9);
  el.style.display = 'block';
}
// lock the controls that are driven for you: live mode owns everything; a storm
// signal owns the weather effects + wind strength (but you can still steer "wind from").
function applyControlLocks() {
  const g = id => document.getElementById(id);
  const storm = stormLevel > 0;
  ['rain', 'clouds', 'fog', 'lightning', 'waves', 'wind', 'thunderrate'].forEach(id => g(id).disabled = liveMode || storm);
  g('winddir').disabled = liveMode;      // direction stays adjustable under a storm
  g('tide').disabled    = liveMode;
  g('storm').disabled   = liveMode;
  const lock = g('wxlock');
  if (liveMode)     { lock.textContent = t('lock.live');  lock.style.display = 'block'; }
  else if (storm)   { lock.textContent = t('lock.storm'); lock.style.display = 'block'; }
  else              { lock.style.display = 'none'; }
}
function updateWindVisuals() {
  const b = bounds(), w = windStrength;
  if (rainPts) { rainPts.material.opacity = 0.45 + 0.4 * w; rainPts.material.size = b.span * 0.0016 * (1 + w * 1.2); }
  if (cloudGrp) {
    const d = stormLevel > 0 ? 1 - w * 0.55 : 1;
    for (const s of cloudGrp.children) { s.material.color.setRGB(0.89 * d, 0.91 * d, 0.94 * d); s.material.opacity = 0.5 + w * 0.4; }
  }
  renderSky(); setFog();
}
// apply a storm signal: preset the wind + escalate the weather effects
function applyStorm(level) {
  stormLevel = level;
  windStrength = STORM_W[level] || 0;
  document.getElementById('wind').value = Math.round(windStrength * 100);
  document.getElementById('windv').textContent = Math.round(windStrength * 100) + '%';
  if (level > 0) {   // "None" just calms the wind and leaves your weather toggles alone
    const chk = (id, on) => { const e = document.getElementById(id); if (e.checked !== on) { e.checked = on; e.dispatchEvent(new Event('change', { bubbles: true })); } };
    chk('clouds', true);
    chk('rain', level >= 3);
    chk('waves', level >= 3);
    chk('fog', level >= 8);
    chk('lightning', level >= 8);
    if (level >= 8) setThunderRate(level >= 10 ? 0.9 : level >= 9 ? 0.65 : 0.45);   // storm drives strike rate
  }
  updateWindVisuals();
  updateStormBadge();
  applyControlLocks();
}
// HKO warning summary -> { level, dir? }
function stormFromWarn(ws) {
  const s = ws && ws.WTCSGNL;
  if (!s || !s.code || s.actionCode === 'CANCEL') return { level: 0 };
  const c = s.code;                                   // TC1 / TC3 / TC8NE.. / TC9 / TC10
  if (c === 'TC1') return { level: 1 };
  if (c === 'TC3') return { level: 3 };
  if (c === 'TC9') return { level: 9 };
  if (c === 'TC10') return { level: 10 };
  if (c.startsWith('TC8')) return { level: 8, dir: c.slice(3) };
  return { level: 0 };
}

// ---- camera framing + presets ---------------------------------------------
function bounds() {
  const halfX = W*cell/2, halfZ = H*cell/2, peakY = zmax*VE;
  return { halfX, halfZ, peakY, span: Math.max(W,H)*cell };
}
function frameCamera() {
  const b = bounds();
  controls.target.set(0, b.peakY*0.35, 0);
  // start 30° above the horizontal (sea-level) plane
  const elev = 30 * Math.PI / 180, dist = b.span * 1.1;
  camera.position.set(0, controls.target.y + dist*Math.sin(elev), dist*Math.cos(elev));
  controls.minDistance = b.span*0.04; controls.maxDistance = b.span*4;   // much more zoom range
  controls.update();
  updateClip();
}

// adaptive depth range: keeps precision (no sea z-fighting) at any zoom, and lets
// the near plane shrink when close so you can zoom right in
let clipNear = -1;
function updateClip() {
  const d = camera.position.distanceTo(controls.target);
  const near = Math.max(d * 0.02, 0.5);
  if (clipNear < 0 || Math.abs(near - clipNear) / clipNear > 0.04) {
    camera.near = near; camera.far = d * 3 + bounds().span * 2.5;
    camera.updateProjectionMatrix(); clipNear = near;
  }
}
function southView() { const b = bounds(); camera.position.set(0, b.peakY*1.2, b.span*1.1); controls.target.set(0, b.peakY*0.3, 0); controls.update(); }
function topView()   { const b = bounds(); camera.position.set(0, b.span*1.4, 0.01);       controls.target.set(0, 0, 0);           controls.update(); }

// ---- UI wiring -------------------------------------------------------------
document.getElementById('src').addEventListener('change', e => {
  loadSource(e.target.value).then(() => { if (liveMode) syncLiveTide(); }).catch(err => {
    document.getElementById('note').textContent = t('note.loadfail') + ': ' + err.message; console.error(err);
  });
});
document.getElementById('surf').addEventListener('change', e => applyStyle(e.target.value));
document.getElementById('bg').addEventListener('change', e => applyBg(e.target.value));
document.getElementById('ve').addEventListener('input', e => {
  VE = parseFloat(e.target.value); document.getElementById('vev').textContent = VE.toFixed(1); applyVE();
});
document.getElementById('meshlines').addEventListener('change', e => { wireOverlay.visible = e.target.checked; });
const meshdens = document.getElementById('meshdens'), meshdensv = document.getElementById('meshdensv');
const densStep = () => 13 - parseInt(meshdens.value, 10);   // slider right = finest (step 1)
meshdens.addEventListener('input', () => { const s = densStep(); meshdensv.textContent = s === 1 ? t('dens.full') : '÷' + s; });
meshdens.addEventListener('change', () => { meshStep = densStep(); rebuildTerrain(); });
const mlColor = document.getElementById('mlcolor'), mlHex = document.getElementById('mlhex');
function setWireColor(hex) {
  hex = hex.trim(); if (!/^#?[0-9a-fA-F]{6}$/.test(hex)) return;
  if (hex[0] !== '#') hex = '#' + hex;
  wireColor = hex; mlColor.value = hex; mlHex.value = hex; wireLook();
}
mlColor.addEventListener('input', e => setWireColor(e.target.value));
mlHex.addEventListener('change', e => setWireColor(e.target.value));
document.getElementById('mlauto').addEventListener('click', () => { wireColor = null; wireLook(); });
const solidColorEl = document.getElementById('solidcolor'), solidHexEl = document.getElementById('solidhex');
function setSolidColor(hex) {
  hex = hex.trim(); if (!/^#?[0-9a-fA-F]{6}$/.test(hex)) return;
  if (hex[0] !== '#') hex = '#' + hex;
  solidColor = hex; solidColorEl.value = hex; solidHexEl.value = hex;
  if (matSolid) matSolid.color.set(hex);
}
solidColorEl.addEventListener('input', e => setSolidColor(e.target.value));
solidHexEl.addEventListener('change', e => setSolidColor(e.target.value));
const rot = d => () => { texRot = Math.round((texRot + d) * 10) / 10; applyTexRot(); };
document.getElementById('toporotL').addEventListener('click', rot(-1));
document.getElementById('toporotLf').addEventListener('click', rot(-0.2));
document.getElementById('toporotRf').addEventListener('click', rot(0.2));
document.getElementById('toporotR').addEventListener('click', rot(1));
document.getElementById('toporot0').addEventListener('click', () => { texRot = 0; applyTexRot(); });
document.getElementById('water').addEventListener('change', e => { sea.visible = e.target.checked; });
document.getElementById('labels').addEventListener('change', e => { labels.forEach(l => l.div.style.display = e.target.checked ? '' : 'none'); });
document.getElementById('spindir').addEventListener('change', e => { spinDir = parseInt(e.target.value, 10); });
document.getElementById('spinspd').addEventListener('input', e => { spinSpeed = parseFloat(e.target.value); });
const panelEl = document.getElementById('panel');
document.getElementById('collapse-btn').addEventListener('click', () => panelEl.classList.add('collapsed'));
document.getElementById('expand-btn').addEventListener('click', () => panelEl.classList.remove('collapsed'));
document.getElementById('navhelp-btn').addEventListener('click', () => {
  const n = document.getElementById('navhelp'); n.style.display = n.style.display === 'none' ? '' : 'none';
});
document.getElementById('fog').addEventListener('change', e => { weather.fog = e.target.checked; setFog(); });
document.getElementById('rain').addEventListener('change', e => { weather.rain = e.target.checked; if (rainPts) rainPts.visible = weather.rain; });
document.getElementById('clouds').addEventListener('change', e => { weather.clouds = e.target.checked; if (cloudGrp) cloudGrp.visible = weather.clouds; });
document.getElementById('lightning').addEventListener('change', e => { weather.lightning = e.target.checked; if (!weather.lightning) { flash = 0; applyBg(bgMode); } });
document.getElementById('waves').addEventListener('change', e => { weather.waves = e.target.checked; });
document.getElementById('tide').addEventListener('input', e => {
  tideManual = parseInt(e.target.value, 10) / 100;
  if (!liveMode) tideLevel = tideManual;                 // live mode drives tideLevel from data instead
  document.getElementById('tidev').textContent = Math.round(tideManual * 100) + '%';
});
document.getElementById('storm').addEventListener('change', e => applyStorm(parseInt(e.target.value, 10)));
document.getElementById('wind').addEventListener('input', e => {
  windStrength = parseInt(e.target.value, 10) / 100;     // fine wind override (keeps the current signal)
  document.getElementById('windv').textContent = Math.round(windStrength * 100) + '%';
  updateWindVisuals();
});
function setThunderRate(v) {
  thunderRate = Math.max(0, Math.min(1, v));
  const el = document.getElementById('thunderrate'); if (el) el.value = Math.round(thunderRate * 100);
  const d = document.getElementById('thunderratev'); if (d) d.textContent = Math.round(thunderRate * 100) + '%';
}
document.getElementById('thunderrate').addEventListener('input', e => {
  thunderRate = parseInt(e.target.value, 10) / 100;
  document.getElementById('thunderratev').textContent = Math.round(thunderRate * 100) + '%';
});
document.getElementById('winddir').addEventListener('change', e => { setWindDir(e.target.value); updateStormBadge(); });

// ---- live weather from HKO / data.gov.hk -----------------------------------
const HKO_ICON = {
  50:'Sunny',51:'Sunny periods',52:'Sunny intervals',53:'Sunny periods · a few showers',
  54:'Sunny intervals · showers',60:'Cloudy',61:'Overcast',62:'Light rain',63:'Rain',
  64:'Heavy rain',65:'Thunderstorms',70:'Fine',71:'Fine',72:'Fine',73:'Fine',74:'Fine',75:'Fine',
  76:'Mainly cloudy',77:'Mainly fine',80:'Windy',81:'Dry',82:'Humid',83:'Fog',84:'Mist',85:'Haze',
  90:'Hot',91:'Warm',92:'Cool',93:'Cold'
};
const HKO_ICON_ZH = {
  50:'天晴',51:'部分時間有陽光',52:'短暫時間有陽光',53:'天晴，有幾陣驟雨',
  54:'短暫時間有陽光，有驟雨',60:'多雲',61:'密雲',62:'微雨',63:'雨',
  64:'大雨',65:'雷暴',70:'天色良好',71:'天色良好',72:'天色良好',73:'天色良好',74:'天色良好',75:'天色良好',
  76:'大致多雲',77:'天色大致良好',80:'有風',81:'乾燥',82:'潮濕',83:'霧',84:'薄霧',85:'煙霞',
  90:'炎熱',91:'和暖',92:'清涼',93:'寒冷'
};
const wxIcon = code => (isZh() ? HKO_ICON_ZH : HKO_ICON)[code];
let liveMode = false, wxClockT = null, wxRefreshT = null;
const wxStation = arr => (arr || []).find(d => /observatory/i.test(d.place)) || (arr || [])[0];
const windFromForecast = desc => { const m = (desc || '').match(/[^.]*\bwind[s]?\b[^.]*/i); return m ? m[0].trim().replace(/\s+/g, ' ') : ''; };

// ---- live tide prediction (HKO HHOT hourly heights) + HUD waveform ---------
// nearest tide station per source (Cheung Chau for Lantau, Quarry Bay for HK-wide)
const TIDE_STATION = {
  'lantau-hk5m':  ['CCH', 'Cheung Chau'], 'lantau-srtm30': ['CCH', 'Cheung Chau'],
  'hk-landsd-5m': ['QUB', 'Quarry Bay'],  'hk-srtm':       ['QUB', 'Quarry Bay'],
};
// HK-local calendar parts for today ± offsetDays (HKT = UTC+8, no DST)
function hkYMD(offsetDays) {
  const d = new Date(Date.now() + offsetDays * 86400000);
  const [y, m, dd] = d.toLocaleDateString('en-CA', { timeZone: 'Asia/Hong_Kong' }).split('-');
  return { y: +y, m: +m, d: +dd };
}
function hkHourFloat() {
  const [H, M] = new Date().toLocaleTimeString('en-GB', { timeZone: 'Asia/Hong_Kong', hour12: false }).split(':').map(Number);
  return H + M / 60;
}
// vals[i] is the predicted height at clock hour (i+1) measured from yesterday 00:00;
// sample (with linear interpolation) at an absolute window-hour
function tideAt(vals, absHour) {
  const idx = absHour - 1, i0 = Math.floor(idx);
  const cl = i => vals[Math.max(0, Math.min(vals.length - 1, i))];
  const a = cl(i0), b = cl(i0 + 1);
  return (isFinite(a) && isFinite(b)) ? a + (b - a) * (idx - i0) : NaN;
}

async function syncLiveTide() {
  const [st, stName] = TIDE_STATION[document.getElementById('src').value] || ['QUB', 'Quarry Bay'];
  const base = 'https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=HHOT&lang=en&rformat=json&station=' + st;
  const day = off => { const { y, m, d } = hkYMD(off); return fetch(`${base}&year=${y}&month=${m}&day=${d}`).then(r => r.json()).catch(() => null); };
  try {
    const rows = await Promise.all([day(-1), day(0), day(1)]);   // yesterday, today, tomorrow
    const dayVals = j => (j && j.data && j.data[0]) ? j.data[0].slice(2).map(Number) : new Array(24).fill(NaN);
    const vals = [...dayVals(rows[0]), ...dayVals(rows[1]), ...dayVals(rows[2])];   // 72 hourly heights
    const nowHour = 24 + hkHourFloat();                          // today 00:00 sits at window-hour 24
    // min/max over the ±12 h window drives both the graph scale and the level normalisation
    let mn = Infinity, mx = -Infinity;
    for (let x = Math.ceil(nowHour - 12); x <= Math.floor(nowHour + 12); x++) {
      const v = tideAt(vals, x); if (isFinite(v)) { mn = Math.min(mn, v); mx = Math.max(mx, v); }
    }
    const cur = tideAt(vals, nowHour);
    tideSeries = { vals, nowHour, min: mn, max: mx, cur, stationName: stName };
    if (mx > mn && isFinite(cur)) tideLevel = Math.max(0, Math.min(1, (cur - mn) / (mx - mn)));
    // reflect the live level on the (locked) slider
    document.getElementById('tide').value = Math.round(tideLevel * 100);
    document.getElementById('tidev').textContent = Math.round(tideLevel * 100) + '%';
    // HUD readout + trend
    const trend = tideAt(vals, nowHour + 0.5) - cur;
    const arrow = trend > 0.02 ? t('tide.rising') : trend < -0.02 ? t('tide.falling') : t('tide.slack');
    document.getElementById('wx-tide').textContent = isFinite(cur) ? `${t('tide.word')} ${cur.toFixed(2)} m  ${arrow}` : '';
    document.getElementById('wx-tidecap').textContent = `${t('tide.24h')} · ${I18N[locale]['st.' + st] || stName}`;
    drawTideGraph();
  } catch (e) { console.error('tide', e); }
}

// past-and-upcoming tide waveform for the HUD (±12 h around now)
function drawTideGraph() {
  const cv = document.getElementById('wx-tidegraph');
  if (!cv || !tideSeries) return;
  const { vals, nowHour, min, max } = tideSeries;
  const dpr = Math.min(devicePixelRatio || 1, 2), Wc = 224, Hc = 56;
  if (cv.width !== Wc * dpr) { cv.width = Wc * dpr; cv.height = Hc * dpr; }
  const ctx = cv.getContext('2d'); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  cv.style.display = 'block'; ctx.clearRect(0, 0, Wc, Hc);
  const lo = nowHour - 12, hi = nowHour + 12, pad = 6, gTop = 7, gBot = Hc - 13;
  const range = Math.max(0.2, max - min);
  const ymin = min - range * 0.18, ymax = max + range * 0.18;
  const xOf = h => pad + (h - lo) / (hi - lo) * (Wc - pad * 2);
  const yOf = v => gBot - (v - ymin) / (ymax - ymin) * (gBot - gTop);
  // curve
  ctx.beginPath(); let started = false;
  for (let h = lo; h <= hi + 1e-6; h += 0.2) {
    const v = tideAt(vals, h); if (!isFinite(v)) continue;
    const x = xOf(h), y = yOf(v);
    started ? ctx.lineTo(x, y) : (ctx.moveTo(x, y), started = true);
  }
  ctx.lineJoin = 'round'; ctx.strokeStyle = 'rgba(120,200,235,.95)'; ctx.lineWidth = 1.8; ctx.stroke();
  // fill under the curve
  ctx.lineTo(xOf(hi), gBot); ctx.lineTo(xOf(lo), gBot); ctx.closePath();
  ctx.fillStyle = 'rgba(90,170,215,.16)'; ctx.fill();
  // "now" marker + dot
  const nx = xOf(nowHour), nv = tideAt(vals, nowHour);
  ctx.strokeStyle = 'rgba(63,224,176,.85)'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(nx, gTop - 3); ctx.lineTo(nx, gBot); ctx.stroke();
  if (isFinite(nv)) { ctx.fillStyle = '#3fe0b0'; ctx.beginPath(); ctx.arc(nx, yOf(nv), 2.8, 0, 7); ctx.fill(); }
  // axis ticks + high-water marker
  ctx.font = '9px ui-monospace, monospace'; ctx.fillStyle = 'rgba(255,255,255,.5)';
  ctx.textAlign = 'left';   ctx.fillText('−12h', pad, Hc - 3);
  ctx.textAlign = 'center'; ctx.fillText('now', nx, Hc - 3);
  ctx.textAlign = 'right';  ctx.fillText('+12h', Wc - pad, Hc - 3);
  ctx.fillStyle = 'rgba(255,255,255,.4)'; ctx.fillText(max.toFixed(1) + ' m', Wc - pad, gTop + 7);
}

async function syncLiveWeather() {
  const el = id => document.getElementById(id);
  const chk = (id, on) => { const e = el(id); if (e.checked !== on) { e.checked = on; e.dispatchEvent(new Event('change', { bubbles: true })); } };
  try {
    const base = `https://data.weather.gov.hk/weatherAPI/opendata/weather.php?lang=${isZh() ? 'tc' : 'en'}&dataType=`;
    const oBase = 'https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?lang=en&rformat=json&dataType=';
    const [rh, fl, ws, lhl] = await Promise.all([
      fetch(base + 'rhrread').then(r => r.json()),
      fetch(base + 'flw').then(r => r.json()).catch(() => ({})),
      fetch(base + 'warnsum').then(r => r.json()).catch(() => ({})),
      fetch(oBase + 'LHL').then(r => r.json()).catch(() => ({})),   // past-hour lightning counts by region
    ]);
    const tst = wxStation(rh.temperature && rh.temperature.data), h = wxStation(rh.humidity && rh.humidity.data);
    const code = (rh.icon || [])[0];
    let warn = rh.warningMessage || ''; if (Array.isArray(warn)) warn = warn.join(' ');
    let rainMax = 0; for (const r of ((rh.rainfall && rh.rainfall.data) || [])) rainMax = Math.max(rainMax, +r.max || 0);
    el('wx-status').textContent = wxIcon(code) || t('wx.live');
    el('wx-temp').textContent = tst ? `${tst.value}°${tst.unit || 'C'}` : '—';
    el('wx-hum').textContent = h ? `${t('tip.humidity')} ${h.value}%` : '';
    el('wx-wind').textContent = windFromForecast(fl.forecastDesc) || '—';
    el('wx-warn').textContent = warn || '';
    const rainy = [53,54,62,63,64,65].includes(code) || rainMax > 0;
    chk('rain', rainy);
    // real past-hour cloud-to-ground lightning count (data.gov.hk LHL), region-aware
    const lregion = /lantau/.test(el('src').value) ? 'Lantau' : 'Hong Kong territory';
    let cg = 0; for (const row of (lhl.data || [])) if (row[1] === 'Cloud-to-ground' && row[2] === lregion) cg = +row[3] || 0;
    const stormy = cg > 0 || code === 65 || /thunderstorm|雷暴/i.test(warn);
    chk('lightning', stormy);
    setThunderRate(cg > 0 ? Math.min(1, 0.15 + cg / 150) : (stormy ? 0.4 : 0));   // strikes/hr → rate
    el('wx-warn').dataset.ltg = cg;                     // (available for a HUD readout if wanted)
    chk('clouds', rainy || [60,61,76].includes(code));
    chk('fog', [83,84,85].includes(code) || (h && +h.value >= 90));
    chk('waves', true);
    // real tropical-cyclone signal from the HKO warning summary
    const tc = stormFromWarn(ws);
    if (tc.dir) { el('winddir').value = tc.dir; setWindDir(tc.dir); }
    el('storm').value = String(tc.level);
    applyStorm(tc.level);
  } catch (e) { el('wx-status').textContent = t('wx.unavail'); console.error(e); }
}

function tickHKClock() {
  document.getElementById('wx-clock').textContent =
    new Date().toLocaleTimeString('en-GB', { timeZone: 'Asia/Hong_Kong', hour12: false }) + ' HKT';
}

function setLiveMode(on) {
  liveMode = on;
  document.getElementById('wxhud').style.display = on ? '' : 'none';
  applyControlLocks();     // live data owns everything; keeps storm-driven locks coherent too
  const btn = document.getElementById('livebtn');
  btn.textContent = on ? t('live.on') : t('live.sync');
  btn.classList.toggle('on', on);
  clearInterval(wxClockT); clearInterval(wxRefreshT);
  if (on) {
    tickHKClock(); wxClockT = setInterval(tickHKClock, 1000);
    syncLiveWeather(); syncLiveTide();
    wxRefreshT = setInterval(() => { syncLiveWeather(); syncLiveTide(); }, 300000);
  } else {
    // keep whatever live sync produced: adopt the last live tide level as the manual value
    tideManual = tideLevel; tideSeries = null;
    document.getElementById('tide').value = Math.round(tideManual * 100);
    document.getElementById('tidev').textContent = Math.round(tideManual * 100) + '%';
  }
}
document.getElementById('livebtn').addEventListener('click', () => setLiveMode(!liveMode));
document.getElementById('reset').addEventListener('click', frameCamera);
document.getElementById('south').addEventListener('click', southView);
document.getElementById('top').addEventListener('click', topView);

// ---- live per-station weather overlay (HKO automatic weather stations) -----
// Coordinates are baked (data/hko-stations.json, HK1980 grid). Live readings
// come from HKO's regional-weather CSVs, which lack CORS headers — so we route
// them through data.gov.hk's historical-archive, which re-serves with CORS *.
let stationData = null, stationMarkers = [], stationsOn = false, stationT = null, wxEmoji = '⛅';
// When true, only plot stations that report air temperature — HKO's wind/marine-only
// stations (Central Pier, Star Ferry, Waglan…) are hidden. Set false to show them too
// (they fall back to a wind-speed reading). The wind-lead rendering below stays intact.
const STATIONS_TEMP_ONLY = true;
const ARCHIVE = 'https://api.data.gov.hk/v1/historical-archive/get-file?url=';
const REGIONAL = 'https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/';

function ghTime() {   // HKT ~15 min ago as YYYYMMDD-HHMM: the archive only has snapshots
  const m = new Date(Date.now() - 15 * 60000)   // up to the last archived version, not the current minute
    .toLocaleString('en-CA', { timeZone: 'Asia/Hong_Kong', hour12: false })
    .match(/(\d{4})-(\d{2})-(\d{2})[,\s]+(\d{2}):(\d{2})/);
  return m ? `${m[1]}${m[2]}${m[3]}-${m[4]}${m[5]}` : '';
}
const regUrl = file => ARCHIVE + encodeURIComponent(REGIONAL + file) + '&time=' + ghTime();
function parseCsv(text) {
  const out = [];
  for (const line of (text || '').trim().split(/\r?\n/).slice(1)) {
    const c = line.split(','); if (c.length >= 2) out.push(c);
  }
  return out;
}
async function fetchStationReadings() {
  const grab = f => fetch(regUrl(f)).then(r => r.ok ? r.text() : '').catch(() => '');
  const [t, h, w, p] = await Promise.all([
    grab('latest_1min_temperature.csv'), grab('latest_1min_humidity.csv'),
    grab('latest_10min_wind.csv'), grab('latest_1min_pressure.csv'),
  ]);
  const R = {}, at = n => (R[n] || (R[n] = {}));
  for (const r of parseCsv(t)) at(r[1].trim()).temp = r[2];
  for (const r of parseCsv(h)) at(r[1].trim()).rh = r[2];
  for (const r of parseCsv(w)) { const s = at(r[1].trim()); s.wdir = r[2]; s.wspd = r[3]; s.gust = r[4]; }
  for (const r of parseCsv(p)) at(r[1].trim()).pres = r[2];
  return R;
}
function iconEmoji(c) {            // HKO weather-icon code -> emoji (rain/sun status)
  if (c == null) return '⛅';
  if (c === 50) return '☀️';
  if ([51, 52, 77].includes(c)) return '🌤️';
  if ([53, 54, 62, 63].includes(c)) return '🌦️';
  if ([60, 61, 76].includes(c)) return '☁️';
  if (c === 64) return '🌧️';
  if (c === 65) return '⛈️';
  if ([83, 84, 85].includes(c)) return '🌫️';
  if ([70, 71, 72, 73, 74, 75].includes(c)) return '🌙';
  if (c === 80) return '💨';
  if ([90, 91].includes(c)) return '🔥';
  if ([92, 93].includes(c)) return '❄️';
  return '⛅';
}
async function fetchWxEmoji() {   // territory-wide current condition (rhrread is CORS-open)
  try {
    const j = await fetch('https://data.weather.gov.hk/weatherAPI/opendata/weather.php?lang=en&dataType=rhrread').then(r => r.json());
    wxEmoji = iconEmoji((j.icon || [])[0]);
  } catch (_) {}
}
function tempColor(t) {           // 12°C (blue) -> 36°C (red)
  const x = Math.max(0, Math.min(1, (t - 12) / 24));
  return `rgb(${Math.round(70 + x*170)},${Math.round(130 - x*40)},${Math.round(210 - x*170)})`;
}
async function ensureStations() {
  if (stationData) return;
  const ver = new URLSearchParams(location.search).get('v');
  stationData = await fetch('data/hko-stations.json' + (ver ? '?v=' + ver : '')).then(r => r.json());
}
function clearStationMarkers() { stationMarkers.forEach(m => m.el.remove()); stationMarkers = []; }
function buildStationMarkers() {
  clearStationMarkers();
  for (const s of stationData.stations) {
    const el = document.createElement('div'); el.className = 'stn'; el.style.display = 'none';
    const nm = `<span class="nm">${s.zh ? `<span class="zh">${s.zh}</span>` : ''}<span class="en">${s.name}</span></span>`;
    el.innerHTML = `<div class="row"><span class="ic">·</span><span class="t">–</span></div><span class="rh"></span>${nm}<div class="tip"></div>`;
    document.body.appendChild(el);
    stationMarkers.push({ el, E: s.E, N: s.N, name: s.name, zh: s.zh });
  }
}
function applyStationReadings(R) {
  for (const m of stationMarkers) {
    const d = R[m.name] || {}, temp = parseFloat(d.temp);
    const ic = m.el.querySelector('.ic'), tEl = m.el.querySelector('.t'), rhEl = m.el.querySelector('.rh');
    // in temp-only mode, flag stations with no thermometer so updateStations skips them
    m.hidden = STATIONS_TEMP_ONLY && !isFinite(temp);
    if (m.hidden) { m.el.style.display = 'none'; continue; }
    // temperature stations lead with temp; wind-only stations lead with wind
    if (isFinite(temp)) {
      ic.textContent = wxEmoji;
      tEl.textContent = Math.round(temp) + '°'; tEl.style.color = tempColor(temp);
      rhEl.textContent = d.rh ? `💧 ${d.rh}%` : '';
    } else if (isFinite(parseFloat(d.wspd))) {
      const gust = parseFloat(d.gust), dir = d.wdir && d.wdir !== 'N/A' ? d.wdir : '';
      ic.textContent = '💨';
      tEl.textContent = Math.round(parseFloat(d.wspd)); tEl.style.color = '#cfe6ff';
      rhEl.textContent = `${dir}${isFinite(gust) ? ` · ${t('tip.gust')} ${gust}` : ''}`.trim();
    } else {
      ic.textContent = wxEmoji;
      tEl.textContent = '–'; tEl.style.color = 'var(--sub)';
      rhEl.textContent = d.pres ? `${d.pres} hPa` : '';
    }
    const rows = [`<b>${m.zh ? m.zh + ' · ' : ''}${m.name}</b>`];
    if (isFinite(temp)) rows.push(`${temp}°C`);
    if (d.rh) rows.push(`${t('tip.humidity')} ${d.rh}%`);
    if (d.wdir) rows.push(`${t('tip.wind')} ${d.wdir} ${d.wspd || '–'} km/h${d.gust ? ` · ${t('tip.gust')} ${d.gust}` : ''}`);
    if (d.pres) rows.push(`${d.pres} hPa`);
    m.el.querySelector('.tip').innerHTML = rows.join('<br>');
  }
}
async function refreshStations() {
  await ensureStations();
  if (!stationMarkers.length) buildStationMarkers();
  try {
    const [readings] = await Promise.all([fetchStationReadings(), fetchWxEmoji()]);
    applyStationReadings(readings);
  } catch (e) { console.error('stations', e); }
}
async function setStations(on) {
  stationsOn = on;
  clearInterval(stationT);
  if (on) { await refreshStations(); stationT = setInterval(refreshStations, 300000); }
  else clearStationMarkers();
}
document.getElementById('stations').addEventListener('change', e => setStations(e.target.checked));

// project station markers onto the terrain each frame (like the peak labels)
function updateStations() {
  if (!stationsOn || !stationMarkers.length || !curG) return;
  const g = curG;
  for (const m of stationMarkers) {
    if (m.hidden) { m.el.style.display = 'none'; continue; }   // no-temperature station (temp-only mode)
    const col = (m.E - g.bE) / g.aE, row = (m.N - g.bN) / g.aN;
    if (col < 0 || col > W - 1 || row < 0 || row > H - 1) { m.el.style.display = 'none'; continue; }
    const lx = (col - W/2)*cell, ly = sampleE(col, row)*VE, lz = (row - H/2)*cell;
    v.set(lx, ly, lz);
    world.localToWorld(v); v.project(camera);
    if (v.z > 1 || occludedLocal(lx, ly, lz)) { m.el.style.display = 'none'; continue; }
    m.el.style.display = '';
    m.el.style.left = ((v.x*0.5 + 0.5) * innerWidth) + 'px';
    m.el.style.top  = ((-v.y*0.5 + 0.5) * innerHeight) + 'px';
  }
}

// ---- label projection + render loop ---------------------------------------
const v = new THREE.Vector3();

// Terrain occlusion for the DOM overlays (labels + station cards): hide a marker
// when a mountain sits between it and the camera. Instead of raycasting the huge
// mesh, we ray-march the elevation grid (heightfield) in the world group's LOCAL
// frame — cheap (O(steps) height lookups) and correct while the model spins.
const LABEL_OCCLUSION = true;   // set false to always show markers regardless of terrain
const _camLocal = new THREE.Vector3();
function occludedLocal(lx, ly, lz) {
  if (!LABEL_OCCLUSION) return false;
  const cx = _camLocal.x, cy = _camLocal.y, cz = _camLocal.z;
  const STEPS = 22, EPS = cell * 0.35;                 // small tolerance so grazing sightlines don't flicker
  for (let s = 1; s < STEPS; s++) {
    const f = s / STEPS;
    if (f > 0.9) break;                                // ignore the anchor's own surface near the target
    const px = cx + (lx - cx) * f, py = cy + (ly - cy) * f, pz = cz + (lz - cz) * f;
    const col = px / cell + W / 2, row = pz / cell + H / 2;
    if (col < 0 || col > W - 1 || row < 0 || row > H - 1) continue;
    if (py < sampleE(col, row) * VE - EPS) return true;   // terrain rises above the sightline → hidden
  }
  return false;
}
function updateLabels() {
  const show = document.getElementById('labels').checked;
  for (const l of labels) {
    if (!show) { l.div.style.display = 'none'; continue; }
    const lx = (l.col-W/2)*cell, ly = sampleE(l.col, l.row)*VE, lz = (l.row-H/2)*cell;
    v.set(lx, ly, lz);
    world.localToWorld(v); v.project(camera);
    const hide = v.z > 1 || occludedLocal(lx, ly, lz);
    l.div.style.display = hide ? 'none' : '';
    l.div.style.left = ((v.x*0.5+0.5)*innerWidth) + 'px';
    l.div.style.top  = ((-v.y*0.5+0.5)*innerHeight) + 'px';
  }
}
function resize() {
  renderer.setSize(innerWidth, innerHeight);
  camera.aspect = innerWidth/innerHeight; camera.updateProjectionMatrix();
}
addEventListener('resize', resize);

function animate() {
  requestAnimationFrame(animate);
  if (spinDir) world.rotation.y += 0.0016 * spinSpeed * spinDir;
  animateWeather();
  // storm screen shake — the terrain judders under the strongest signals
  const sh = stormLevel >= 10 ? 1 : stormLevel >= 9 ? 0.6 : stormLevel >= 8 ? 0.32 : 0;
  if (sh > 0) { const a = bounds().span * 0.0012 * sh; world.position.set((Math.random()*2-1)*a, (Math.random()*2-1)*a, (Math.random()*2-1)*a); }
  else if (world.position.x || world.position.y || world.position.z) world.position.set(0, 0, 0);
  controls.update();
  updateClip();                 // keep near/far tuned to the current zoom distance
  renderer.render(scene, camera);
  world.updateMatrixWorld();    // camera position in the terrain's local frame, for occlusion tests
  _camLocal.copy(camera.position); world.worldToLocal(_camLocal);
  updateLabels();
  updateStations();
}

// ---- shareable state: sync all controls + camera to the URL ----------------
function serializeState() {
  const g = id => document.getElementById(id);
  const p = new URLSearchParams();
  p.set('s', g('src').value);
  p.set('surf', g('surf').value);
  p.set('bg', g('bg').value);
  p.set('ve', g('ve').value);
  p.set('d', String(meshStep));
  p.set('ml', g('meshlines').checked ? '1' : '0');
  p.set('w', g('water').checked ? '1' : '0');
  p.set('lb', g('labels').checked ? '1' : '0');
  p.set('L', [...document.querySelectorAll('#layers input:checked')].map(i => i.id.slice(4)).join('.'));
  if (wireColor) p.set('mc', wireColor.slice(1));
  p.set('sc', solidColor.slice(1));
  p.set('sp', String(spinDir));
  p.set('ss', String(spinSpeed));
  p.set('fo', weather.fog ? '1' : '0');
  p.set('ra', weather.rain ? '1' : '0');
  p.set('cl', weather.clouds ? '1' : '0');
  p.set('li', weather.lightning ? '1' : '0');
  p.set('wv', weather.waves ? '1' : '0');
  p.set('ti', String(Math.round(tideManual * 100)));
  p.set('tr', String(Math.round(thunderRate * 100)));
  p.set('st', String(stormLevel));
  p.set('wi', String(Math.round(windStrength * 100)));
  p.set('wd', g('winddir').value);
  p.set('lv', liveMode ? '1' : '0');
  p.set('ws', stationsOn ? '1' : '0');
  if (!pathRouted()) p.set('locale', locale);   // in path mode the locale lives in the URL path instead
  const r = n => Math.round(n);
  p.set('cam', [r(camera.position.x), r(camera.position.y), r(camera.position.z),
                r(controls.target.x), r(controls.target.y), r(controls.target.z),
                world.rotation.y.toFixed(3)].join(','));
  return p.toString();
}

let syncTimer = null, restoring = false;
function syncUrl() {
  if (restoring) return;
  clearTimeout(syncTimer);
  syncTimer = setTimeout(() => history.replaceState(null, '', '?' + serializeState()), 200);
}

function applyState(p) {
  restoring = true;
  const g = id => document.getElementById(id);
  const fire = (el, ev) => el.dispatchEvent(new Event(ev));
  const setVal = (id, v, ev = 'change') => { const el = g(id); el.value = v; fire(el, ev); };
  const setChk = (id, on) => { const el = g(id); if (el && el.checked !== on) { el.checked = on; fire(el, 'change'); } };
  if (p.has('bg'))   setVal('bg', p.get('bg'));
  if (p.has('surf')) setVal('surf', p.get('surf'));
  if (p.has('ve'))   setVal('ve', p.get('ve'), 'input');
  if (p.has('d'))    setVal('meshdens', String(13 - parseInt(p.get('d'), 10)), 'change');
  if (p.has('ml'))   setChk('meshlines', p.get('ml') === '1');
  if (p.has('w'))    setChk('water', p.get('w') === '1');
  if (p.has('lb'))   setChk('labels', p.get('lb') === '1');
  if (p.has('L')) {
    const on = new Set(p.get('L').split('.').filter(Boolean));
    for (const inp of document.querySelectorAll('#layers input')) setChk(inp.id, on.has(inp.id.slice(4)));
  }
  if (p.has('mc')) setWireColor('#' + p.get('mc'));
  if (p.has('sc')) setSolidColor('#' + p.get('sc'));
  if (p.has('sp')) setVal('spindir', p.get('sp'));
  if (p.has('ss')) setVal('spinspd', p.get('ss'), 'input');
  if (p.has('fo')) setChk('fog', p.get('fo') === '1');
  if (p.has('ra')) setChk('rain', p.get('ra') === '1');
  if (p.has('cl')) setChk('clouds', p.get('cl') === '1');
  if (p.has('li')) setChk('lightning', p.get('li') === '1');
  if (p.has('wv')) setChk('waves', p.get('wv') === '1');
  if (p.has('ti')) setVal('tide', p.get('ti'), 'input');
  if (p.has('tr')) setVal('thunderrate', p.get('tr'), 'input');
  if (p.has('wd')) setVal('winddir', p.get('wd'));       // direction before signal (badge quadrant)
  if (p.has('st')) setVal('storm', p.get('st'));         // applies the signal preset
  if (p.has('wi')) setVal('wind', p.get('wi'), 'input'); // then any custom wind override
  if (p.has('ws')) setChk('stations', p.get('ws') === '1');
  if (p.has('cam')) {
    const c = p.get('cam').split(',').map(Number);
    if (c.length >= 6 && c.every(isFinite)) {
      camera.position.set(c[0], c[1], c[2]); controls.target.set(c[3], c[4], c[5]);
      if (c.length >= 7) world.rotation.y = c[6];
      controls.update();
    }
  }
  restoring = false;
}

document.getElementById('copylink').addEventListener('click', async e => {
  const btn = e.currentTarget, label = btn.textContent;
  const url = location.origin + location.pathname + '?' + serializeState();
  try { await navigator.clipboard.writeText(url); btn.textContent = 'Copied!'; }
  catch (_) { history.replaceState(null, '', '?' + serializeState()); btn.textContent = 'In address bar'; }
  setTimeout(() => { btn.textContent = label; }, 1400);
});

// ---- locale routing + toggle ----------------------------------------------
function pathLocale() { const seg = location.pathname.split('/')[1]; return LOCALES.includes(seg) ? seg : null; }
function pathRouted() { return pathLocale() !== null; }
function detectLocale() {
  const fromPath = pathLocale(); if (fromPath) return fromPath;                 // /en-hk/ (CF Function route)
  const q = new URLSearchParams(location.search).get('locale'); if (LOCALES.includes(q)) return q;
  try { const s = localStorage.getItem('locale'); if (LOCALES.includes(s)) return s; } catch (_) {}
  for (const p of (navigator.languages || [navigator.language || ''])) {        // browser preference
    const l = p.toLowerCase(); if (LOCALES.includes(l)) return l;
    const m = LOCALES.find(x => x.split('-')[0] === l.split('-')[0]); if (m) return m;
  }
  return DEFAULT_LOCALE;
}
function applyLocale(loc) {
  locale = LOCALES.includes(loc) ? loc : DEFAULT_LOCALE;
  document.documentElement.lang = isZh() ? 'zh-HK' : 'en';
  document.body.dataset.locale = locale;
  for (const el of document.querySelectorAll('[data-i18n]'))       el.textContent = t(el.getAttribute('data-i18n'));
  for (const el of document.querySelectorAll('[data-i18n-title]')) el.title = t(el.getAttribute('data-i18n-title'));
  for (const el of document.querySelectorAll('[data-i18n-html]'))  el.innerHTML = t(el.getAttribute('data-i18n-html'));
  try { localStorage.setItem('locale', locale); } catch (_) {}
  const lb = document.getElementById('langbtn'); if (lb) lb.textContent = isZh() ? 'EN' : '中';
  const md = document.getElementById('meshdensv'); if (md) md.textContent = meshStep === 1 ? t('dens.full') : '÷' + meshStep;
  if (gridW) updateNote();
  updateStormBadge(); applyControlLocks();
  const btn = document.getElementById('livebtn'); if (btn) btn.textContent = liveMode ? t('live.on') : t('live.sync');
  if (liveMode) { syncLiveWeather(); syncLiveTide(); }
  if (stationsOn) refreshStations();
}
function switchLocale(loc) {
  if (!LOCALES.includes(loc) || loc === locale) return;
  try { localStorage.setItem('locale', loc); } catch (_) {}
  if (pathRouted()) {                       // prod: navigate to /<loc>/… (CF Function stamps the cookie)
    const rest = location.pathname.split('/').slice(2).join('/');
    location.href = `/${loc}/${rest}${location.search}${location.hash}`;
  } else {                                  // dev / query mode: switch in place
    const p = new URLSearchParams(location.search); p.set('locale', loc);
    history.replaceState(null, '', location.pathname + '?' + p.toString() + location.hash);
    applyLocale(loc);
  }
}
document.getElementById('langbtn').addEventListener('click', () => switchLocale(isZh() ? 'en-hk' : 'zh-hk'));

resize();
applyBg('dark');
locale = detectLocale();
applyLocale(locale);
const startParams = new URLSearchParams(location.search);
const startSrc = SOURCES[startParams.get('s')] ? startParams.get('s') : 'hk-landsd-5m';
document.getElementById('src').value = startSrc;
loadSource(startSrc).then(() => {
  applyState(startParams);
  controls.addEventListener('change', syncUrl);     // camera orbit/zoom/pan
  const panel = document.getElementById('panel');
  panel.addEventListener('change', syncUrl);         // selects + checkboxes
  panel.addEventListener('input', syncUrl);          // sliders + colour
  syncUrl();
  animate();
  // default to live weather on (unless a shared link explicitly opted out with lv=0)
  if (startParams.has('lv') ? startParams.get('lv') === '1' : true) setLiveMode(true);
}).catch(err => {
  document.getElementById('note').textContent = t('note.loadfail') + ': ' + err.message;
  console.error(err);
});
