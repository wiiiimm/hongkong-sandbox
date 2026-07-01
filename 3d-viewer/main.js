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
let spinDir = 1, spinSpeed = 1;   // horizontal auto-spin (0 = off; 1 = clockwise)
let wireColor = '#2a4c33';        // mesh-line colour; 'auto' button sets null = auto by background
let solidColor = '#262626';       // fill colour for the "Solid colour" surface
let texRot = 0;                   // B50K raster rotation in degrees (manual alignment)

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
  document.getElementById('note').textContent = 'Loading ' + s.label + '…';
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
  setFog();
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
    `${gridW}×${gridH} mesh · ${(gridW*gridH/1e3).toFixed(0)}k verts · peak ${Math.round(zmax)} m`;
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

  matShaded = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.95, metalness: 0 });
  matTint   = new THREE.MeshBasicMaterial({ vertexColors: true });                 // flat hypsometric
  matMatte  = new THREE.MeshStandardMaterial({ color: 0x8a8f86, roughness: 1, metalness: 0 });
  matSolid  = new THREE.MeshBasicMaterial({ color: solidColor });                  // flat solid fill
  matTopo   = new THREE.MeshBasicMaterial({});   // unlit: show the map flat, no hillshade darkening

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
    lab.innerHTML = `<input type="checkbox" id="${id}" ${on?'checked':''}/> ${style.label}`;
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

function setFog() {
  const b = bounds();
  scene.fog = weather.fog ? new THREE.Fog(BG[bgMode], b.span*0.35, b.span*1.5) : null;
}

function animateWeather() {
  const b = bounds();
  if (rainPts && rainPts.visible) {
    const p = rainPts.geometry.attributes.position.array, top = rainPts.userData.top, spd = b.span*0.012;
    for (let i = 1; i < p.length; i += 3) { p[i] -= spd; if (p[i] < 0) p[i] = top; }
    rainPts.geometry.attributes.position.needsUpdate = true;
  }
  if (cloudGrp && cloudGrp.visible) {
    const lim = b.halfX * 1.3;
    for (const s of cloudGrp.children) { s.position.x += b.span*0.0006; if (s.position.x > lim) s.position.x = -lim; }
  }
  // tide = slow water level (0..1, from live prediction or the manual slider);
  // waves = a small ripple layered on top of that level.
  if (sea) {
    const tideY  = SEA_Y + tideLevel * b.span * 0.0012;
    // ripple laps UP from the tide line only (0..amp) so it never drains below it, even at low tide
    const ripple = weather.waves ? (Math.sin(wavePhase += 0.03) * 0.5 + 0.5) * b.span * 0.00004 : 0;
    sea.position.y = tideY + ripple;
  }
  if (weather.lightning) {
    if (flash > 0) { flash -= 0.07; hemi.intensity = (bgMode === 'paper' ? 1.9 : 1.4) + flash * 5; }
    else if (Math.random() < 0.007) flash = 1;
  }
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

function applyStyle(style) {
  surfStyle = style;
  const mats = { shaded: matShaded, tint: matTint, matte: matMatte, solid: matSolid, topo: matTopo };
  // 'none' = no filled surface; every other style fills the terrain.
  terrain.visible = (style !== 'none');
  if (terrain.visible) terrain.material = mats[style] || matShaded;
  document.getElementById('solidrow').style.display = (style === 'solid') ? '' : 'none';
  document.getElementById('toporow').style.display = (style === 'topo') ? '' : 'none';
  // mesh lines are an independent overlay in ALL styles (incl. none)
  wireOverlay.visible = document.getElementById('meshlines').checked;
  wireLook();
}
function applyBg(mode) {
  bgMode = mode;
  renderer.setClearColor(BG[mode], 1);
  const onPaper = mode === 'paper';
  hemi.intensity = onPaper ? 1.9 : 1.4;
  sun.intensity  = onPaper ? 2.4 : 2.0;
  if (wireOverlay) wireLook();
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
    document.getElementById('note').textContent = 'Load failed: ' + err.message; console.error(err);
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
meshdens.addEventListener('input', () => { const s = densStep(); meshdensv.textContent = s === 1 ? 'full' : '÷' + s; });
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

// ---- live weather from HKO / data.gov.hk -----------------------------------
const HKO_ICON = {
  50:'Sunny',51:'Sunny periods',52:'Sunny intervals',53:'Sunny periods · a few showers',
  54:'Sunny intervals · showers',60:'Cloudy',61:'Overcast',62:'Light rain',63:'Rain',
  64:'Heavy rain',65:'Thunderstorms',70:'Fine',71:'Fine',72:'Fine',73:'Fine',74:'Fine',75:'Fine',
  76:'Mainly cloudy',77:'Mainly fine',80:'Windy',81:'Dry',82:'Humid',83:'Fog',84:'Mist',85:'Haze',
  90:'Hot',91:'Warm',92:'Cool',93:'Cold'
};
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
    const arrow = trend > 0.02 ? '↑ rising' : trend < -0.02 ? '↓ falling' : '→ slack';
    document.getElementById('wx-tide').textContent = isFinite(cur) ? `tide ${cur.toFixed(2)} m  ${arrow}` : '';
    document.getElementById('wx-tidecap').textContent = `24 h tide · ${stName}`;
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
    const base = 'https://data.weather.gov.hk/weatherAPI/opendata/weather.php?lang=en&dataType=';
    const [rh, fl] = await Promise.all([
      fetch(base + 'rhrread').then(r => r.json()),
      fetch(base + 'flw').then(r => r.json()).catch(() => ({})),
    ]);
    const t = wxStation(rh.temperature && rh.temperature.data), h = wxStation(rh.humidity && rh.humidity.data);
    const code = (rh.icon || [])[0];
    let warn = rh.warningMessage || ''; if (Array.isArray(warn)) warn = warn.join(' ');
    let rainMax = 0; for (const r of ((rh.rainfall && rh.rainfall.data) || [])) rainMax = Math.max(rainMax, +r.max || 0);
    el('wx-status').textContent = HKO_ICON[code] || 'Live';
    el('wx-temp').textContent = t ? `${t.value}°${t.unit || 'C'}` : '—';
    el('wx-hum').textContent = h ? `humidity ${h.value}%` : '';
    el('wx-wind').textContent = windFromForecast(fl.forecastDesc) || '—';
    el('wx-warn').textContent = warn || '';
    const rainy = [53,54,62,63,64,65].includes(code) || rainMax > 0;
    chk('rain', rainy);
    chk('lightning', code === 65 || /thunderstorm/i.test(warn));
    chk('clouds', rainy || [60,61,76].includes(code));
    chk('fog', [83,84,85].includes(code) || (h && +h.value >= 90));
    chk('waves', true);
  } catch (e) { el('wx-status').textContent = 'live weather unavailable'; console.error(e); }
}

function tickHKClock() {
  document.getElementById('wx-clock').textContent =
    new Date().toLocaleTimeString('en-GB', { timeZone: 'Asia/Hong_Kong', hour12: false }) + ' HKT';
}

function setLiveMode(on) {
  liveMode = on;
  document.getElementById('wxhud').style.display = on ? '' : 'none';
  document.getElementById('wxlock').style.display = on ? 'block' : 'none';
  // live data owns the weather + tide controls, so lock them while it's on
  ['rain', 'clouds', 'fog', 'lightning', 'waves', 'tide'].forEach(id => { const e = document.getElementById(id); if (e) e.disabled = on; });
  const btn = document.getElementById('livebtn');
  btn.textContent = on ? '⛅ Live weather · ON' : '⛅ Sync live weather';
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

// ---- label projection + render loop ---------------------------------------
const v = new THREE.Vector3();
function updateLabels() {
  const show = document.getElementById('labels').checked;
  for (const l of labels) {
    if (!show) { l.div.style.display = 'none'; continue; }
    v.set((l.col-W/2)*cell, sampleE(l.col, l.row)*VE, (l.row-H/2)*cell);
    world.localToWorld(v); v.project(camera);
    const behind = v.z > 1;
    l.div.style.display = behind ? 'none' : '';
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
  controls.update();
  updateClip();                 // keep near/far tuned to the current zoom distance
  renderer.render(scene, camera);
  updateLabels();
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

resize();
applyBg('dark');
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
}).catch(err => {
  document.getElementById('note').textContent = 'Load failed: ' + err.message;
  console.error(err);
});
